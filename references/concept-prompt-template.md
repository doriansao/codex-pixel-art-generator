# Concept Art Prompt Template

Single concept-art generation at 1024×1024 with a **flat solid chroma-key background**.

The agent's primary job here: take the user's natural-language input and **expand it into a rich, specific Subject description** that imagegen can render coherently. The user shouldn't have to prompt-engineer — the agent does that work using its world knowledge.

## Tool settings

Built-in `image_gen` tool. Settings: `size=1024x1024, quality=high`.

## Concept-art chroma-key color

Per imagegen-skill docs (see `$CODEX_HOME/skills/.system/imagegen/SKILL.md` → "Transparent image requests"):

- **Default: `#00ff00`** (green) — works for most subjects.
- **Use `#ff00ff`** (magenta) if the subject is itself green-themed (green dragon, slime, grass-warrior, forest druid, Hulk-style character).
- **Avoid `#0000ff`** (blue) for blue subjects.

This bg gets stripped to transparent in Step 4 by the imagegen helper. The user reviews the raw concept (with chroma-key bg) at Step 3.

## Structured prompt (fill in per call)

```text
Use case: stylized-concept
Asset type: 2D video game <character | object | item | weapon | powerup | prop | tile | environment> pixel art
Primary request: <one-line headline of what's being generated, paraphrasing the user's request>
Input images: <Image 1: user reference (preserve identity / silhouette / costume / key features; transform only the rendering style to pixel art). Do NOT use the reference's background — replace with the chroma-key.> | NONE
Subject: <RICH ENRICHED description — see "Agent's prompt-enrichment job" below>
Pixel art rendering: HAND-DRAWN PIXEL ART. The output must look like it was drawn pixel-by-pixel in Aseprite / Piskel / PixelOrama by a sprite artist — like Pokemon Crystal overworld sprites, Stardew Valley villagers, Earthbound NES, or Chrono Trigger SNES sprites — NOT a detailed AI illustration with pixel-art surface treatment. NO anti-aliasing on edges. NO smooth gradient shading. NO sub-pixel detail (no individual fur strands, no fine wrinkles, no thin lines smaller than 1 logical pixel, no glasses frames thinner than 1 logical pixel, no whiskers thinner than 1 logical pixel). Each color region uses 2-3 tones maximum (base + shadow + optional highlight); painterly multi-tone shading ONLY if the user explicitly asked for it. Visible pixel grid — every "pixel" is a solid block of one palette color with crisp 1-pixel-step boundaries.
Scene/backdrop: Create the subject on a perfectly flat solid <CHROMA_KEY_HEX> chroma-key background for background removal. The background must be one uniform color with no shadows, gradients, texture, reflections, floor plane, or lighting variation. Keep the subject fully separated from the background with crisp edges and generous padding. Do not use <CHROMA_KEY_HEX> anywhere in the subject. No cast shadow, no contact shadow, no reflection, no watermark, and no text unless explicitly requested.
Constraints: 1024×1024 square output; subject does NOT touch any frame edge (15% margins all sides); ONE subject only (no scenes, no groups, no companions in frame). Characters MAY hold weapons / tools / items / powerups if described or implied by role. Standalone weapons / items / props are rendered alone (no character holding them).
Avoid: scenery, floor, drop shadow, environment around character, MULTIPLE SUBJECTS, additional characters, companion pets, crowd, blurry, low-detail, generic AI-art look, AI pixel art aesthetic, HD pixel art, detailed AI illustration with pixel-art surface treatment, anti-aliased silhouette, anti-aliased edges, smooth gradient shading, smooth color transitions, sub-pixel detail, fine fur strands, individual hairs, individual whiskers, glasses frames thinner than 1 logical pixel, surface textures finer than the pixel grid, painterly rendering (unless user asked for it), illustration look, soft edges, text, watermark, feet touching bottom of frame, head touching top of frame, subject using <CHROMA_KEY_HEX> in costume / material.
```

## Agent's prompt-enrichment job

The user gives a natural-language input. The agent translates it into a rich `Subject:` line by:

1. **Identifying the subject category** — character / weapon / item / monster / vehicle / environment tile.
2. **Expanding with visual specificity** using the agent's world knowledge:
   - For characters: age / build, hair (style + color), eye color, signature facial feature, clothing pieces with materials and colors, accessories, pose, expression, anything held in hands.
   - For weapons / items: shape, materials (steel / wood / gem / leather), color palette, ornamentation, perspective (3/4 for weapons, front-facing for symmetric items).
   - For monsters: silhouette type, dominant colors, distinctive features (horns / wings / tail / eyes).
3. **Preserving any style references the user mentioned VERBATIM** — if the user said "in the style of River City Ransom", that exact phrase goes in the Subject line. If they said "modern indie chunky", check `style-references.md` for 2-4 specific game names and integrate them naturally.
4. **Preserving any specifics the user mentioned** — don't override the user's choices. If they said "red sneakers", keep "red sneakers", don't generalize to "athletic shoes".
5. **NOT inventing things the user didn't ask for** — no extra companions, no random scenery, no over-specific lore (e.g., don't add a fantasy backstory to a "knight" request).

Pick a chroma-key color (`#00ff00` default, `#ff00ff` for green-themed subjects, `#FFFF00` yellow if the subject is both green AND magenta-themed) and substitute into `<CHROMA_KEY_HEX>`.

## Translation examples

### Example 1: vague character — agent enriches with sensible defaults

**User:** "a knight"

**Subject line:**
> A heroic medieval European knight in full plate armor — polished steel chestplate, pauldrons, gauntlets, and sabatons; visored helm with a single feather crest; longsword held at the side, point-down; standing in a calm ready stance; emblem on the breastplate is a simple geometric heraldic shape (cross / star / lion); armored boots. Modern indie chunky pixel art, in the spirit of Stardew Valley villager sprites / Pokemon Crystal overworld / Cave Story.

### Example 2: specific game style — agent uses the game name verbatim

**User:** "kunio from river city ransom"

**Subject line:**
> Kunio, the protagonist of River City Ransom / Downtown Nekketsu Monogatari (Technos, NES, 1989) — short spiky black hair with a small forelock, fierce determined eyes, white sleeveless tank top, blue denim jeans rolled at the cuff, red sneakers, fists clenched at chest height in a ready beat'em-up stance, Technos-NES-era chibi proportions (head is ~1/2 of body height). **Match the original NES sprite's exact silhouette, palette (4-color NES hardware), and color use.** In the style of Kunio-kun / River City Ransom / Downtown Nekketsu Monogatari / Renegade NES (Technos Japan, 1986-89).

### Example 3: mood + style hint — agent picks game refs from style-references.md

**User:** "a cyberpunk hacker girl with neon hair"

**Subject line:**
> A young woman cyberpunk hacker — short asymmetric undercut with neon-magenta and electric-cyan highlights, dark roots; visor-style smart glasses reflecting blue-pink neon; black leather jacket with cyan tech-glow trim and small circuit-pattern decals; cargo pants with magenta utility straps; chunky combat boots; one hand holding a small handheld device with a glowing green screen; calm focused expression; standing in a slight side-3/4 angle. In the style of VA-11 HALL-A: Cyberpunk Bartender Action / The Red Strings Club / 198X — anime-influenced cyberpunk pixel art with neon accents on a dark palette.

### Example 4: standalone item — agent describes material / form / perspective

**User:** "a magic sword"

**Subject line:**
> An ornate magic longsword — straight double-edged steel blade with a faint blue luminescent rune etched down the fuller; ornate gold-and-silver crossguard with elegant filigree; deep blue leather-wrapped grip; pommel set with a single round sapphire that emits a soft glow. Vertical orientation, point-up, displayed as a standalone item with no character holding it. In the style of classic JRPG item icons (Chrono Trigger / FF6 / Secret of Mana).

### Example 5: reference image attached — preserve identity, transform style

**User:** attaches a photo / illustration + "in pixel art"

**`Input images:` line:**
> Image 1: user reference (preserve the subject's identity, silhouette, costume, posture, and key features; transform only the rendering style to pixel art). Do NOT use the reference's background — replace with the `#00ff00` chroma-key.

**`Subject:` line:** the agent describes what's in the reference image so imagegen has both the image AND a text description (more robust):
> The subject from Image 1: [agent describes what's visible — a young woman with auburn hair, wearing a green tunic and brown trousers, holding a wooden staff]. Preserve all identifying features; render in pixel art style at modern indie chunky resolution (~48 px tall sprite feel).

### Example 6: environment tile — separate category

**User:** "grass tile for a top-down rpg"

**Subject line:**
> A single 32×32 px seamlessly-tileable grass tile for a top-down 2D RPG. Bright green grass with occasional darker-green tufts and a few yellow-tipped grass blades, viewed straight-down. Tile must be seamlessly tileable — left edge matches right edge, top edge matches bottom edge, no obvious center focal point. In the style of Stardew Valley grass / Pokemon HGSS overworld grass / Zelda LttP grass.

## What NOT to do in enrichment

- **Don't override the user's explicit choices.** If they said "young knight", don't make it elderly.
- **Don't invent extra characters / companions.** One subject only.
- **Don't add scenery / background details** beyond the chroma-key bg.
- **Don't add lore or backstory** the user didn't ask for.
- **Don't replace style references with generic descriptions.** If the user named a specific game, keep that game name in the prompt — your enrichment supplements, doesn't replace.
- **Don't over-specify.** If the user is vague, add ENOUGH detail for coherence (color palette, basic clothing, pose) but don't write a paragraph for each body part.

## Settings reminder

- `size='1024x1024'`, `quality='high'`.
- The built-in `image_gen` tool may return non-exact sizes (e.g., 1254×1254 instead of 1024×1024) — that's fine. The snapper handles any input dimensions.
