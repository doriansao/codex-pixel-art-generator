---
name: pixel-art-generator
description: Generate beautiful 2D pixel art characters, weapons, items, powerups, props, and layout tiles for video games and animations. The agent takes a casual natural-language prompt, optionally a style hint or reference image, and produces three transparent-background outputs - clean concept art, Sprite Fusion-snapped pixel art at native logical resolution, and a 1024x1024 NEAREST upscale for display. Trigger keywords - pixel art, sprite art, 2D character pixel art, 2D object pixel art, weapon pixel art, item pixel art, powerup pixel art, prop pixel art, tile pixel art, retro game asset, indie game asset, character concept art. Authored by Dorian Butron.
---

# Pixel Art Generator

**Authored by Dorian Butron.**

The skill's contract: **produce pixel art for video games. Always.**

- Vague prompt → produce a sensible pixel-art default.
- Detailed prompt → produce pixel art matching the user's specifics.
- Style hint (era, mood, genre) → produce pixel art anchored on those abstract descriptors using the vocabulary in `references/visual-vocabulary.md`.
- Reference to a named IP (character, franchise, game title, studio) — text or attached image → the agent runs the **6-phase IP-reference process** (Step 1 below) to translate the named reference into original, abstract visual traits before calling `image_gen`. The final prompt contains NO protected proper nouns, and the output is a genuinely original asset inspired by the user's intent.

The 6-phase process is universal — it applies to ANY proper-noun reference the user might mention, without needing a curated list of "famous characters." Abstract design dimensions, not IP names, are what reach the image generator.

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

The agent uses world knowledge to fill in visual specifics the user didn't bother to mention — color palettes, distinctive features, pose, clothing details, era/genre cues — without inventing things the user didn't ask for. See `references/concept-prompt-template.md` for the structured template and an example of the 6-phase process applied end-to-end.

When the user gives a style hint (era / mood / genre), the agent draws abstract descriptors from `references/visual-vocabulary.md`. **There is no curated anchor library and no list of named games** — the agent uses world knowledge to interpret the user's intent, then writes the prompt using only abstract dimensions (era, hardware constraints, palette family, silhouette, mood) drawn from the visual vocabulary. Variety comes from the user's prompt + the agent's enrichment + the abstract descriptor set, not from named-game presets.

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
  concept-prompt-template.md  # imagegen prompt template + example of the 6-phase process applied
  visual-vocabulary.md        # abstract descriptive vocabulary (era / palette / silhouette / mood) — no IP, no game names
  imagegen-sizes.md           # size + quality settings for the concept art step
  failure-modes.md            # symptom → cause → fix table
```

**External tool (REUSED, not bundled):** `$CODEX_HOME/skills/.system/imagegen/scripts/remove_chroma_key.py` — the imagegen skill's bg-removal helper. Used once in the pipeline (Step 4).

## Workflow

### Step 1 — Prompt enrichment (the 6-phase IP-reference process)

This is where the agent earns its keep. Read the user's natural-language input and translate it into a rich `Subject:` line for the imagegen prompt — using **only abstract design vocabulary**, no protected proper nouns.

**The core rule: no proper nouns reach `image_gen`.** Character names, franchise names, studio names, and game titles are all stripped during enrichment. The agent uses world knowledge in Phases 1-4 to interpret what the user meant; Phase 5 writes the prompt using only abstract descriptors drawn from `references/visual-vocabulary.md`. Phase 6 preflight scans for any leaked references before the prompt is sent.

This is a universal process — it does not depend on a curated list of famous characters. Any proper noun the user might mention (Pikachu, Iron Man, Stardew Valley, Castlevania III, Square Enix, Nintendo, even "NES") is handled by the same six phases.

#### Phase 1 — Detect proper-noun references

Scan the user's input for any capitalized name that isn't generic vocabulary. Examples of what to detect:

- **Character names**: Pikachu, Mario, Link, Iron Man, Sonic, Kunio, Madeline.
- **Franchise / IP names**: Pokemon, Marvel, Star Wars, Final Fantasy.
- **Studio / publisher names**: Nintendo, Capcom, Square Enix, Konami, Technos.
- **Game titles**: River City Ransom, Castlevania III, Chrono Trigger, Stardew Valley.
- **Hardware / platform names**: NES, SNES, Game Boy, Genesis, Pico-8.
- **Visible-in-reference-image IP**: if a user attaches an image, mentally label any recognizable IP in it.

If nothing capitalized is in the prompt and there's no reference image → skip to normal enrichment (use the vocabulary in `visual-vocabulary.md` for any directional hints like "16-bit JRPG" or "cyberpunk").

#### Phase 2 — Classify what role the reference plays

For each detected reference, classify how the user is using it. Five roles:

| Role | Pattern | Risk | Treatment |
|---|---|---|---|
| **exact** | "draw Pikachu", "make Mario", "the actual Cloud Strife" | HIGH | Phase 4 mandatory: make a clearly original character with shifted identity traits. |
| **like** | "X-like", "X-style", "inspired by X", "in the vein of X" where X is a character/franchise | HIGH | Phase 4 mandatory: translate into abstract traits, never copy. |
| **image-of** | User attached a reference image and it depicts protected IP | HIGH | Phase 4 mandatory: do NOT pass the image to `image_gen` (no `Input images:` line). Read traits from the image internally, translate to abstract terms. |
| **style-anchor** | User names a game/franchise as a STYLE anchor ("in the style of Castlevania III") — and the request is NOT for a character from that game | MEDIUM | Phase 4: translate the game-name into abstract era / hardware / palette / mood descriptors. |
| **era-only** | User names hardware ("NES style", "Game Boy palette") or a generic era descriptor | LOW | Phase 4: translate to abstract hardware / era descriptors (e.g., "NES" → "8-bit console era, 3-4 colors per sprite, chibi 1:2 proportions"). |

Original references (user's own art, OC, indie character they made, public-domain artwork, photo of a consenting real person) are NOT in this classification — they bypass Phases 2-4 and go through Variation 3 (preserve identity, transform rendering style). Use judgment to distinguish: protected IP is widely recognizable; OC / personal art typically isn't.

#### Phase 3 — Extract abstract design dimensions

For the subject (whether triggered by an IP reference or a vague user prompt), extract the **eight abstract design dimensions** below using the agent's world knowledge plus `references/visual-vocabulary.md`. These dimensions are the substrate from which the final prompt is written.

1. **Asset type** — character / monster / weapon / item / powerup / prop / vehicle / tile / environment.
2. **Body shape + silhouette** — proportions (chibi 1:2 / chibi 1:3 / semi-chibi 1:4 / adult 1:6 / heroic 1:7), build (compact stocky / slim tall / muscular brawler / mech vertical), pose (front 3/4 idle / combat stance / side-on running).
3. **Palette family** — see `visual-vocabulary.md` → "Palette family vocabulary" (NES-constrained primary / Game Boy DMG 4-shade / SNES vibrant fantasy / cyberpunk neon-on-dark / dark fantasy grim / warm earthy cottagecore / etc.).
4. **Distinctive motifs** — what makes the subject visually identifiable WITHOUT using the protected name (e.g., "yellow electric rodent with lightning-tail and red cheek-circles" instead of "Pikachu"; "armored techno-brawler with chest power core and red/gold panel armor" instead of "Iron Man").
5. **Emotional tone** — see `visual-vocabulary.md` → "Mood / tone vocabulary" (cute / heroic / grim / cyberpunk / playful / mystical / gritty / regal).
6. **Era / hardware** — see `visual-vocabulary.md` → "Era / hardware vocabulary" (8-bit console era / Game Boy DMG / 16-bit SNES / arcade beat'em-up / modern indie chunky / HD-2D / etc.). NEVER write "NES" or "SNES" in the final prompt; use the abstract era descriptor.
7. **Gameplay role** — see `visual-vocabulary.md` → "Genre / role vocabulary" (JRPG protagonist / beat'em-up brawler / monster-catching RPG creature / cyberpunk hacker / dark-fantasy hunter / cozy farm villager / etc.).
8. **Camera angle / pose** — front 3/4 / pure side-view / top-down 3/4 / isometric 3/4 / pure top-down (for tiles).

#### Phase 4 — Transform identity-bearing traits

This is the originality guarantee. For HIGH-risk references (exact / like / image-of), actively alter the identity-bearing traits so the output is genuinely original — not just relabeled. For MEDIUM/LOW-risk, translate but don't necessarily transform.

Five levers to pull (use 2-4 of them, not all five at once — the goal is "clearly inspired, clearly original," not "unrecognizable"):

1. **Silhouette change** — shift proportions (e.g., make a 1:3 chibi into a 1:4 semi-chibi), alter limb / head ratios, adjust outline shape.
2. **Palette shift** — change the dominant-color balance (e.g., crimson + brass + gunmetal instead of crimson + gold; teal + electric blue instead of yellow + red).
3. **Signature symbols altered** — no logos, no franchise icons, no named-power symbols (no triforces, no red Spider-symbols, no Pokeball motifs). Replace with original symbols drawn from the same genre family.
4. **Named powers → generic effects** — "Pikachu's lightning" → "electric spark from cheek glow"; "Iron Man's repulsor" → "cyan energy palm glow"; "Mario's fireball" → "small orange fire orb."
5. **Costume layout altered** — change panel arrangement, armor segment count, helmet face-shape, accessory placement, distinctive prop position.

For MEDIUM-risk style-anchor: typically only need lever 6 (translate to era/palette/silhouette abstract). For LOW-risk era-only: just translate (no transformation needed).

**The originality test** (for HIGH-risk): would someone looking at the final art instantly say "that's [protected name]"? If yes, transform more. If no — but it still feels like the right genre — you're done.

#### Phase 5 — Write the final prompt from abstract traits only

Compose the `Subject:` line of the structured prompt (see `references/concept-prompt-template.md`) using **only** the abstract dimensions from Phase 3 and the transformed traits from Phase 4. NO protected proper nouns appear in:

- `Primary request`
- `Subject`
- `Constraints`
- `Avoid`
- The chroma-key background block

Not even in negative clauses like "not Iron Man" or "no Marvel logo" — those still trip guardrails. The model never sees the protected name; it sees the abstract description.

**Abstract era descriptors replace hardware names.** Write "8-bit console era, 3-4 colors per sprite" instead of "NES style"; write "16-bit JRPG era, ~16-24 colors, chibi 1:3 proportions with dithered shading" instead of "SNES style like Chrono Trigger". Hardware names are technically trademarks; the abstract description is universally legal and gives the model an equally precise visual target via training data.

**Allowed broad genre / archetype language** (not proper nouns — fine to use): "armored techno-brawler", "cute electric creature", "plumber-inspired platform hero", "monster-catching RPG creature", "side-scrolling beat'em-up character".

#### Phase 6 — Preflight scan

Before the prompt goes to `image_gen`, run a 4-check scan:

1. **Copied proper nouns** — does the prompt contain any name from Phase 1's detected list? If yes, return to Phase 5.
2. **"Inspired by X" / "not X" / "X-like" clauses** — do these phrases survive in any form? Strip them. The model doesn't need a negative; it needs the positive abstract description.
3. **Identity-preservation instructions on protected refs** — for `image-of` references where the image was protected IP, is the `Input images:` line absent? It should be. (For original references, `Input images:` with "preserve identity" stays.)
4. **Identity-bearing traits copied verbatim** — did Phase 4 actually transform at least 2-3 levers for HIGH-risk refs? If the description reads like a one-to-one copy with the name removed, go back to Phase 4 and transform more.

If any check fails → return to the appropriate phase and re-run before sending.

#### Image-reference handling (image-of role)

When the user attaches a reference image and it depicts a protected character (image-of role from Phase 2):

- Use the image internally during Phases 3-4 to read visual traits (palette, silhouette, distinctive features).
- Do NOT pass the image to `image_gen`. The `Input images:` line is omitted (Phase 6 check #3).
- Generate the concept normally without pausing. The skill's contract is "generate by default" — don't stall asking for permission.
- At Step 3 user review, lead with one transparent sentence: *"Your reference depicts a recognizable character — I generated an original version inspired by its visual traits. Let me know if you want a different translation or want to attach a different reference."* The user accepts / modifies / rejects normally.

For ORIGINAL reference images (user's own art, OC, public-domain artwork, photo of a consenting real person), the image is passed normally with the Variation 3 `Input images:` line ("preserve identity, transform rendering style").

#### Don'ts in enrichment

- Don't override the user's choices (if they said "red sneakers", keep red sneakers in the abstract description).
- Don't invent companions, scenery, or lore the user didn't ask for.
- Don't replace user-specified details with generic abstractions — your enrichment SUPPLEMENTS, doesn't REPLACE.
- Don't put protected character / franchise / studio / hardware names into the final `image_gen` prompt, even inside "not copying X" or "no X logo" clauses.
- Don't over-specify; add enough detail for coherence, not a paragraph per body part.
- Don't skip Phase 6 — it's the safety net.

**Pick a concept-art chroma-key:**

The rule: **the chroma-key's strong channels must NOT match the subject's strong channels.** The bg-removal helper detects which channels are "key channels" and treats any pixel dominated by those channels as key-like. If skin / hair / clothing / saturated accents share a strong channel with the key, those pixels get stripped to transparent.

- **Default: `#00ff00`** (green). Strong channel: G. Safe for almost everything — humans (warm skin = R + some B, not G), most clothing, most natural subjects.
- **Use `#ff00ff`** (magenta) ONLY when the subject's dominant body color is green AND the subject contains NO warm skin tones (e.g., green slime, green dragon, full-body Hulk-style character, forest druid with green hood covering the face). **Never use magenta for human characters with visible skin** — warm pink/peach skin is R-dominant, and magenta has R as a key channel; despill will strip the red from skin and turn it white/gray. Olive-jacket-but-human-face = green chroma-key.
- **Use `#FFFF00`** (yellow) for the rare case where the subject contains BOTH green AND magenta (e.g., a watermelon prop with green skin and magenta flesh, or a ZX Spectrum palette character). Strong channels: R + G. Avoid for warm-skinned humans (same R-dominance problem as magenta).
- **Avoid `#0000ff`** (blue) for blue subjects (blue clothing, blue hair, water elementals).

If two different rules conflict (e.g., humanoid with green hair and pink skin), prefer the **default green** unless the green character body color is truly dominant in the silhouette. A pale-pink face is more visually load-bearing than green hair, so green chroma-key is correct.

This is the bg the model renders BEHIND the subject; it's stripped to transparent at Step 4 using `--key-color "<HEX>"` (explicit — NEVER `--auto-key border`, see Step 4 explanation).

**Save** the agent's enriched prompt to `tmp/prompt.md`. This is for the user's reference — useful for debugging (compare against what `image_gen` produced), iterating (tweak by hand and re-run), or auditing the agent's translation work (especially for HIGH-risk IP-reference cases where the agent ran the full 6-phase process).

See `references/concept-prompt-template.md` for the full structured template and an end-to-end example of the 6-phase process.

### Step 2 — Generate concept art

Follow the imagegen skill's documented transparent-image workflow (see `$CODEX_HOME/skills/.system/imagegen/SKILL.md` → "Transparent image requests").

Invoke the built-in `image_gen` tool with the enriched prompt from Step 1 and the chroma-key bg request block below. The built-in tool's current host API may only accept a `prompt` argument; do **not** pass unsupported `size`, `quality`, destination-path, or model parameters to the built-in tool. Put desired size/quality guidance inside the prompt text instead:

```text
Create the requested subject on a perfectly flat solid <CHROMA_KEY_HEX> chroma-key background for background removal.
The background must be one uniform color with no shadows, gradients, texture, reflections, floor plane, or lighting variation.
Keep the subject fully separated from the background with crisp edges and generous padding.
Do not use <CHROMA_KEY_HEX> anywhere in the subject.
No cast shadow, no contact shadow, no reflection, no watermark, and no text unless explicitly requested.
```

Save the selected output to `tmp/imagegen/<name>_concept_raw.png` (copy from `$CODEX_HOME/generated_images/...` or the generated-image path shown by the host).

Every imagegen call also includes the **universal Pixel art rendering line** from `concept-prompt-template.md` — this is what enforces "draw as pixel art, not detailed illustration" at the prompt level.

### Step 3 — USER REVIEW (critical — do not skip)

Show the user the raw concept (with chroma-key bg) and wait for explicit accept / modify / reject. Do NOT auto-proceed.

1. **Accept** → proceed to Step 4.
2. **Modify** → adjust the prompt and re-run Step 2.
3. **Reject** → restart Step 2 with a fresh prompt or different style direction.

Iteration is unbounded. Concept art is the visual ceiling — get it right before bg-strip / snap / upscale.

### Step 4 — Strip background to transparent (after user accepts)

Pass `--key-color "<HEX>"` matching the chroma-key you chose in Step 1 (e.g., `#00ff00`, `#ff00ff`, `#FFFF00`). **Do not use `--auto-key border`** — it samples the actual border pixel color from the imagegen output, and the model often renders the bg as a near-but-not-exact color (e.g., `#fa03e8` instead of `#ff00ff` with a 1-2 pixel gradient). When the auto-sampled key has even one channel below the spill-detection threshold (`max - 16`), the helper misclassifies the key as a single-channel key, and any pixel dominated by that channel gets treated as key-like — including warm-skinned human faces on a magenta bg, or green-themed characters on a green bg.

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/remove_chroma_key.py" \
    --input tmp/imagegen/<name>_concept_raw.png \
    --out concept/<name>_concept.png \
    --key-color "<CHROMA_KEY_HEX>" \
    --soft-matte \
    --transparent-threshold 12 \
    --opaque-threshold 220 \
    --despill
```

Windows PowerShell:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
python (Join-Path $codexHome "skills/.system/imagegen/scripts/remove_chroma_key.py") `
    --input tmp/imagegen/<name>_concept_raw.png `
    --out concept/<name>_concept.png `
    --key-color "<CHROMA_KEY_HEX>" `
    --soft-matte `
    --transparent-threshold 12 `
    --opaque-threshold 220 `
    --despill
```

Substitute `<CHROMA_KEY_HEX>` with the same color you embedded in the imagegen prompt's `Scene/backdrop` block (default `#00ff00`).

Validate: alpha channel present, transparent corners, subject coverage plausible, no key-color fringe, **and skin / dominant subject colors fully opaque**. If skin or saturated foreground areas came out transparent or pale, the chroma-key choice was wrong for this subject (see Step 1 chroma-key picker + `references/failure-modes.md`). If a thin fringe remains, retry once with `--edge-contract 1`.

### Step 5 — Pixel snap (Sprite Fusion)

```bash
python scripts/snap_pixels.py \
    --input concept/<name>_concept.png \
    --output concept/<name>_snapped.png \
    --colors 16
```

`--colors` is the k-means palette size. **Picking the right `k` is load-bearing** — it controls whether shading on skin, hair, and metallic surfaces resolves into distinct mid-tones or collapses into flat blocks. Pick based on the subject's era / aesthetic, not on intuition:

| `--colors` | Use when the subject's era / aesthetic is… | Examples (per `visual-vocabulary.md`) |
|---|---|---|
| **8–12** | hardware-constrained early eras (small palette per sprite is the AESTHETIC) | 8-bit primitive, 8-bit NES, Game Boy DMG (4-shade), Pico-8 fantasy-console, pixel horror lo-fi, roguelike top-down |
| **16** (default) | classic 8/16-bit consoles + arcade golden age | Game Boy Color, 16-bit SNES JRPG overworld, 16-bit Genesis console, arcade beat'em-up, isometric tactics |
| **24** | refined handhelds + early modern indie chunky | GBA refined handheld, modern indie chunky, Western RPG / post-apocalyptic, DOS / VGA adventure, Japanese PC-98 |
| **32** | arcade fighters, modern indie painterly, atmospheric color-rich subjects | arcade 16-bit fighter, late-arcade 2D fighter, modern indie painterly, cyberpunk pixel-art, dark fantasy / soulslike, Diablo-style dark fantasy isometric |
| **48** | HD-2D hybrid, painterly characters with realistic skin / hair gradation | HD-2D hybrid era; any modern character where skin needs 3-4 distinct tones (base / shadow / midtone / highlight) and hair needs 3-4 brown/blonde variations |
| **64** | maximum painterly fidelity, complex multi-material props (shields with wood-grain + metal + cloth + leather all distinct) | rare — only when k=48 visibly loses important color separation; matches Hugo's reference tool's high-fidelity setting |

**Rule of thumb for humans with visible skin:** k=16 is too tight for warm skin to render with a proper base+shadow+highlight separation (skin tones get merged into one centroid, looking pasty or flat). Use **k=32-48 for any human character**. Reserve k=8-16 for non-human subjects (props, monsters, mechs, hardware-constrained-era characters).

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
- Don't put protected proper nouns in the `image_gen` prompt — not character names, not franchise names, not studio names, not game titles, not hardware names. The 6-phase process (Step 1) translates all of them into abstract descriptors before the prompt is sent. Even "not Iron Man" or "no Pokemon logo" negative clauses still trip the IP guardrail — the model never sees the protected name.
- Don't skip Phase 6 preflight. It's the safety net that catches accidentally leaked proper nouns before the prompt reaches `image_gen`.

## When something goes wrong

See `references/failure-modes.md`. Common cases:

- Built-in image generation disconnects before completion → almost always a **preflight failure** (Phase 6 missed something). Check `$CODEX_HOME/generated_images/...` for a newly written image; if a file exists, show it for Step 3 review. If no file exists, return to Phase 6 of Step 1, scrub the prompt for any leaked proper nouns (character names, franchise names, studio names, game titles, hardware names), and retry with a purely abstract description. If it still fails, explain that the built-in image tool is failing and ask before using the imagegen CLI fallback, which requires `OPENAI_API_KEY`.
- Output doesn't match the user's mental style target → return to Phase 3 and tune the abstract descriptors (era / palette family / silhouette / mood). If the user is asking for a very specific look, encourage them to attach a reference image — that's the highest-fidelity match (and goes through the image-of branch of Phase 2 if the reference depicts protected IP).
- Holes in character → never write a custom bg-removal tool; use the imagegen helper at Step 4 with the documented flags.
- Subject color matches the chroma-key → flip Step 1's chroma-key (green ↔ magenta).
- Snapped output too coarse / too fine → override with `--pixel-size N` on the snapper.
- Upscaled output has uneven block widths → expected for non-integer ratios; use `--scale N` for uniform blocks.
- Multiple subjects in frame → re-roll with stricter "single subject" language in the prompt.
- Concept came back as detailed illustration (smooth gradients, fine details) → make sure the universal `Pixel art rendering:` line was included in the imagegen prompt. That line is the prompt-level enforcer.
