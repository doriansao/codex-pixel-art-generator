#!/usr/bin/env python3
"""NEAREST-neighbor upscale a small pixel-art image, preserving aspect ratio.

Pairs with `snap_pixels.py`. The snapper produces small native-resolution
images (e.g., 172x236 for a portrait sprite); this tool upscales them onto
a target canvas (default 1024x1024) using NEAREST-NEIGHBOR.

DEFAULT BEHAVIOR (canvas-fit mode):
  Find the LARGEST INTEGER scale factor that fits the input inside the
  target canvas, NEAREST-upscale by that factor, then center on a transparent
  canvas of the target size.

  Example: 172x236 input into a 1024x1024 canvas:
    - scale_w = 1024 // 172 = 5
    - scale_h = 1024 // 236 = 4
    - fit_scale = min(5, 4) = 4
    - scaled = 688x944 (NEAREST upscale by 4)
    - centered on 1024x1024 transparent canvas

  This preserves the input's aspect ratio AND keeps a perfect pixel grid
  (every block is exactly scale x scale display pixels). The canvas around
  the image is transparent. NEVER stretches a portrait into a square.

EXPLICIT-SCALE MODE (--scale N):
  Output dimensions = input_size * N. No canvas. Use when you want a
  specific scale factor and don't care about a fixed canvas.

Alpha channel is preserved throughout.

Usage:
  python upscale.py --input snapped.png --output upscaled.png            # canvas-fit, default 1024x1024
  python upscale.py --input snapped.png --output upscaled.png --size 2048 2048
  python upscale.py --input snapped.png --output upscaled.png --scale 4  # no canvas
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def upscale(
    input_path: Path,
    output_path: Path,
    size: tuple[int, int] | None = (1024, 1024),
    scale: int | None = None,
) -> Image.Image:
    """NEAREST-upscale a pixel-art image, preserving aspect ratio.

    Two modes:

    1. **Canvas-fit mode (default, when `size` is set and `scale` is None):**
       Find the LARGEST INTEGER scale factor that makes the input fit inside
       the target canvas (e.g., 1024×1024). NEAREST-upscale by that factor —
       preserves the input's aspect ratio AND keeps a clean pixel grid (every
       block is exactly `scale × scale` display pixels). Then center the
       upscaled image on a transparent canvas of `size` dimensions.

       Example: 172×236 input into a 1024×1024 canvas →
       `min(1024//172=5, 1024//236=4) = 4` → scaled to 688×944, centered on
       a 1024×1024 transparent canvas (168 px transparent padding on each
       side horizontally; 40 px top/bottom).

       This is the fix for the "concept was 1024×1536 portrait, upscaled to
       1024×1024 square = distorted" bug. We never stretch to non-uniform
       aspect; we fit and pad.

    2. **Explicit-scale mode (when `scale` is provided):**
       Output dimensions = `(input_w * scale, input_h * scale)`, no canvas.
       Use this when you want a specific scale factor regardless of canvas.

    Args:
        input_path: Source PNG (typically a small native-resolution snapped
            sprite).
        output_path: Destination PNG.
        size: Target canvas dimensions (W, H). Defaults to (1024, 1024).
            Image is centered on this canvas with transparent padding.
            Ignored if `scale` is provided.
        scale: Explicit integer scale factor. If provided, overrides `size`.

    Returns:
        The upscaled image (also written to output_path).
    """
    img = Image.open(input_path).convert("RGBA")
    orig_w, orig_h = img.size

    if scale is not None:
        # Explicit-scale mode: no canvas, just multiply dimensions.
        target_w = orig_w * scale
        target_h = orig_h * scale
        result = img.resize((target_w, target_h), Image.Resampling.NEAREST)
    else:
        if size is None:
            size = (1024, 1024)
        canvas_w, canvas_h = size

        # Find the largest integer scale that fits the input inside the canvas.
        scale_w = canvas_w // orig_w
        scale_h = canvas_h // orig_h

        if scale_w < 1 or scale_h < 1:
            # Input is larger than the canvas on at least one axis. This
            # USUALLY means pipeline misuse — `upscale.py` expects the
            # small native-resolution snapped sprite (Step 5 output,
            # typically 50-250 px per side), not a full-resolution concept
            # (Step 4 output, ~1024x1024). If you're seeing this warning,
            # check that you ran `snap_pixels.py` before `upscale.py`.
            #
            # We still produce an output via a NEAREST downscale so the
            # call doesn't fail outright, but the warning is loud so the
            # misuse doesn't go unnoticed.
            import sys

            fit_ratio = min(canvas_w / orig_w, canvas_h / orig_h)
            scaled_w = max(1, int(orig_w * fit_ratio))
            scaled_h = max(1, int(orig_h * fit_ratio))
            print(
                f"  WARNING: input ({orig_w}x{orig_h}) is LARGER than the "
                f"target canvas ({canvas_w}x{canvas_h}). This usually means "
                f"the pipeline was used incorrectly — `upscale.py` expects "
                f"the small snapped sprite from `snap_pixels.py` (Step 5), "
                f"not the full-resolution concept (Step 4).\n"
                f"  Did you skip Step 5 (the pixel snap)? Run snap_pixels.py "
                f"first.\n"
                f"  Proceeding with a NEAREST downscale to {scaled_w}x{scaled_h} "
                f"to fit the canvas — some input pixels are dropped and the "
                f"per-pixel art quality is reduced. Pass --scale N to skip "
                f"canvas-fit entirely, or --size with a larger canvas.",
                file=sys.stderr,
            )
            scaled = img.resize((scaled_w, scaled_h), Image.Resampling.NEAREST)
        else:
            # Normal case: integer-scale up so the input fits inside the canvas.
            fit_scale = min(scale_w, scale_h)
            scaled_w = orig_w * fit_scale
            scaled_h = orig_h * fit_scale
            scaled = img.resize((scaled_w, scaled_h), Image.Resampling.NEAREST)

        # Center on a transparent canvas of the target size.
        result = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        offset_x = (canvas_w - scaled_w) // 2
        offset_y = (canvas_h - scaled_h) // 2
        result.paste(scaled, (offset_x, offset_y), scaled)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", "-i", type=Path, required=True, help="Input PNG path (small pixel-art image).")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Output PNG path (NEAREST-upscaled).")
    parser.add_argument(
        "--size",
        type=int,
        nargs=2,
        default=[1024, 1024],
        metavar=("W", "H"),
        help="Target CANVAS dimensions in display pixels (default 1024 1024). "
        "The input is NEAREST-upscaled by the largest integer factor that "
        "fits inside this canvas (preserving aspect ratio), then centered "
        "on a transparent canvas of these dimensions. Never stretches the "
        "input into a non-uniform aspect ratio.",
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=None,
        help="Explicit integer scale factor (overrides --size). Output "
        "dimensions = input_size * scale, no canvas, no padding. Use this "
        "when you want a specific scale factor regardless of canvas size.",
    )
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"input not found: {args.input}")

    result = upscale(
        args.input,
        args.output,
        size=tuple(args.size) if args.scale is None else None,
        scale=args.scale,
    )

    orig_w, orig_h = Image.open(args.input).size
    print(f"upscaled {args.input} -> {args.output}")
    print(f"  input size: ({orig_w}, {orig_h})")
    print(f"  output size: {result.size}")
    if args.scale is not None:
        print(f"  mode: explicit-scale {args.scale}x")
    else:
        canvas_w, canvas_h = args.size[0], args.size[1]
        scale_w = canvas_w // orig_w
        scale_h = canvas_h // orig_h
        if scale_w < 1 or scale_h < 1:
            fit_ratio = min(canvas_w / orig_w, canvas_h / orig_h)
            scaled_w = max(1, int(orig_w * fit_ratio))
            scaled_h = max(1, int(orig_h * fit_ratio))
            print(f"  mode: canvas-fit DOWNSCALE (canvas {canvas_w}x{canvas_h}, input larger than canvas)")
            print(f"  fit ratio: {fit_ratio:.3f}x -> image at {scaled_w}x{scaled_h}, centered with transparent padding")
        else:
            fit_scale = min(scale_w, scale_h)
            scaled_w = orig_w * fit_scale
            scaled_h = orig_h * fit_scale
            print(f"  mode: canvas-fit upscale (canvas {canvas_w}x{canvas_h})")
            print(f"  fit scale: {fit_scale}x -> image at {scaled_w}x{scaled_h}, centered with transparent padding")


if __name__ == "__main__":
    main()
