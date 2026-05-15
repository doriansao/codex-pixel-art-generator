# Concept Art Prompt Template

Single concept-art generation at 1024×1024 with a **flat solid chroma-key background**.

The agent's primary job here: take the user's natural-language input and **expand it into a rich, specific Subject description** that imagegen can render coherently. The user shouldn't have to prompt-engineer — the agent does that work using its world knowledge.

## Tool call

Use the built-in `image_gen` tool with a single prompt argument. Some Codex hosts do not expose `size`, `quality`, destination-path, or model parameters on the built-in tool; do not pass those as tool arguments unless the live schema explicitly supports them. Include the desired square framing and quality guidance in the prompt text instead.

## Concept-art chroma-key color

Per imagegen-skill docs (see `$CODEX_HOME/skills/.system/imagegen/SKILL.md` → "Transparent image requests"):

- **Default: `#00ff00`** (green) — works for most subjects.
- **Use `#ff00ff`** (magenta) if the subject is itself green-themed (green dragon, slime, grass-warrior, forest druid, Hulk-style character).
- **Avoid `#0000ff`** (blue) for blue subjects.

This bg gets stripped to transparent in Step 4 by the imagegen helper. The user reviews the raw concept (with chroma-key bg) at Step 3.

## Structured prompt (fill in per call)

```text
Use case: stylized-concept
Asset type: 2D video game <character | monster | weapon | item | powerup | prop | vehicle | tile | environment> pixel art
Primary request: <one-line SAFE headline of what's being generated. If the user mentioned protected IP/source names, do NOT copy the raw user request here; write an original sanitized headline with no protected names, no "X-like", no "inspired by X", and no "not X" clauses.>
Input images: <Image 1: user reference (preserve identity / silhouette / costume / key features; transform only the rendering style to pixel art). Do NOT use the reference's background — replace with the chroma-key.> | NONE
Subject: <RICH ENRICHED description — see "Agent's prompt-enrichment job" below>
Pixel art rendering: HAND-DRAWN PIXEL ART. The output must look like it was drawn pixel-by-pixel in a sprite-art editor by a human artist — chibi or compact-sprite proportions, 2-3 tones per color region (base + shadow + optional highlight), 1-pixel dark colored outlines, visible pixel grid where every "pixel" is a solid block of one palette color with crisp 1-pixel-step boundaries — NOT a detailed AI illustration with pixel-art surface treatment. NO anti-aliasing on edges. NO smooth gradient shading. NO sub-pixel detail (no individual fur strands, no fine wrinkles, no thin lines smaller than 1 logical pixel, no glasses frames thinner than 1 logical pixel, no whiskers thinner than 1 logical pixel). Painterly multi-tone shading ONLY if the user explicitly asked for it.
Scene/backdrop: Create the subject on a perfectly flat solid <CHROMA_KEY_HEX> chroma-key background for background removal. The background must be one uniform color with no shadows, gradients, texture, reflections, floor plane, or lighting variation. Keep the subject fully separated from the background with crisp edges and generous padding. Do not use <CHROMA_KEY_HEX> anywhere in the subject. No cast shadow, no contact shadow, no reflection, no watermark, and no text unless explicitly requested.
Constraints: 1024×1024 square output; subject does NOT touch any frame edge (15% margins all sides); ONE subject only (no scenes, no groups, no companions in frame). Characters MAY hold weapons / tools / items / powerups if described or implied by role. Standalone weapons / items / props are rendered alone (no character holding them).
Avoid: scenery, floor, drop shadow, environment around character, MULTIPLE SUBJECTS, additional characters, companion pets, crowd, blurry, low-detail, generic AI-art look, AI pixel art aesthetic, HD pixel art, detailed AI illustration with pixel-art surface treatment, anti-aliased silhouette, anti-aliased edges, smooth gradient shading, smooth color transitions, sub-pixel detail, fine fur strands, individual hairs, individual whiskers, glasses frames thinner than 1 logical pixel, surface textures finer than the pixel grid, painterly rendering (unless user asked for it), illustration look, soft edges, text, watermark, feet touching bottom of frame, head touching top of frame, subject using <CHROMA_KEY_HEX> in costume / material.
```

## Agent's prompt-enrichment job

The user gives a natural-language input. The agent translates it into a complete safe image-generation prompt via the **6-phase IP-reference process** documented in `SKILL.md` → Step 1. The raw user wording is NEVER pasted directly into the final `image_gen` prompt when it contains protected/source-IP names. The phases in summary:

1. **Detect** any protected/source-IP reference in the user's input (character / franchise / studio / publisher / specific game title, or recognizable IP visible in an attached reference image) plus any allowed hardware / era / genre style tokens.
2. **Classify** the role: exact / like / image-of / style-anchor / era-only.
3. **Extract** the 8 abstract design dimensions (asset type, body shape + silhouette, palette, distinctive motifs, emotional tone, era / hardware, gameplay role, camera / pose) using `references/visual-vocabulary.md`.
4. **Transform** identity-bearing traits for HIGH-risk references (silhouette / palette / signature symbols / named powers / costume layout) so the output is clearly original.
5. **Write** the complete final structured prompt using allowed hardware / era / genre tokens plus concrete visual dimensions — no protected identity / source-IP names appear anywhere in the prompt, including `Primary request`, `Input images`, `Subject`, `Constraints`, and `Avoid`.
6. **Preflight** scan the complete prompt text before calling `image_gen`: confirm no leaked protected names, no "X-like", "inspired by X", or "not X" clauses, no protected semantic lookalike cluster, correct handling of any reference image, and that HIGH-risk references actually got transformed.

Additionally, while writing the `Subject:` line:

- **Preserve specifics the user mentioned** — don't override the user's choices. If they said "red sneakers", keep "red sneakers", don't generalize to "athletic shoes".
- **Don't invent things the user didn't ask for** — no extra companions, no random scenery, no over-specific lore (e.g., don't add a fantasy backstory to a "knight" request).
- **Expand with visual specificity** using world knowledge:
  - For characters: age / build, hair (style + color), eye color, signature facial feature, clothing pieces with materials and colors, accessories, pose, expression, anything held in hands.
  - For weapons / items: shape, materials (steel / wood / gem / leather), color palette, ornamentation, perspective (3/4 for weapons, front-facing for symmetric items).
  - For monsters: silhouette type, dominant colors, distinctive features (horns / wings / tail / eyes).

Pick a chroma-key color (`#00ff00` default, `#ff00ff` for green-themed subjects, `#FFFF00` yellow if the subject is both green AND magenta-themed) and substitute into `<CHROMA_KEY_HEX>`.

## Translation examples

### Example 1: vague prompt — no IP, agent enriches with abstract defaults

**User:** "a knight"

**Phase 1 (Detect):** no protected/source-IP names.
**Phase 2 (Classify):** N/A.
**Phase 3 (Extract):** character / heroic 1:6 build, plate armor silhouette / SNES vibrant fantasy palette / heraldic motif on breastplate / heroic-action tone / 16-bit JRPG era / JRPG protagonist role / front 3/4 idle stance.
**Phases 4-6:** no transformation needed; preflight clean.

**Subject line:**
> A heroic medieval European knight in full plate armor — polished steel chestplate, pauldrons, gauntlets, and sabatons; visored helm with a single feather crest; longsword held at the side, point-down; standing in a calm ready stance; emblem on the breastplate is a simple geometric heraldic shape (cross or star or lion); armored boots. Modern indie chunky pixel art aesthetic — 24-40 colors per sprite, 2-3 tones per region with selective bright rim highlights, 1-pixel dark colored outlines (deep brown / deep blue), chibi-to-semi-chibi proportions, warm earthy fantasy palette, hand-drawn intent with compact readable silhouette.

### Example 2: mood hint — agent picks abstract era + palette from visual-vocabulary.md

**User:** "a cyberpunk hacker girl with neon hair"

**Phase 1 (Detect):** no protected/source-IP names.
**Phase 2 (Classify):** N/A.
**Phase 3 (Extract):** character / adult anime 1:6 build, slim / cyberpunk neon-on-dark palette / neon hair + tech-glow trim motif / cyberpunk-urban-night tone / cyberpunk pixel-art era / cyberpunk hacker role / front 3/4 angle.
**Phases 4-6:** no transformation needed; preflight clean.

**Subject line:**
> A young woman cyberpunk hacker — short asymmetric undercut with neon-magenta and electric-cyan highlights, dark roots; visor-style smart glasses reflecting blue-pink neon; black leather jacket with cyan tech-glow trim and small circuit-pattern decals; cargo pants with magenta utility straps; chunky combat boots; one hand holding a small handheld device with a glowing green screen; calm focused expression; standing in a slight side-3/4 angle. Cyberpunk pixel-art aesthetic — 32-48 colors per sprite with neon accents on dark backgrounds; 3-4 tones per region with strong rim lighting from cyan/pink sources, painterly transitions on the face; 1-pixel deep-magenta / deep-blue outlines; anime-influenced adult proportions; hot pink / cyan / magenta / electric blue on near-black and deep purple.

### Example 3: standalone item — agent describes material / form / perspective

**User:** "a magic sword"

**Phase 1 (Detect):** no protected/source-IP names.
**Phase 2 (Classify):** N/A.
**Phase 3 (Extract):** weapon / vertical orientation / SNES vibrant fantasy palette with cool blue glow / sapphire-pommel + rune motif / regal-mystical tone / 16-bit JRPG era / JRPG item icon role / pure vertical front-facing.
**Phases 4-6:** no transformation needed; preflight clean.

**Subject line:**
> An ornate magic longsword — straight double-edged steel blade with a faint blue luminescent rune etched down the fuller; ornate gold-and-silver crossguard with elegant filigree; deep blue leather-wrapped grip; pommel set with a single round sapphire that emits a soft glow. Vertical orientation, point-up, displayed as a standalone item with no character holding it. 16-bit JRPG item-icon aesthetic — ~16-24 colors, 2-3 tones per region with selective dithering on the blade gradient, 1-pixel dark-blue outlines, vibrant fantasy palette.

### Example 4: HIGH-risk text reference — agent runs the full 6-phase process

**User:** "an [extremely-famous-superhero]-like character for a beat'em-up"

(Filled-in example assuming the user named a recognizable armored-techno-hero from a major comics franchise — the process is identical for any such reference.)

**Phase 1 (Detect):** one protected/source-IP name — the named superhero. Also implicit: the publisher / franchise.

**Phase 2 (Classify):** `like` (HIGH-risk). The user is asking for an "X-like" character, not X exactly. Phase 4 is mandatory.

**Phase 3 (Extract abstract dimensions):**
1. Asset type: character.
2. Body shape + silhouette: heroic 1:7 adult build, muscular, armored bulky outline.
3. Palette family: bright cartoon primary with metallic accents — red + gold + steel.
4. Distinctive motifs: chest power core, segmented plate armor, narrow visor on helmet, energy-glow palm.
5. Emotional tone: heroic / action.
6. Era / hardware: arcade golden-age beat'em-up (1989-95) — 48-80 px tall character, 16-32 colors, bold 1-pixel black outlines, 2-3 tones per region.
7. Gameplay role: beat'em-up brawler.
8. Camera / pose: front 3/4 idle fighting stance.

**Phase 4 (Transform identity-bearing traits):** pull 3 of the 5 levers:
- **Palette shift**: deep crimson + brushed brass + dark gunmetal + cyan energy (instead of bright red + bright gold).
- **Costume layout altered**: asymmetric breastplate (one shoulder bulkier than the other), triangular chest power core (not circular), rectangular oversized gauntlets, narrow cyan visor on a sharp angular helmet (not rounded faceplate).
- **Named powers → generic effects**: "energy palm glow" / "energy lines along armor seams" (no franchise-specific weapon names, no logos, no insignia).

**Phase 5 (Write final prompt):**

**Primary request line:**
> Original armored techno-brawler hero for a side-scrolling arcade beat'em-up.

**Subject line:**
> An original armored techno-brawler hero for a side-scrolling beat'em-up game — athletic adult build with chunky arcade proportions, oversized rectangular gauntlets, heavy armored boots, compact asymmetrical torso armor (one shoulder pauldron bulkier than the other), and a sharp angular helmet with a narrow cyan visor. Armor palette: deep crimson plates, brushed brass shoulder and knee guards, dark gunmetal joints, cyan energy lines along the seams, and a triangular chest power core set into the breastplate. Pose: 3/4 front-facing idle fighting stance, feet planted wide, one armored fist raised near the chest and the other pulled back with a subtle cyan energy glow in the palm. Arcade golden-age beat'em-up aesthetic — 48-80 px tall character, 16-32 colors per sprite, 2-3 tones per region with selective bright highlight pixels, bold 1-pixel solid black outlines, comic-book-on-pixels action-figure feel.

**Phase 6 (Preflight):**
- Copied protected/source-IP names anywhere in the complete prompt? None.
- "X-like" / "inspired by X" / "not X" clauses anywhere in the complete prompt? None — the prompt is purely positive abstract description. ✓
- Identity-preservation on protected refs? N/A (no image). ✓
- Identity-bearing traits transformed? Palette shifted (crimson + brass + gunmetal instead of bright red + bright gold), costume layout altered (asymmetric, triangular core, narrow visor), powers genericized. 3 levers pulled. ✓

Prompt is safe to send.

### Example 5: reference image attached (ORIGINAL subject) — preserve identity, transform rendering style

**User:** attaches a photo / illustration of an ORIGINAL character (their own art, OC, public-domain artwork, or a photo of a real person who consented) + "in pixel art"

**Phase 1 (Detect):** no protected/source-IP names in the image (it's the user's own / public-domain / OC art).
**Phase 2 (Classify):** original reference — bypasses Phases 2-4 of the IP-reference branch. Uses Variation 3 ("preserve identity, transform rendering style").

**`Input images:` line:**
> Image 1: user reference (preserve the subject's identity, silhouette, costume, posture, and key features; transform only the rendering style to pixel art). Do NOT use the reference's background — replace with the `#00ff00` chroma-key.

**`Subject:` line:** the agent describes what's in the reference image so imagegen has both the image AND a text description (more robust):
> The subject from Image 1: [agent describes what's visible — a young woman with auburn hair, wearing a green tunic and brown trousers, holding a wooden staff]. Preserve all identifying features; render in modern indie chunky pixel art aesthetic (24-40 colors per sprite, 2-3 tones per region, 1-pixel dark colored outlines, ~48 px tall sprite feel).

### Example 5b: reference image of PROTECTED IP — auto-translate via the 6-phase process, don't stall

**User:** attaches a screenshot of a recognizable protected character + "make this pixel art"

**Phase 1 (Detect):** the image depicts protected IP (recognizable character).
**Phase 2 (Classify):** `image-of` (HIGH-risk). The image is NOT sent to `image_gen` — the agent reads visual traits from it internally and translates to abstract terms.
**Phases 3-4:** extract the 8 abstract dimensions from the image, then transform identity-bearing traits (silhouette / palette / signature symbols / named powers / costume layout) so the output is clearly original.
**Phase 5:** write the Subject line using only abstract dimensions.
**Phase 6:** preflight clean — `Input images:` line is absent (check #3); no copied protected/source-IP names; identity transformed.

**`Input images:` line:** `NONE` (the image is NOT passed to `image_gen`).

**`Subject:` line:** filled in with abstract dimensions + transformed traits, just like Example 4.

**Don't stall.** The skill's contract is "generate by default." Auto-translate and flag the translation transparently in the Step 3 user-review message: *"Your reference depicts a recognizable character — I generated an original version inspired by its visual traits. Let me know if you want a different translation or want to attach a different reference."* The user accepts / modifies / rejects via the normal review flow.

### Example 6: environment tile — separate category

**User:** "grass tile for a top-down rpg"

**Phase 1 (Detect):** no protected/source-IP names.
**Phase 2 (Classify):** N/A.
**Phase 3 (Extract):** environment tile / pure top-down view / warm-earthy cottagecore palette / grass-blade motif / cute-friendly tone / modern indie chunky era / top-down action-RPG role / pure top-down camera.

**Subject line:**
> A single 32×32 px seamlessly-tileable grass tile for a top-down 2D RPG. Bright green grass with occasional darker-green tufts and a few yellow-tipped grass blades, viewed straight-down. Tile must be seamlessly tileable — left edge matches right edge, top edge matches bottom edge, no obvious center focal point. Modern indie chunky pixel art tile aesthetic — 16-24 colors per tile, 2-3 tones per grass cluster, no dark outlines (tile-internal), warm earthy palette consistent across the tile-set.

## What NOT to do in enrichment

- **Don't override the user's explicit choices.** If they said "young knight", don't make it elderly.
- **Don't invent extra characters / companions.** One subject only.
- **Don't add scenery / background details** beyond the chroma-key bg.
- **Don't add lore or backstory** the user didn't ask for.
- **Don't include protected identity / source-IP names anywhere in the complete prompt.** Character names, franchise names, studio / publisher names, and specific game titles are translated during the 6-phase process. Hardware / era / genre descriptors like NES-style, SNES-era, Game Boy-style, arcade beat'em-up, 16-bit JRPG, and creature-collection RPG are allowed when useful, but they should be paired with concrete descriptors from `visual-vocabulary.md`.
- **Don't leave "X-like", "inspired by X", or "not X" clauses anywhere in the prompt.** Even negative clauses trip the IP guardrail. Phase 6 preflight catches these.
- **Don't keep protected semantic clusters.** If the sanitized prompt still points strongly to one protected subject, transform at least 3 identity levers before calling `image_gen`: species/body taxonomy, silhouette, palette, markings/symbols, power/effect placement, costume/accessory layout, role framing, pose, or camera.
- **Don't skip Phase 4 transformation for HIGH-risk references.** If the description reads like a 1:1 copy with the name removed, it'll still look like the named character — pull more identity-altering levers.
- **Don't over-specify.** If the user is vague, add ENOUGH detail for coherence (color palette, basic clothing, pose) but don't write a paragraph for each body part.

## Settings reminder

- Built-in `image_gen`: pass the complete structured prompt as `prompt`.
- Desired output: square, about 1024×1024, high quality. Express that inside the prompt text.
- The built-in `image_gen` tool may return non-exact sizes (e.g., 1254×1254 instead of 1024×1024) — that's fine. The snapper handles any input dimensions.
