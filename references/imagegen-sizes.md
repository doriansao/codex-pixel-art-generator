# `imagegen` Size and Quality Guidance

This skill makes **one** `imagegen` call per character/object — the concept art step.

## Recommended setting

| Step | Size | Quality |
|------|------|---------|
| Concept art | `1024x1024` | **high** |

## Important note about size

The built-in `image_gen` tool does NOT strictly enforce the requested size. Requesting `1024x1024` often returns `1254x1254` or other non-standard dimensions. **This is expected behavior** and doesn't break the pipeline — the snapper's `--output-size 1024 1024` flag normalizes to exactly 1024×1024 regardless of what imagegen produced.

The CLI fallback (`gpt-image-2`) DOES strictly enforce size, but the imagegen SKILL documentation explicitly says *"Do not switch to CLI fallback for ordinary quality, size, or file-path control."* So we accept whatever the built-in tool returns and normalize downstream.

## How to specify in `imagegen` calls

```
imagegen with prompt="...", size="1024x1024", quality="high"
```

If the parameter form isn't accepted, ask in the prompt itself: "Output exactly 1024×1024 pixels at high quality."

Either way, the final snapped output is exactly 1024×1024 (the snapper handles it).

## Cost

~$0.17 per call at `quality=high`. Iteration is typical: 1-3 re-rolls per character before user accepts. Per-character total: ~$0.20–0.70 at the concept stage. Snap and chroma-key removal are local Python — free.
