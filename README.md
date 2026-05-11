# Pixel Art Generator

A [Codex CLI](https://github.com/openai/codex) skill that generates beautiful 2D pixel art for video games and animations.

**Repo:** `codex-pixel-art-generator`
**Skill name (registered):** `pixel-art-generator`
**Author:** Dorian Butron

## What it does

Takes a natural-language prompt (and optionally a reference image) and produces three transparent-background PNGs per asset:

1. **`<name>_concept.png`** — clean concept art from `image_gen` + bg removal (~1024×1024 or 1254×1254). The artist-facing reference.
2. **`<name>_snapped.png`** — Sprite Fusion-style pixel-snapped sprite at native logical resolution (e.g., 114×114). Every pixel in the file IS one logical pixel. **The canonical game-engine asset.**
3. **`<name>_upscaled.png`** — NEAREST upscale of the snapped image, fit into a 1024×1024 canvas with aspect ratio preserved + transparent padding. For preview / marketing / display.

Works for **characters** (warriors, mages, NPCs, monsters), **weapons & equipment**, **powerups & items**, **props**, and **environment tiles**.

## Pipeline

```
Step 1: Prompt enrichment      Agent expands user's NL input → rich imagegen prompt
Step 2: Concept generation     image_gen → tmp/imagegen/<name>_concept_raw.png (chroma-key bg)
Step 3: USER REVIEW             Show raw concept → accept / modify / regenerate
Step 4: Strip bg (after accept) imagegen helper → concept/<name>_concept.png (transparent)
Step 5: Pixel snap              snap_pixels.py → concept/<name>_snapped.png (small native, transparent)
Step 6: Upscale                 upscale.py → concept/<name>_upscaled.png (1024×1024, transparent)
```

The skill is mechanical — the snapper + upscaler convert any input into clean pixel art deterministically. The agent is the creative layer: it reads the user's casual prompt and translates it into a rich, imagegen-friendly Subject line using world knowledge.

## Installation

### Prerequisites

- [Codex CLI](https://github.com/openai/codex) (modern version with the `.system` skills bundle)
- Python 3.10+
- The `imagegen` system skill at `$CODEX_HOME/skills/.system/imagegen/` (bundled with Codex)

### Option A — Install via `$skill-installer` (recommended)

Open an active Codex chat session and invoke the bundled installer skill:

```
$skill-installer install https://github.com/doriansao/codex-pixel-art-generator
```

The `$` is Codex's in-session skill-invocation marker (typed inside the Codex chat, not in a shell). The `skill-installer` skill is a built-in `.system` skill auto-installed with modern Codex.

It clones the repo into `$CODEX_HOME/skills/pixel-art-generator/` (using the `name:` field from `SKILL.md`'s frontmatter as the folder name). The skill is picked up by Codex automatically. If it doesn't appear, restart Codex.

See [OpenAI's skills catalog](https://github.com/openai/skills) and [Codex skills docs](https://developers.openai.com/codex/skills) for more on the installer.

### Option B — Manual `git clone`

If you prefer the explicit path or you're on an agent host that doesn't have `$skill-installer`:

```bash
git clone https://github.com/doriansao/codex-pixel-art-generator.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/pixel-art-generator"
```

Windows PowerShell:

```powershell
$skills = if ($env:CODEX_HOME) { "$env:CODEX_HOME\skills" } else { "$HOME\.codex\skills" }
git clone https://github.com/doriansao/codex-pixel-art-generator.git "$skills\pixel-art-generator"
```

The folder name in `$CODEX_HOME/skills/` must be `pixel-art-generator` (matching `SKILL.md`'s `name:` field), not `codex-pixel-art-generator` (the repo name).

### Install Python dependencies

The skill needs Pillow and numpy. Install once globally:

```bash
pip install "Pillow>=10.0" "numpy>=1.24"
```

Or with `uv`:

```bash
uv pip install "Pillow>=10.0" "numpy>=1.24"
```

### Updating

To pull the latest changes:

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills/pixel-art-generator"
git pull
```

Restart Codex if the updates don't appear.

## Usage

Invoke the skill in your agent host with a natural-language prompt:

```
Generate a pixel art knight with full plate armor and a longsword.
```

Or with a style reference:

```
Generate a pixel art character in the style of River City Ransom (NES) —
a young brawler with spiky black hair, white tank top, blue jeans, red sneakers.
```

Or attach a reference image:

```
Convert this character to pixel art.
[attached image]
```

The agent walks through the 6-step pipeline, showing you the raw concept at Step 3 for accept/modify/reject before running bg removal and the snapper.

## How it works

### Sprite Fusion algorithm

The snapper is a Python port of [Hugo Duprez's spritefusion-pixel-snapper](https://github.com/Hugo-Dz/spritefusion-pixel-snapper). The key operations:

1. **K-means++ quantize the full-resolution input** to N colors (default 16). Clusters colors by density — soft fringe noise around each rendered color collapses into the dominant centroid.
2. **Detect grid via gradient profiles.** Compute X/Y gradient profiles, find peaks, estimate step size.
3. **Walk + stabilize** to find non-uniform cuts aligned with actual color transitions in the image (not uniform N×N blocks — that misaligns with the model's natural pixel grid).
4. **Mode-per-cell.** Each output pixel is the most common RGBA value in its source cell.

This produces a small native-resolution sprite (e.g., 114×114) where every pixel in the file IS one logical pixel of the rendered drawing.

### Upscaler (aspect-preserving NEAREST)

The upscaler does **canvas-fit** by default: finds the largest integer scale factor that fits the input inside the target canvas (default 1024×1024), NEAREST-upscales by that factor, and centers on a transparent canvas. Never distorts the aspect ratio.

For perfectly uniform block widths, pass `--scale N` for an integer scale factor (output = `input × N`, no canvas).

### Background removal

Uses the `imagegen` system skill's bundled `remove_chroma_key.py` helper (proper alpha matting + despill). Color-distance matching at any tolerance > 0 punches holes in character pixels close to the bg color; the imagegen helper's soft matte preserves them via partial alpha.

## Project structure

```
codex-pixel-art-generator/                # repo name on GitHub
├── SKILL.md                              # main skill definition (name: pixel-art-generator)
├── README.md                             # this file
├── LICENSE                               # MIT
├── .gitignore
├── agents/
│   └── openai.yaml                       # agent metadata (display name, dependencies)
├── scripts/
│   ├── snap_pixels.py                    # Sprite Fusion pixel snapper (k-means + walk + mode)
│   └── upscale.py                        # aspect-preserving NEAREST upscaler
└── references/
    ├── concept-prompt-template.md        # imagegen prompt template + agent enrichment examples
    ├── style-references.md               # game-name reference list by era / mood
    ├── imagegen-sizes.md                 # size + quality settings for imagegen
    └── failure-modes.md                  # symptom → cause → fix table
```

After installation, the folder is at `$CODEX_HOME/skills/pixel-art-generator/` (using the registered skill name from `SKILL.md`).

## Standalone use (without the agent)

You can invoke the Python scripts directly on any image:

```bash
# Snap an existing transparent-bg pixel-art-style image to a clean grid
python scripts/snap_pixels.py \
    --input path/to/your_concept.png \
    --output path/to/your_snapped.png \
    --colors 16

# Upscale a small pixel-art sprite to a display canvas
python scripts/upscale.py \
    --input path/to/your_snapped.png \
    --output path/to/your_upscaled.png \
    --size 1024 1024
```

Run with `--help` for full CLI options.

## Credits

- **Sprite Fusion algorithm** by [Hugo Duprez](https://github.com/Hugo-Dz/spritefusion-pixel-snapper) (MIT) — the snapper is a Python reimplementation of his Rust+WASM tool.
- **`imagegen` skill** (system-bundled) for the `image_gen` tool integration and the alpha-matting bg-removal helper.

## License

MIT — see [LICENSE](LICENSE).

## Author

**Dorian Butron** — built this skill, tested it across NES, SNES, modern indie, cyberpunk, and post-apocalyptic styles.
