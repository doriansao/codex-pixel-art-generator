---
name: pixel-art-generator
description: Generate beautiful 2D pixel art characters, weapons, items, powerups, props, and layout tiles for video games and animations. The agent takes a casual natural-language prompt, optionally a style reference (game name) or reference image, and produces three transparent-background outputs - clean concept art, Sprite Fusion-snapped pixel art at native logical resolution, and a 1024x1024 NEAREST upscale for display. Trigger keywords - pixel art, sprite art, 2D character pixel art, 2D object pixel art, weapon pixel art, item pixel art, powerup pixel art, prop pixel art, tile pixel art, retro game asset, indie game asset, character concept art. Authored by Dorian Butron.
---

# Pixel Art Generator

**Authored by Dorian Butron.**

The skill's contract: **produce pixel art for video games. Always.**

- Vague prompt → produce a sensible pixel-art default.
- Detailed prompt → produce pixel art matching the user's specifics.
- Style reference (game name) → produce pixel art in that game's style.
- Reference image attached → produce pixel art that matches the reference's identity and silhouette.

Works for **characters** (warriors, mages, NPCs, monsters, mounts, pets), **weapons & equipment**, **powerups & items**, **props**, and **layout / environment pieces** (tiles, doors, trees, rocks, terrain elements).

## What the skill produces

Three transparent-background PNGs per asset:

1. **Concept art** (`<name>_concept.png`) — clean transparent PNG from `imagegen` + bg removal. Roughly 1024×1024 (or 1254×1254 — whatever imagegen returned). The artist-facing reference image.
2. **Snapped pixel art** (`<name>_snapped.png`) — small native logical resolution (e.g., 114×114). Every pixel in the file IS one logical pixel. Sprite Fusion algorithm (Hugo Duprez) with k-means quantization + grid-aligned mode-per-cell. **This is the canonical game-engine asset** — engines NEAREST-upscale at runtime for crisp display.
3. **Upscaled display version** (`<name>_upscaled.png`) — NEAREST upscale of the snapped image, fit into a 1024×1024 canvas while preserving aspect ratio. For preview / marketing / display use.

## The agent's primary job: prompt enrichment

**The skill is mechanical** — the snapper + upscaler convert any input into pixel art deterministically. **The agent is the creative layer.** Its job:

1. Take the user's casual natural-language input.
2. Expand it into a rich, specific imagegen prompt that the model can render coherently.
3. Run the pipeline (imagegen → review → bg strip → snap → upscale).

The agent uses world knowledge to fill in visual specifics the user didn't bother to mention — color palettes, distinctive features, pose, clothing details, era/genre cues — without inventing things the user didn't ask for. See `references/concept-prompt-template.md` for the structured template and translation examples.

When the user gives a style hint (era / mood / specific game), the agent looks at `references/style-references.md` for canonical game names to integrate as references. **There is no fixed anchor library to pick from** — variety comes from the user's prompt + the agent's enrichment, not from a curated style preset.

## Image generation tool — REQUIRED

Concept art is generated via the built-in **`image_gen` tool** (the `imagegen` skill). NOT by writing Python that draws shapes with PIL primitives.

This skill uses three tools in the pipeline:

- **`$CODEX_HOME/skills/.system/imagegen/scripts/remove_chroma_key.py`** (imagegen skill's bundled bg-removal). Uses proper alpha matting + despill — never write a custom one (color-distance matching at tolerance > 0 punches holes in character pixels close to the bg color).
- **`scripts/snap_pixels.py`** (this skill) — Sprite Fusion-style pixel snapper. K-means quantize + grid-aligned mode-per-cell.
- **`scripts/upscale.py`** (this skill) — NEAREST upscale to a target canvas (default 1024×1024) preserving aspect ratio with transparent padding.

## Architecture: 1 imagegen call + 3 Python steps per asset

```
Step 1: Prompt enrichment        Agent expands user's NL input → rich imagegen prompt
Step 2: Concept generation       imagegen → tmp/imagegen/<name>_concept_raw.png  (chroma-key bg)
Step 3: USER REVIEW               Show raw concept to user → accept / modify / regenerate
Step 4: Strip bg (after accept)   imagegen helper → concept/<name>_concept.png  (transparent)
Step 5: Pixel snap                snap_pixels.py → concept/<name>_snapped.png  (small native, transparent)
Step 6: Upscale                   upscale.py → concept/<name>_upscaled.png  (1024×1024, transparent)
```

**Bg removal is deferred until after the user accepts** — rejected iterations don't waste the bg-removal step.

Per asset: 1 imagegen call + 2 local Python calls + 1 imagegen-helper call. Cost: ~$0.20–0.70 depending on iteration count.

## Files this skill ships with

```
scripts/
  snap_pixels.py            # CLI: Sprite Fusion pixel snap, outputs small native transparent
  upscale.py                # CLI: aspect-preserving NEAREST upscale to 1024x1024 canvas

references/
  concept-prompt-template.md  # imagegen prompt template + agent prompt-enrichment examples
  style-references.md         # game-name reference list by era/mood (no anchor structure)
  imagegen-sizes.md           # size + quality settings for the concept art step
  failure-modes.md            # symptom → cause → fix table
```

**External tool (REUSED, not bundled):** `$CODEX_HOME/skills/.system/imagegen/scripts/remove_chroma_key.py` — the imagegen skill's bg-removal helper. Used once in the pipeline (Step 4).

## Workflow

### Step 1 — Prompt enrichment

This is where the agent earns its keep. Read the user's natural-language input and translate it into a rich `Subject:` line for the imagegen prompt.

**Read the user's input and identify:**

- **Subject category** — character / weapon / item / monster / vehicle / tile / environment / prop.
- **Specifics the user mentioned** — names, colors, traits, accessories, era, style refs. Preserve these EXACTLY.
- **Style direction** — if the user named a specific game (e.g., "River City Ransom style"), keep that name verbatim. If they gave a directional hint (e.g., "16-bit JRPG", "cyberpunk", "modern indie"), check `references/style-references.md` for 2-4 specific game names to integrate.
- **Reference image** — if the user attached one, the prompt uses Variation 3 (preserve identity, transform rendering style).

**Then enrich** using your world knowledge:

- For characters: add age/build, hair (style + color), eye color, distinctive facial features, clothing pieces with materials + colors, accessories, pose, expression, anything held.
- For weapons/items: shape, materials (steel/wood/gem/leather), color palette, ornamentation, perspective (3/4 for weapons, front-facing for symmetric items).
- For monsters: silhouette type, dominant colors, distinctive features (horns/wings/tail/eyes).
- For tiles/environments: specify tile size, whether it tiles seamlessly, the surface type and texture.

**Don't:**
- Override the user's choices (if they said "red sneakers", keep red sneakers).
- Invent companions, scenery, or lore the user didn't ask for.
- Replace style references with generic descriptions — your enrichment SUPPLEMENTS, doesn't REPLACE.
- Over-specify; add enough detail for coherence, not a paragraph per body part.

**Style-reference integration (the River City Ransom case):** when the user names a specific game, that game name goes VERBATIM into the Subject line, AND you add specific visual descriptors that match that game's known characters/style. Do NOT bury the game name under abstract structural parameters — that dilutes the reference. Example: "Kunio from River City Ransom" → "Kunio, the protagonist of River City Ransom / Downtown Nekketsu Monogatari (Technos, NES, 1989) — short spiky black hair with a small forelock, white sleeveless tank top, blue denim jeans, red sneakers, fists clenched in a ready stance, Technos-NES-era chibi proportions."

**Pick a concept-art chroma-key:**

- Default: `#00ff00` (green).
- Use `#ff00ff` (magenta) if the subject is green-themed (green dragon, slime, grass-warrior).
- Avoid `#0000ff` (blue) for blue subjects.

This is the bg the model renders BEHIND the subject; it's stripped to transparent at Step 4.

**Save** the agent's enriched prompt to `tmp/prompt.md` for reference.

See `references/concept-prompt-template.md` for the full structured template and translation examples.

### Step 2 — Generate concept art

Follow the imagegen skill's documented transparent-image workflow (see `$CODEX_HOME/skills/.system/imagegen/SKILL.md` → "Transparent image requests").

Invoke `image_gen` with `size='1024x1024'`, `quality='high'`, the enriched prompt from Step 1, and the chroma-key bg request block:

```text
Create the requested subject on a perfectly flat solid <CHROMA_KEY_HEX> chroma-key background for background removal.
The background must be one uniform color with no shadows, gradients, texture, reflections, floor plane, or lighting variation.
Keep the subject fully separated from the background with crisp edges and generous padding.
Do not use <CHROMA_KEY_HEX> anywhere in the subject.
No cast shadow, no contact shadow, no reflection, no watermark, and no text unless explicitly requested.
```

Save the selected output to `tmp/imagegen/<name>_concept_raw.png` (copy from `$CODEX_HOME/generated_images/...`).

Every imagegen call also includes the **universal Pixel art rendering line** from `concept-prompt-template.md` — this is what enforces "draw as pixel art, not detailed illustration" at the prompt level.

### Step 3 — USER REVIEW (critical — do not skip)

Show the user the raw concept (with chroma-key bg) and wait for explicit accept / modify / reject. Do NOT auto-proceed.

1. **Accept** → proceed to Step 4.
2. **Modify** → adjust the prompt and re-run Step 2.
3. **Reject** → restart Step 2 with a fresh prompt or different style direction.

Iteration is unbounded. Concept art is the visual ceiling — get it right before bg-strip / snap / upscale.

### Step 4 — Strip background to transparent (after user accepts)

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/remove_chroma_key.py" \
    --input tmp/imagegen/<name>_concept_raw.png \
    --out concept/<name>_concept.png \
    --auto-key border \
    --soft-matte \
    --transparent-threshold 12 \
    --opaque-threshold 220 \
    --despill
```

Validate: alpha channel present, transparent corners, subject coverage plausible, no key-color fringe. If a thin fringe remains, retry once with `--edge-contract 1`.

### Step 5 — Pixel snap (Sprite Fusion)

```bash
python scripts/snap_pixels.py \
    --input concept/<name>_concept.png \
    --output concept/<name>_snapped.png \
    --colors 16
```

`--colors` is the k-means palette size. Defaults: `16` (Hugo's default — tight, classic pixel-art palette); raise to `24-32` for color-rich subjects, lower to `8-12` for hardware-constrained 8-bit feel.

Output: small native logical resolution (e.g., 114×114), transparent bg, perfect pixel grid.

### Step 6 — Upscale to display size

```bash
python scripts/upscale.py \
    --input concept/<name>_snapped.png \
    --output concept/<name>_upscaled.png
```

Defaults to a 1024×1024 canvas. Finds the largest integer scale that fits the input inside the canvas (preserves aspect ratio), NEAREST-upscales by that factor, then centers on a transparent canvas of the target size. Never distorts.

For perfectly uniform block widths use `--scale N` (output dimensions = input × N, no canvas).

## Project folder structure

```
outputs/<name>/
├── tmp/
│   ├── prompt.md                          # the enriched prompt the agent built at Step 1
│   └── imagegen/
│       └── <name>_concept_raw.png         # imagegen output with chroma-key bg (intermediate)
└── concept/
    ├── <name>_concept.png                 # 1: clean concept art, transparent bg
    ├── <name>_snapped.png                 # 2: Sprite Fusion pixel-snapped (canonical game asset)
    └── <name>_upscaled.png                # 3: NEAREST upscale to 1024x1024 canvas, transparent
```

## Don'ts

- Don't write character/object art with PIL primitives. `image_gen` only.
- Don't reuse PNGs from prior assets' folders. Every asset generates fresh.
- Don't skip the user review in Step 3. The user reviews the RAW concept BEFORE bg-removal runs.
- Don't run bg removal before user review (Step 4 runs AFTER Step 3 accepts).
- Don't put more than one subject in the frame.
- **Don't write a custom bg-removal tool.** Use the imagegen helper at Step 4. Color-distance matching punches holes; the helper's soft matte preserves character pixels via partial alpha.
- Don't reintroduce a chroma-key flow inside the snapper — the snapper operates on the transparent concept and outputs transparent.
- Don't ship `_upscaled.png` as the game-engine asset. Ship `_snapped.png` — engines NEAREST-upscale at runtime and the result is crisper.
- Don't bury style references under abstract structural parameters. If the user named "Castlevania III NES", that game name belongs in the Subject line directly. Don't dilute it with sprite-size / palette / shading paragraphs that average across many similar games.

## When something goes wrong

See `references/failure-modes.md`. Common cases:

- Output doesn't match a specific game style the user named → check that the game name is in the Subject line VERBATIM, plus character-specific descriptors. Encourage the user to attach a reference image — that's the highest-fidelity match for specific styles.
- Holes in character → never write a custom bg-removal tool; use the imagegen helper at Step 4 with the documented flags.
- Subject color matches the chroma-key → flip Step 1's chroma-key (green ↔ magenta).
- Snapped output too coarse / too fine → override with `--pixel-size N` on the snapper.
- Upscaled output has uneven block widths → expected for non-integer ratios; use `--scale N` for uniform blocks.
- Multiple subjects in frame → re-roll with stricter "single subject" language in the prompt.
- Concept came back as detailed illustration (smooth gradients, fine details) → make sure the universal `Pixel art rendering:` line was included in the imagegen prompt. That line is the prompt-level enforcer.
