#!/usr/bin/env python3
"""Snap an AI-generated near-pixel-art image to a clean pixel grid.

Faithful Python port of Hugo Duprez's spritefusion-pixel-snapper algorithm
(MIT, Rust+WASM, https://github.com/Hugo-Dz/spritefusion-pixel-snapper).

Algorithm (in order):
  1. K-MEANS++ QUANTIZE the FULL-RESOLUTION input (default k=16, max 15
     iters, squared-Euclidean RGB). Pixels with alpha > 0 are included in
     training; alpha=0 pixels are passed through unchanged.
  2. Every opaque pixel is replaced with its nearest centroid → an
     intermediate full-res image with only k distinct RGB values.
  3. Compute 1D gradient profiles over the quantized image (full gray when
     alpha > 0; 0 when alpha == 0 — matches Hugo's compute_profiles).
  4. Estimate native pixel step size per axis from the median of peak-to-
     peak distances in each profile. Step size is a FLOAT (not int) so the
     walker stays locked on the true grid across the full sprite.
  5. WALK each profile to find non-uniform cuts at local gradient peaks
     within a ±step*0.35 window. Only snap to a peak if its value exceeds
     0.5 × mean(profile); otherwise place a uniform cut. This prevents
     noise-snap in smooth regions.
  6. If a walker yielded too few cuts (weak profile), fall back to uniform
     cuts at the resolved step size.
  7. For each cell defined by the cuts, take the MODE of (R,G,B,A) tuples
     of the quantized pixels — ties broken by smallest packed value.

Why this matters for OUTLINE QUALITY:

- K-means trained on alpha-edge pixels (alpha 1-127) sees enough dark
  outline samples to allocate a dedicated near-black centroid. Excluding
  those pixels (the old default of alpha_threshold=128) starved the dark
  cluster and pulled outlines into a "dark brown" centroid.
- Float step + float walker arithmetic keeps cell boundaries aligned with
  the true logical-pixel grid. Int-truncating the step compounds a 0.5px
  error over each step and smears 1-pixel outlines across two cells, where
  the body color wins mode and the outline disappears.
- Walker strength threshold (0.5 × mean) keeps the walker on the true grid
  in smooth regions instead of being deflected by sub-mean noise peaks.

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

    Kernel is [-1, 0, 1] on grayscale. Per Hugo: pixels with alpha=0 contribute
    gray=0; pixels with alpha>0 contribute FULL gray (no alpha attenuation).
    This matters along soft-matte silhouette edges — alpha-attenuated gray
    would weaken the silhouette-edge peak and let it drift away from logical
    pixel boundaries.
    """
    rgb = arr_rgba[..., :3].astype(np.float64)
    alpha = arr_rgba[..., 3]
    gray = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    gray[alpha == 0] = 0.0

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
    profile: np.ndarray,
    peak_threshold_multiplier: float = 0.2,
    peak_distance_filter: int = 4,
) -> float | None:
    """Estimate the native pixel step size from a gradient profile.

    Faithful port of Hugo's estimate_step_size:
      - threshold = max(profile) * peak_threshold_multiplier (default 0.2)
      - find local maxima above threshold
      - filter peaks closer than peak_distance_filter - 1 = 3 apart
      - return median of consecutive-peak differences as FLOAT

    Returning a float (not int) matters: Hugo carries f64 step sizes through
    `walk` so the walker stays locked on the true logical-pixel grid across
    long sweeps. Integer-truncating drifts the walker off the grid over a
    few-hundred-pixel character, smearing thin features (especially 1-pixel
    outlines) across cell boundaries.
    """
    n = len(profile)
    if n < 3 or profile.max() <= 0:
        return None
    threshold = float(profile.max()) * peak_threshold_multiplier

    # Local maxima above threshold
    raw_peaks: list[int] = []
    for i in range(1, n - 1):
        v = profile[i]
        if v > threshold and v > profile[i - 1] and v > profile[i + 1]:
            raw_peaks.append(i)

    # Filter peaks closer than peak_distance_filter - 1 apart.
    # Hugo's filter keeps the FIRST of each cluster (not the tallest) — match
    # exactly so output is deterministic and matches the upstream reference.
    filtered: list[int] = []
    for p in raw_peaks:
        if not filtered or p - filtered[-1] > (peak_distance_filter - 1):
            filtered.append(p)

    if len(filtered) < 2:
        return None

    diffs = np.diff(np.array(filtered, dtype=np.float64))
    return float(np.median(diffs))


def walk(
    profile: np.ndarray,
    step_size: float,
    window_ratio: float = 0.35,
    min_search_window: float = 2.0,
    strength_threshold: float = 0.5,
) -> list[int]:
    """Walk along the profile, snapping each expected cut to its local peak.

    Faithful port of Hugo's walk:
      - Maintain `current_pos` as float, advance by `target = current_pos + step`.
      - Search window is `max(step * window_ratio, min_search_window)`.
      - Within the window, find the argmax. If that peak's value is above
        `mean(profile) * strength_threshold`, snap to it; otherwise place a
        uniform cut at `target` (don't be deflected by sub-mean noise peaks
        in smooth regions).

    The float walk + strength threshold combo is what keeps the cuts aligned
    with logical pixel boundaries across the full sprite without getting
    pulled off-grid by smooth-region noise. Cells stay aligned with actual
    color transitions, so 1-pixel outlines fill exactly one cell instead of
    smearing across two.
    """
    n = len(profile)
    if step_size <= 1 or n <= step_size:
        return [0, n]

    search_window = max(step_size * window_ratio, min_search_window)
    mean_val = float(profile.sum() / max(1, len(profile)))
    threshold = mean_val * strength_threshold

    cuts: list[int] = [0]
    current_pos = 0.0

    while current_pos < n:
        target = current_pos + step_size
        if target >= n:
            cuts.append(n)
            break

        lo = max(int(target - search_window), int(current_pos + 1.0))
        hi = min(int(target + search_window), n)
        if hi <= lo:
            current_pos = target
            continue

        window = profile[lo:hi]
        rel = int(np.argmax(window))
        peak_idx = lo + rel
        peak_val = float(window[rel])

        if peak_val > threshold:
            cuts.append(peak_idx)
            current_pos = float(peak_idx)
        else:
            uniform_cut = int(target)
            if uniform_cut <= cuts[-1]:
                uniform_cut = cuts[-1] + 1
            cuts.append(min(uniform_cut, n))
            current_pos = target

    if cuts[-1] != n:
        cuts.append(n)
    return cuts


def stabilize_axis(
    cuts: list[int], step_size: float, n: int, min_gap_ratio: float = 0.5
) -> list[int]:
    """Stabilize cuts: drop cuts that are too close to their neighbor.

    Simplified version of Hugo's cross-axis stabilize. Removes cuts that
    would produce cells smaller than half the step size — those are
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


def snap_uniform_cuts(
    profile: np.ndarray,
    limit: int,
    target_step: float,
    window_ratio: float = 0.35,
    min_search_window: float = 2.0,
    strength_threshold: float = 0.5,
    min_required: int = 4,
) -> list[int]:
    """Fallback when the walker yields too few cuts.

    Computes uniformly-spaced target positions and snaps each toward its
    local peak (same strength gate as `walk`). Used when a profile is too
    weak / noisy for the walker to find enough cuts naturally. Faithful
    port of Hugo's snap_uniform_cuts.
    """
    if limit <= 1:
        return [0, max(limit, 1)]

    if target_step is None or not np.isfinite(target_step) or target_step <= 0:
        desired_cells = 1
    else:
        desired_cells = max(1, int(round(limit / target_step)))
    desired_cells = max(desired_cells, max(min_required - 1, 1))
    desired_cells = min(desired_cells, limit)

    cell_width = limit / desired_cells
    search_window = max(cell_width * window_ratio, min_search_window)
    mean_val = float(profile.sum() / max(1, len(profile))) if len(profile) else 0.0
    threshold = mean_val * strength_threshold

    cuts: list[int] = [0]
    for idx in range(1, desired_cells):
        target = cell_width * idx
        prev = cuts[-1]
        if prev + 1 >= limit:
            break
        lo = max(int(target - search_window), prev + 1)
        hi = min(int(target + search_window) + 1, limit)
        if hi <= lo:
            lo = prev + 1
            hi = lo + 1
        window = profile[lo:hi] if hi <= len(profile) else profile[lo:]
        if window.size == 0:
            chosen = min(int(round(target)), limit - 1)
        else:
            rel = int(np.argmax(window))
            peak_idx = lo + rel
            peak_val = float(window[rel])
            if peak_val >= threshold:
                chosen = peak_idx
            else:
                chosen = int(round(target))
        if chosen <= prev:
            chosen = prev + 1
        if chosen >= limit:
            chosen = limit - 1
        cuts.append(chosen)

    if cuts[-1] != limit:
        cuts.append(limit)

    # Deduplicate while preserving order
    seen: set[int] = set()
    dedup: list[int] = []
    for c in cuts:
        if c not in seen:
            seen.add(c)
            dedup.append(c)
    return dedup


def detect_grid(
    arr_rgba: np.ndarray,
    pixel_size_override: float | None = None,
    min_cuts_per_axis: int = 4,
    fallback_target_segments: int = 64,
    max_step_ratio: float = 1.8,
) -> tuple[list[int], list[int], float]:
    """Detect grid cuts (Hugo's full algorithm, faithful port).

    Returns (col_cuts, row_cuts, effective_step_size). col_cuts defines the
    vertical cell boundaries (X positions); row_cuts the horizontal ones.

    Step sizes are tracked as floats throughout to avoid drift over long
    sweeps (a 0.5-px-per-step error compounds to several pixels by the time
    the walker reaches the far edge of the sprite).
    """
    h, w = arr_rgba.shape[:2]

    prof_x = compute_gradient_profile(arr_rgba, axis=1)
    prof_y = compute_gradient_profile(arr_rgba, axis=0)

    if pixel_size_override is not None:
        step_x = step_y = float(pixel_size_override)
    else:
        sx = estimate_step_size(prof_x)
        sy = estimate_step_size(prof_y)
        # Hugo's resolve_step_sizes: average unless ratio > max_step_ratio
        if sx is None and sy is None:
            fallback = max(1.0, min(h, w) / fallback_target_segments)
            step_x = step_y = fallback
        elif sx is None:
            step_x = step_y = float(sy)
        elif sy is None:
            step_x = step_y = float(sx)
        else:
            ratio = max(sx, sy) / max(1e-9, min(sx, sy))
            if ratio > max_step_ratio:
                step_x = step_y = float(min(sx, sy))
            else:
                step_x = step_y = float((sx + sy) / 2.0)

    col_cuts = walk(prof_x, step_x)
    row_cuts = walk(prof_y, step_y)

    col_cuts = stabilize_axis(col_cuts, step_x, w)
    row_cuts = stabilize_axis(row_cuts, step_y, h)

    # Hugo's fallback: if a profile yielded too few cuts (weak gradients in
    # smooth sprites), snap to uniform cuts at the resolved step size.
    if len(col_cuts) < min_cuts_per_axis:
        col_cuts = snap_uniform_cuts(prof_x, w, step_x, min_required=min_cuts_per_axis)
    if len(row_cuts) < min_cuts_per_axis:
        row_cuts = snap_uniform_cuts(prof_y, h, step_y, min_required=min_cuts_per_axis)

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
    pixel_size: float | None = None,
    alpha_threshold: int = 1,
    kmeans_seed: int = 42,
    kmeans_iters: int = 15,
    kmeans_tol: float = 0.01,
) -> tuple[Image.Image, float]:
    """Snap a transparent-bg concept to a clean pixel grid (Sprite Fusion).

    Faithful port of Hugo Duprez's spritefusion-pixel-snapper:
      1. K-means++ quantize the full-res opaque pixels (alpha >= threshold;
         default threshold=1, matching Hugo's "anything not fully-
         transparent is opaque" rule).
      2. Replace each opaque pixel with its nearest centroid; preserve
         original alpha; zero out RGB of background pixels for clean mode
         counting.
      3. Compute X/Y gradient profiles on the quantized image (full gray
         where alpha > 0, zero where alpha == 0).
      4. Estimate float step size per axis (median of peak-to-peak distances
         in each profile).
      5. Walk each profile with FLOAT arithmetic, snapping to a local peak
         only when peak > 0.5 × mean(profile). Otherwise place a uniform
         cut. This aligns each cell with one logical pixel of the original
         drawing without being deflected by smooth-region noise.
      6. Fall back to snap_uniform_cuts if the walker yielded too few cuts.
      7. Resample: per cell, take the MODE of (R,G,B,A) tuples — ties
         broken by smallest packed value.

    Why faithful porting matters: integer-truncating the step size compounds
    a sub-pixel error over the sweep that smears 1-pixel outlines across
    two cells (body wins mode → outline disappears). Excluding edge pixels
    from k-means training (alpha_threshold=128) starves the dark cluster
    of outline samples (no dedicated near-black centroid → outlines merge
    into "dark brown"). Both bugs ship together as muddy outlines; the
    fixes ship together as crisp ones.

    Output is at NATIVE LOGICAL RESOLUTION (small, e.g. 80-250px per side).
    Use `upscale.py` to NEAREST-upscale to a display size.
    """
    img = Image.open(input_path).convert("RGBA")
    orig_w, orig_h = img.size

    arr = np.array(img)  # (H, W, 4) uint8
    alpha = arr[..., 3]
    # Hugo treats `alpha > 0` as opaque (default alpha_threshold=1). Including
    # anti-aliased / soft-matte edge pixels in k-means training is what gives
    # the quantizer enough dark-outline samples to allocate a dedicated near-
    # black centroid. Excluding them (the old default of 128) starves the
    # dark cluster and pulls outlines into the "dark brown" centroid instead.
    fg_mask = alpha >= alpha_threshold

    # 1. K-means quantize the opaque pixels.
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

    # Zero out RGB of background pixels (alpha < threshold) so they all pack
    # to the same sentinel for mode-per-cell counting. This is a safety net
    # over Hugo's behavior — the bg-removal helper can leave despill residue
    # in alpha=0 pixels (small non-zero RGB), which would fragment mode counts
    # on edge cells. Hugo's reference inputs have clean (0,0,0,0) backgrounds.
    rgb_quantized = rgb_quantized.copy()
    rgb_quantized[~fg_mask] = 0
    # Preserve original alpha (Hugo's behavior). The mode-per-cell step keys
    # off the full (R,G,B,A) tuple; partial-alpha edge pixels naturally
    # become partial-alpha output pixels for a soft silhouette.
    quantized_rgba = np.dstack([rgb_quantized, alpha])

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
        type=float,
        default=None,
        help="Override the auto-detected native pixel block size (float; the "
        "walker keeps float precision across the sweep). If omitted, the "
        "snapper detects from the (quantized) input.",
    )
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        default=1,
        help="A pixel is treated as opaque if alpha >= threshold (default 1, "
        "matching Hugo's reference implementation). Includes anti-aliased / "
        "soft-matte edge pixels in k-means training, which is what gives the "
        "quantizer enough dark-outline samples to allocate a dedicated near-"
        "black centroid. Raise to ~64-128 for inputs where soft-matte residue "
        "is producing a halo around the silhouette.",
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
        print(f"  detected native pixel size: {used_pixel_size:.2f}px (from quantized image)")
    else:
        print(f"  used pixel size: {used_pixel_size:.2f}px (manual override)")
    print(f"  k-means palette: k={args.colors}, seed={args.kmeans_seed}, max_iter={args.kmeans_iters}")
    print(f"  alpha threshold: {args.alpha_threshold}")
    print(f"  output size: {result.size}  (Sprite Fusion native logical resolution)")


if __name__ == "__main__":
    main()
