#!/usr/bin/env python3
"""Snap an AI-generated near-pixel-art image to a clean pixel grid.

Faithful Python port of Hugo Duprez's spritefusion-pixel-snapper algorithm
(MIT, Rust+WASM, https://github.com/Hugo-Dz/spritefusion-pixel-snapper).

The crucial detail is the ORDER:
  1. K-MEANS QUANTIZE the FULL-RESOLUTION input first (default k=16, k-means++
     init, max 15 iters, squared-Euclidean RGB, alpha=0 pixels excluded from
     training and passed through unchanged).
  2. Every opaque pixel is replaced with its nearest centroid → an
     intermediate full-res image with only k distinct RGB values.
  3. Detect native pixel block size (auto or `--pixel-size`).
  4. For each NxN block, take the MODE (most common exact RGBA) of the
     quantized pixels.
  5. Save at native logical resolution.

Why this order matters: in a smooth gradient on raw RGB, every pixel has a
UNIQUE color, so block-mode would pick a random pixel — producing noisy
gradients. After k-means quantization, the gradient has only 2-3 distinct
colors per region, so block-mode locks onto a clear supermajority. This is
what makes Sprite Fusion's output cleanly banded vs. speckled.

Why k-means (not FASTOCTREE): k-means concentrates centroids in dense
regions of the color histogram. AI-generated pixel art has soft fringe
noise around each "real" rendered color — k-means collapses that fringe
into the real centroid. FASTOCTREE bins by spatial cube subdivision and
tends to preserve fringe noise as distinct palette entries.

Output is at NATIVE LOGICAL RESOLUTION — every pixel in the output file IS
one logical pixel. Use `upscale.py` for NEAREST-upscaling to display sizes.

Usage:
  python snap_pixels.py --input concept.png --output snapped.png --colors 16
  python snap_pixels.py --input concept.png --output snapped.png --pixel-size 6
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image


# ---------------------------------------------------------------------------
# Grid detection (faithful port of Hugo's compute_profiles + estimate_step_size
# + walk + stabilize_both_axes)
# ---------------------------------------------------------------------------


def compute_gradient_profile(arr_rgba: np.ndarray, axis: int) -> np.ndarray:
    """1D gradient profile along the given axis. Hugo's compute_profiles.

    axis=1 → vertical cuts (gradient along X, summed over Y)
    axis=0 → horizontal cuts (gradient along Y, summed over X)

    Kernel is [-1, 0, 1] on grayscale; transparent pixels contribute 0.
    """
    rgb = arr_rgba[..., :3].astype(np.float32)
    alpha = arr_rgba[..., 3].astype(np.float32) / 255.0
    gray = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]) * alpha

    if axis == 1:
        grad = np.zeros_like(gray)
        grad[:, 1:-1] = np.abs(gray[:, 2:] - gray[:, :-2])
        profile = grad.sum(axis=0)
    else:
        grad = np.zeros_like(gray)
        grad[1:-1, :] = np.abs(gray[2:, :] - gray[:-2, :])
        profile = grad.sum(axis=1)
    return profile


def estimate_step_size(
    profile: np.ndarray, peak_distance_filter: int = 4
) -> int | None:
    """Estimate the native pixel step size from a gradient profile.

    Hugo's estimate_step_size:
      - threshold = max(profile) * 0.2
      - find local maxima above threshold
      - filter peaks closer than peak_distance_filter - 1 = 3 apart
      - return median of consecutive-peak differences
    """
    n = len(profile)
    if n < 3 or profile.max() <= 0:
        return None
    threshold = float(profile.max()) * 0.2

    # Local maxima above threshold
    raw_peaks = []
    for i in range(1, n - 1):
        v = profile[i]
        if v > threshold and v > profile[i - 1] and v > profile[i + 1]:
            raw_peaks.append(i)

    # Filter peaks closer than peak_distance_filter - 1 apart (keep the taller)
    filtered: list[int] = []
    for p in raw_peaks:
        if filtered and p - filtered[-1] < peak_distance_filter - 1:
            if profile[p] > profile[filtered[-1]]:
                filtered[-1] = p
        else:
            filtered.append(p)

    if len(filtered) < 2:
        return None

    diffs = np.diff(np.array(filtered))
    return int(np.median(diffs))


def walk(profile: np.ndarray, step_size: int, window_ratio: float = 0.35) -> list[int]:
    """Walk along the profile, snapping each expected cut to its local peak.

    Hugo's walk: starts at 0, then for each expected cut at position k*step,
    looks for the local-maximum within ±step*window_ratio and uses that as
    the actual cut position. Cuts can be non-uniform (variable cell sizes).
    """
    n = len(profile)
    if step_size <= 1 or n <= step_size:
        return [0, n]

    half_window = max(1, int(round(step_size * window_ratio)))
    cuts: list[int] = [0]
    expected = step_size

    while expected < n:
        lo = max(cuts[-1] + 1, expected - half_window)
        hi = min(n - 1, expected + half_window)
        if hi <= lo:
            # No window; just place a uniform cut and move on
            cuts.append(int(min(expected, n - 1)))
            expected = cuts[-1] + step_size
            continue
        # Argmax of the profile within [lo, hi]
        window = profile[lo : hi + 1]
        peak = lo + int(np.argmax(window))
        # If the peak is the same as the last cut (degenerate), force step
        if peak <= cuts[-1]:
            peak = min(cuts[-1] + step_size, n - 1)
        cuts.append(peak)
        expected = peak + step_size

    if cuts[-1] != n:
        cuts.append(n)
    return cuts


def stabilize_axis(
    cuts: list[int], step_size: int, n: int, min_gap_ratio: float = 0.5
) -> list[int]:
    """Stabilize cuts: drop cuts that are too close to their neighbor.

    This is a simpler version of Hugo's cross-axis stabilize. It just removes
    cuts that would produce cells smaller than half the step size — those are
    detection artifacts.
    """
    if len(cuts) < 3:
        return cuts
    min_gap = max(1, int(round(step_size * min_gap_ratio)))
    stabilized = [cuts[0]]
    for c in cuts[1:-1]:
        if c - stabilized[-1] >= min_gap:
            stabilized.append(c)
    if cuts[-1] - stabilized[-1] >= min_gap:
        stabilized.append(cuts[-1])
    else:
        stabilized[-1] = cuts[-1]
    return stabilized


def detect_grid(
    arr_rgba: np.ndarray,
    pixel_size_override: int | None = None,
) -> tuple[list[int], list[int], int]:
    """Detect grid cuts (Hugo's full algorithm).

    Returns (col_cuts, row_cuts, effective_step_size). col_cuts defines the
    vertical cell boundaries (X positions); row_cuts the horizontal ones.
    """
    h, w = arr_rgba.shape[:2]

    if pixel_size_override is not None:
        step_x = step_y = pixel_size_override
    else:
        prof_x = compute_gradient_profile(arr_rgba, axis=1)
        prof_y = compute_gradient_profile(arr_rgba, axis=0)
        sx = estimate_step_size(prof_x)
        sy = estimate_step_size(prof_y)
        # Fallback if detection failed
        if sx is None and sy is None:
            fallback = max(2, min(h, w) // 64)
            step_x = step_y = fallback
        elif sx is None:
            step_x = step_y = sy
        elif sy is None:
            step_x = step_y = sx
        else:
            # Hugo's resolve_step_sizes: average unless ratio > 1.8, then pick smaller
            ratio = max(sx, sy) / max(1, min(sx, sy))
            if ratio > 1.8:
                step_x = step_y = min(sx, sy)
            else:
                avg = int(round((sx + sy) / 2))
                step_x = step_y = max(2, avg)

    # Profiles for the walk (recompute even with override, so cuts align to peaks)
    prof_x = compute_gradient_profile(arr_rgba, axis=1)
    prof_y = compute_gradient_profile(arr_rgba, axis=0)

    col_cuts = walk(prof_x, step_x)
    row_cuts = walk(prof_y, step_y)

    col_cuts = stabilize_axis(col_cuts, step_x, w)
    row_cuts = stabilize_axis(row_cuts, step_y, h)

    return col_cuts, row_cuts, step_x


# ---------------------------------------------------------------------------
# K-means++ quantization (faithful port of Hugo's quantize_image)
# ---------------------------------------------------------------------------


def kmeans_plus_plus(
    pixels: np.ndarray,
    k: int,
    max_iter: int = 15,
    tol: float = 0.01,
    seed: int = 42,
    chunk_size: int = 200_000,
) -> tuple[np.ndarray, np.ndarray]:
    """K-means++ initialization + Lloyd's iterations on RGB pixels.

    Matches Hugo's algorithm:
      - K-means++ init with weighted-by-squared-distance sampling.
      - Lloyd iterations: max 15, early exit when max centroid movement
        (squared) drops below 0.01.
      - Squared-Euclidean RGB distance (no perceptual weighting).
      - Deterministic seed (42 by default).

    Args:
        pixels: (N, 3) float32 array of RGB values in 0-255 range.
        k: number of clusters.
        max_iter: max Lloyd iterations.
        tol: convergence threshold on max squared centroid movement.
        seed: RNG seed for reproducibility.
        chunk_size: distance-computation chunk size to bound memory.

    Returns:
        (centroids (k, 3) float32, labels (N,) int32)
    """
    pixels = np.ascontiguousarray(pixels, dtype=np.float32)
    n = pixels.shape[0]
    rng = np.random.default_rng(seed)

    if n == 0:
        return np.zeros((k, 3), dtype=np.float32), np.zeros((0,), dtype=np.int32)
    if n <= k:
        centroids = np.zeros((k, 3), dtype=np.float32)
        centroids[:n] = pixels
        # Fill unused centroids with the last pixel (won't get assignments)
        if n < k and n > 0:
            centroids[n:] = pixels[-1]
        return centroids, np.arange(n, dtype=np.int32)

    # ---- k-means++ init ----
    centroids = np.empty((k, 3), dtype=np.float32)
    idx0 = int(rng.integers(n))
    centroids[0] = pixels[idx0]

    # Running min squared-distance to any existing centroid
    min_d_sq = np.full(n, np.inf, dtype=np.float32)

    for ci in range(1, k):
        # Update min_d_sq with the just-added centroid (only)
        latest = centroids[ci - 1]
        for start in range(0, n, chunk_size):
            end = min(start + chunk_size, n)
            d = pixels[start:end] - latest
            d_sq = (d * d).sum(axis=-1)
            np.minimum(min_d_sq[start:end], d_sq, out=min_d_sq[start:end])

        total = float(min_d_sq.sum())
        if total <= 0.0:
            idx = int(rng.integers(n))
        else:
            r = float(rng.random()) * total
            cum = np.cumsum(min_d_sq)
            idx = int(np.searchsorted(cum, r))
            if idx >= n:
                idx = n - 1
        centroids[ci] = pixels[idx]

    # ---- Lloyd iterations ----
    labels = np.empty(n, dtype=np.int32)

    def assign_labels(c: np.ndarray) -> None:
        # |x - c|^2 = |x|^2 + |c|^2 - 2 x·c. Use chunked dot products.
        c_sq = (c * c).sum(axis=-1)  # (k,)
        for start in range(0, n, chunk_size):
            end = min(start + chunk_size, n)
            chunk = pixels[start:end]
            # (chunk, k) = -2 * chunk @ c.T + c_sq (broadcast)
            # We can skip x.x because it's constant per row → argmin is the same.
            dots = chunk @ c.T  # (chunk, k)
            dist_proxy = c_sq[None, :] - 2.0 * dots  # (chunk, k), shifted by |x|^2
            labels[start:end] = np.argmin(dist_proxy, axis=1)

    for _ in range(max_iter):
        assign_labels(centroids)

        new_centroids = centroids.copy()
        for ci in range(k):
            mask = labels == ci
            if mask.any():
                new_centroids[ci] = pixels[mask].mean(axis=0)
            # else: keep old centroid (empty cluster)

        diff = new_centroids - centroids
        max_move_sq = float((diff * diff).sum(axis=-1).max())
        centroids = new_centroids
        if max_move_sq < tol:
            break

    # Final assignment (in case loop ended without re-labeling at last centroids)
    assign_labels(centroids)
    return centroids, labels


# ---------------------------------------------------------------------------
# Main snapper
# ---------------------------------------------------------------------------


def snap_pixels(
    input_path: Path,
    output_path: Path,
    colors: int = 16,
    pixel_size: int | None = None,
    alpha_threshold: int = 128,
    kmeans_seed: int = 42,
    kmeans_iters: int = 15,
    kmeans_tol: float = 0.01,
) -> tuple[Image.Image, int]:
    """Snap a transparent-bg concept to a clean pixel grid (Sprite Fusion).

    Faithful port of Hugo Duprez's spritefusion-pixel-snapper:
      1. K-means++ quantize the full-res opaque pixels (k = `colors`).
      2. Replace each opaque pixel with its nearest centroid.
      3. Compute X/Y gradient profiles on the quantized image.
      4. Estimate step size per axis (median of peak-to-peak distances).
      5. Walk each profile to find non-uniform cuts at local gradient peaks
         (this aligns each cell with one logical pixel of the original
         drawing — critical for thin features like outlines).
      6. Resample: for each cell defined by (col_cuts[i:i+1], row_cuts[j:j+1])
         take the MODE of quantized RGBA pixels.

    Why grid-aligned cuts matter: uniform NxN blocks crossing logical-pixel
    boundaries mix outline pixels with body pixels — the body wins MODE
    because it's the majority, and the outline disappears. Hugo's walk
    places cuts at the actual color transitions so each cell contains one
    logical pixel of the rendered drawing, preserving thin outlines cleanly.

    Output is at NATIVE LOGICAL RESOLUTION (small, e.g. 80-200px per side).
    Use `upscale.py` to NEAREST-upscale to a display size.
    """
    img = Image.open(input_path).convert("RGBA")
    orig_w, orig_h = img.size

    arr = np.array(img)  # (H, W, 4) uint8
    alpha = arr[..., 3]
    fg_mask = alpha >= alpha_threshold

    # 1. K-means quantize the OPAQUE pixels.
    rgb_quantized = arr[..., :3].copy()
    if fg_mask.any():
        opaque_pixels = arr[fg_mask, :3].astype(np.float32)
        centroids, labels = kmeans_plus_plus(
            opaque_pixels,
            k=colors,
            max_iter=kmeans_iters,
            tol=kmeans_tol,
            seed=kmeans_seed,
        )
        centroid_rgb = np.clip(np.round(centroids), 0, 255).astype(np.uint8)
        rgb_quantized[fg_mask] = centroid_rgb[labels]

    # Hard-threshold alpha early. The grid detection and the per-cell mode
    # both operate on this hard-alpha image so transparent pixels form a
    # single distinct value in MODE counting.
    alpha_hard = np.where(fg_mask, 255, 0).astype(np.uint8)
    # Zero out RGB of transparent pixels so the packed-RGBA value collapses
    # to a single sentinel (0) for all transparent pixels.
    rgb_quantized = rgb_quantized.copy()
    rgb_quantized[~fg_mask] = 0
    quantized_rgba = np.dstack([rgb_quantized, alpha_hard])

    # 2. Detect grid (Hugo's compute_profiles + estimate_step_size + walk
    # + stabilize). Cuts are at local gradient peaks → cells align with
    # actual logical-pixel boundaries.
    col_cuts, row_cuts, used_step = detect_grid(quantized_rgba, pixel_size)

    sh = len(row_cuts) - 1
    sw = len(col_cuts) - 1

    # 3. Resample: per cell, take the MODE of quantized RGBA pixels.
    packed = (
        quantized_rgba[..., 0].astype(np.uint32)
        | (quantized_rgba[..., 1].astype(np.uint32) << 8)
        | (quantized_rgba[..., 2].astype(np.uint32) << 16)
        | (quantized_rgba[..., 3].astype(np.uint32) << 24)
    )

    output_rgba = np.zeros((sh, sw, 4), dtype=np.uint8)
    for y in range(sh):
        y0, y1 = row_cuts[y], row_cuts[y + 1]
        if y1 <= y0:
            continue
        for x in range(sw):
            x0, x1 = col_cuts[x], col_cuts[x + 1]
            if x1 <= x0:
                continue
            cell = packed[y0:y1, x0:x1].ravel()
            unique_vals, counts = np.unique(cell, return_counts=True)
            mode_packed = int(unique_vals[counts.argmax()])
            if mode_packed == 0:
                # Transparent wins — leave (0, 0, 0, 0)
                continue
            output_rgba[y, x, 0] = mode_packed & 0xFF
            output_rgba[y, x, 1] = (mode_packed >> 8) & 0xFF
            output_rgba[y, x, 2] = (mode_packed >> 16) & 0xFF
            output_rgba[y, x, 3] = (mode_packed >> 24) & 0xFF

    result = Image.fromarray(output_rgba, "RGBA")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path)
    return result, used_step


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", "-i", type=Path, required=True, help="Input PNG path (transparent-bg expected).")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Output PNG path (small native transparent).")
    parser.add_argument(
        "--colors",
        type=int,
        default=16,
        help="K-means palette size (default 16, matching Hugo's default). "
        "K-means quantization runs on the FULL-RESOLUTION input before the "
        "per-block mode step. Lower for tighter classic palettes (NES 8-16); "
        "raise to 24-32 for richer modern palettes.",
    )
    parser.add_argument(
        "--pixel-size",
        type=int,
        default=None,
        help="Override the auto-detected native pixel block size. "
        "If omitted, the snapper detects from the (quantized) input.",
    )
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        default=128,
        help="A pixel is treated as opaque if alpha >= threshold (default 128).",
    )
    parser.add_argument(
        "--kmeans-seed",
        type=int,
        default=42,
        help="RNG seed for k-means++ initialization (default 42, deterministic).",
    )
    parser.add_argument(
        "--kmeans-iters",
        type=int,
        default=15,
        help="Max Lloyd iterations for k-means (default 15).",
    )
    parser.add_argument(
        "--kmeans-tol",
        type=float,
        default=0.01,
        help="K-means convergence tolerance on max squared centroid movement "
        "(default 0.01).",
    )
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"input not found: {args.input}")

    result, used_pixel_size = snap_pixels(
        args.input,
        args.output,
        colors=args.colors,
        pixel_size=args.pixel_size,
        alpha_threshold=args.alpha_threshold,
        kmeans_seed=args.kmeans_seed,
        kmeans_iters=args.kmeans_iters,
        kmeans_tol=args.kmeans_tol,
    )

    print(f"snapped {args.input} -> {args.output}")
    if args.pixel_size is None:
        print(f"  detected native pixel size: {used_pixel_size}px (from quantized image)")
    else:
        print(f"  used pixel size: {used_pixel_size}px (manual override)")
    print(f"  k-means palette: k={args.colors}, seed={args.kmeans_seed}, max_iter={args.kmeans_iters}")
    print(f"  alpha threshold: {args.alpha_threshold}")
    print(f"  output size: {result.size}  (Sprite Fusion native logical resolution)")


if __name__ == "__main__":
    main()
