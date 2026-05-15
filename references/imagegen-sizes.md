# `imagegen` Size and Quality Guidance

This skill makes **one** `imagegen` call per character/object — the concept art step.

## Recommended prompt guidance

| Step | Size | Quality |
|------|------|---------|
| Concept art | `1024x1024` | **high** |

## Important note about size

The built-in `image_gen` tool does NOT strictly enforce the requested size. Asking for `1024x1024` often returns `1254x1254` or other non-standard dimensions. **This is expected behavior** and doesn't break the pipeline — the snapper handles arbitrary input dimensions, and `upscale.py` normalizes the display preview to the requested canvas size.

The CLI fallback (`gpt-image-2`) DOES strictly enforce size, but the imagegen SKILL documentation explicitly says *"Do not switch to CLI fallback for ordinary quality, size, or file-path control."* So we accept whatever the built-in tool returns and normalize downstream.

## How to specify in built-in `image_gen` calls

```
image_gen with prompt="<complete structured prompt that asks for a square, about 1024x1024, high-quality output>"
```

Do not pass `size`, `quality`, destination-path, or model arguments to the built-in tool unless the current host schema explicitly supports them. In Codex hosts where the built-in tool only accepts `prompt`, passing extra arguments makes the image generation step fail before it starts.

The final snapped output is native logical resolution; the final upscaled display output is the 1024×1024 canvas.

## Cost

~$0.17 per call at `quality=high`. Iteration is typical: 1-3 re-rolls per character before user accepts. Per-character total: ~$0.20–0.70 at the concept stage. Snap and chroma-key removal are local Python — free.
