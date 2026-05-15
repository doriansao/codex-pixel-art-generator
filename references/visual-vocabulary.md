# Visual Vocabulary

Quick descriptive reference for the agent during **Phase 3 (extract abstract design dimensions)** of the prompt-enrichment process — see `SKILL.md` → Step 1.

**No IP**: no character names, no franchise names, no studio names, no game titles. Pure descriptive vocabulary organized by era / genre / mood / silhouette / palette. The agent uses this to translate any IP reference (which is detected and stripped in Phase 1) into abstract terms that work in the final `image_gen` prompt without tripping IP guardrails.

The agent uses its world knowledge for anything not covered here.

---

## Era / hardware vocabulary

### 8-bit primitive era (very early consoles)

- 2-4 color sprites per character, no shading, blocky silhouettes, abstract shapes
- 8-16 px tall character, often horizontally stretched
- Single-color regions, no outlines
- Pose: simple side-view stance, minimal animation potential

### 8-bit home computer (early-80s)

- 8-16 color palettes with hardware-specific quirks
- Heavy dithering (signature of the era — used to simulate more colors than the hardware allowed)
- 16-32 px tall character, chunky proportions
- 1-2 tones per region, flat blocks
- Bold dark outlines

### 8-bit NES era

- 3-4 colors per sprite (hardware-constrained), shared bg color
- 16-32 px tall character (small-format protagonists)
- Single tone per region, no per-pixel multi-tone shading
- Iconic readable silhouettes, chibi 1:2 head-to-body proportions
- Bold black outlines or color-against-color region transitions
- Era sub-variants:
  - **Earliest NES (1984-86)**: very minimal, single-tone, abstract silhouettes
  - **Late NES action (1988-92)**: 4-8 colors per sprite, 1-2 tones per region, comic-book energy, dynamic action poses
  - **NES JRPG overworld**: tiny 16-24 px chibi sprite, single-tone, iconic-at-a-glance silhouette, eyes-only face
  - **NES beat'em-up**: 32-48 px chibi with 1:2 head-to-body, flat shading, urban-street setting

### Game Boy DMG (monochrome handheld)

- 4 shades of green-tint or pure grayscale ONLY
- 16-32 px tall character, super-deformed chibi
- 2-3 of the 4 shades per region, flat blocks
- 1-pixel outlines in the darkest shade
- No other colors permitted

### Game Boy Color handheld

- 8-16 colors per sprite, hardware-bright
- 24-40 px tall character, chibi proportions
- 2 tones per region, flat color blocks
- 1-pixel dark colored outlines (often dark green / dark brown)

### 16-bit SNES era

- 16-24 colors per sprite
- 24-48 px tall character for overworld; 80-120 px tall for combat / portrait sprites
- 2-3 tones per region with selective dithering on round forms (hair, armor curves)
- Cute anime-influenced facial features (visible eyes, soft expressions)
- 1-pixel dark outlines, often colored (dark blue / maroon / deep brown) rather than pure black
- Bright vibrant fantasy palette

### 16-bit Genesis-era console

- 16-32 colors per sprite (hardware-constrained)
- 32-48 px tall character
- 2 tones per region with selective highlights, flat color blocks
- 1-pixel solid black outlines
- Snappy "attitude" poses, motion-implying stance
- Slightly deeper / moodier palette than SNES, occasional rim light

### Arcade golden-age beat'em-up (1989-95)

- 16-32 colors per sprite
- 48-80 px tall character (compact arcade range)
- 2-3 tones per region, flat color blocks with selective bright highlight pixels
- Bold 1-pixel solid black outlines
- Either: vibrant primary palette + cartoony-cute big-eyed characters + Saturday-morning energy
- Or: muscular brawler proportions + comic-book-on-pixels feel + action-figure heroic
- Or: gritty urban dark palette + deeper shadows + cinematic mood

### Arcade 16-bit fighter (1991-95)

- 32-48 colors per sprite
- 96-128 px tall character (LARGE for one-on-one readability)
- 2-3 tones per region with strong rim lighting, detailed muscle definition
- Bold 1-pixel outlines
- Realistic-ish muscular adult proportions
- Sharp pixel edges, no anti-aliasing
- Combat-ready dynamic poses

### Late-arcade 2D fighter (1995-2003)

- 48-64 colors per sprite (richer palette than 16-bit fighter)
- 120-160 px tall character (LARGE, more detailed than SF II era)
- 3-4 tones per region with rim lighting, selective dithering on round forms
- 1-pixel colored outlines (deep brown / maroon / indigo, NOT pure black) — softer than earlier fighters
- Anime-influenced detailed features, expressive eyes
- Late-90s polish, flowing hair / clothing

### 32-bit / late-arcade transition

- Richer palette (~64+ colors)
- Larger sprites, more detailed dithering
- More painterly transitions within the pixel grid
- Sharp edges still maintained

### Game Boy Advance refined handheld

- 24-32 colors per sprite
- 40-64 px tall character; 24-40 px for items
- 2-3 tones per region with occasional rim light, very selective dithering
- 1-pixel dark colored outlines (often dark blue or dark purple for refinement)
- Balanced anime-cartoon hybrid features
- Late-handheld polish — refined yet compact

### DOS / Western adventure VGA (1990-95)

- 256-color VGA palette, hand-painted-illustration feel
- 48-80 px tall character; backgrounds at 320×200 resolution
- 3-4 tones per region with painterly blending, occasional dithering for gradients
- Comedic exaggerated proportions, big expressive facial features
- 1-pixel colored outlines (warm brown / deep maroon)

### Japanese PC-98 anime era (1989-95)

- Strict 16 colors per sprite (PC-98 VRAM constraint)
- 48-80 px tall character, often vertical portrait orientation
- Heavy dithering for gradient simulation
- Anime features with bright eyes, pastels and pinks common
- 1-pixel dark colored outlines

### Western RPG / post-apocalyptic (late-80s to early-2000s)

- 24-32 colors per sprite, desaturated post-apocalyptic palette
- 40-64 px tall character; 24-40 px for items
- 2-3 tones per region with selective dithering for weathering
- 1-pixel dark colored outlines (deep brown / umber, NOT pure black)
- Realistic-grim adult proportions, weathered features
- Top-down 3/4 isometric viewing angle
- Rust / dust / sun-bleached cloth / gunmetal / sickly-green-radiation palette

### Modern indie chunky (2010s+)

- 24-40 colors per sprite
- 24-48 px tall character; 12-24 for items
- 2-3 tones per region, flat blocks with selective bright rim highlights
- 1-pixel dark colored outlines, often dark brown / dark blue / dark purple (softer than pure black)
- Chibi to semi-chibi proportions, hand-drawn intent
- Compact readable silhouettes
- Warm-earthy or atmospheric palette depending on genre

### Modern indie painterly (2010s+)

- 32-64 colors per sprite, richer painterly palette
- 120-160 px tall character
- Multi-tone shading achieved via DITHERING (not smooth gradients), painterly within the pixel grid
- 1-pixel colored outlines
- Realistic-heroic proportions
- Atmospheric mood with surface textures rendered at pixel level
- Deep saturated shadows, warm/golden highlights

### HD-2D hybrid era

- 32-48 colors per sprite, warm rich palette
- 64-96 px tall character
- 3-4 tones per region via dithering, painterly highlights
- 1-pixel dark colored outlines (warm brown / deep indigo)
- Chibi JRPG proportions (head ~1/3 of body)
- Designed to sit in a 3D world with depth-of-field blur

### Pico-8 fantasy-console aesthetic

- Strict fixed 16-color palette (specific 16 colors only)
- 8-16 px tall character (very tiny)
- Single tone per region, occasionally 2 tones using the palette's natural light/dark pairs
- No dithering, no anti-aliasing
- Chunky retro feel, 1-2-heads-tall chibi

### Roguelike top-down pixel

- 12-20 colors per sprite, often desaturated earth tones
- 12-24 px tall character (very compact for tile density)
- 1-2 tones per region (mostly flat — at this size there isn't room for shading)
- 1-pixel solid dark outline (strong silhouette at small size)
- Top-down 3/4 perspective

### Cyberpunk pixel-art era

- 32-48 colors per sprite, neon accents on dark backgrounds
- 48-80 px tall character; 120-160 px for portrait pixel art; 24-48 px for items / gadgets
- 3-4 tones per region with strong rim lighting (neon back-light from cyan/pink sources), painterly transitions on faces
- 1-pixel dark colored outlines (deep magenta / deep blue)
- Anime-influenced adult proportions
- Hot pink / cyan / magenta / electric blue / lime neon accents against near-black / deep purple / deep teal backgrounds

### Dark fantasy / soulslike pixel

- 32-48 colors per sprite, desaturated grim palette
- 64-96 px tall character; 32-64 px for weapons / items
- 3-4 tones per region with painterly shadows, heavy dithering on cloth / stone
- 1-pixel colored outlines (deep charcoal / deep maroon)
- Realistic-grim gaunt or armored adult proportions
- Deep maroon / dried-blood crimson / charcoal / cold stone gray / dim gold accent palette
- Religious-horror Spanish-Baroque oppressive atmosphere

### Pixel horror lo-fi

- Strict 4-8 colors per sprite, desaturated muted reds / browns / grays / sickly greens
- 16-32 px tall character (deliberately small / low-res for unsettling effect)
- Flat single tone per region, occasional 2-tone with shadow
- 1-pixel dark outlines, sometimes broken / dithered for unsettling effect
- Realistic-but-degraded proportions, blurry or missing or asymmetric features
- 1-bit black-and-white also valid for ultra-minimal horror

### Isometric tactics / strategy pixel

- 16-24 colors per sprite
- 32-48 px tall character; 16-32 px for items / tiles
- 2-3 tones per region with selective highlights, consistent light source from upper-left
- 1-pixel dark colored outlines
- Chibi-anime proportions (head ~1/3 of body, super-deformed)
- 3/4 isometric viewing angle — character renders as if standing on an isometric grid

### Diablo-style dark fantasy isometric

- 32-40 colors per sprite, cold-stone / deep-brown / deep-red / dim-gold dark-fantasy palette
- 40-64 px tall character (foreshortened by isometric angle)
- 2-3 tones per region with selective dithering on round forms
- 1-pixel outlines often colored (deep brown / deep navy, NOT pure black)
- Realistic-grim adult proportions, gaunt or armored
- Dungeon-crawl somber atmospheric mood
- 3/4 isometric perspective with elevated camera

---

## Genre / role vocabulary

- **Beat'em-up brawler**: brawler stance with fists clenched, ready combat pose, urban street fashion or martial-arts attire, comic-book action energy
- **JRPG protagonist**: heroic standing pose, fantasy attire (armor / cloak / robe), held weapon (sword / staff / bow), cute anime features
- **Platformer mascot**: running / jumping animation potential, energetic stance, colorful primary palette, anthropomorphic creature or cartoon hero
- **Fighter (1v1)**: combat stance, muscular adult proportions, exotic costume, hero or villain archetype, foot-planted ready
- **Action-platformer hero**: heroic action pose, weapon or signature ability visible (sword / gun / whip), dynamic athletic build
- **Shmup spaceship / mecha**: small compact sprite, top-down or side-view, spaceship / mecha / aircraft, energy weapons visible
- **Monster-catching RPG creature**: cute compact creature, expressive eyes, paired short limbs, signature elemental motif (water / fire / electric / grass / etc.), friendly stance
- **Tactical RPG unit**: 3/4 isometric view, chibi-anime proportions, weapon held, fantasy class costume
- **Top-down action-adventure hero**: 3/4 perspective, chibi 1:3 proportions, simple readable silhouette, sword / shield
- **Post-apocalyptic survivor**: weathered gritty attire, gas-mask / leather / improvised armor, gaunt features, hardened look
- **Cyberpunk hacker / netrunner**: anime adult proportions, neon-accent palette on dark, holographic / tech-glow details, urban setting, handheld device
- **Dark fantasy hunter / paladin**: gaunt grim adult, deep maroon / dried-blood / charcoal palette, religious-iconographic ornament
- **Cozy farm villager**: warm earthy attire, chibi proportions, friendly expression, gardening / cottage props
- **Roguelike adventurer**: very compact silhouette, top-down readable, simple class-indicating accessory (wand / sword / dagger / spell focus)
- **Mech / robot pilot**: large mechanical body, plate-armor segments, weapon mounts, mechanical joints, no organic features

---

## Mood / tone vocabulary

- **Cute / friendly / cottagecore**: warm earthy tones, chibi proportions, friendly expression, soft palette, simple readable forms
- **Heroic / action / adventure**: dynamic ready pose, vibrant primaries, confident expression, weapon at side or raised
- **Dark / grim / serious**: desaturated grim palette, gaunt features, serious or anguished expression, somber atmosphere
- **Cyberpunk / neon / urban-night**: hot pink / cyan / magenta neon on dark, holographic accents, tech-glow trim
- **Mysterious / arcane / occult**: dark robes, glowing accents, hooded silhouette, mystical symbolism
- **Playful / mascot / cartoon**: round shapes, big expressive eyes, bright primaries, simple silhouette
- **Comedy / exaggerated**: cartoonish big features (huge eyes / nose / mouth), exaggerated proportions for humor
- **Mystical / dreamy / surreal**: pastel palette, soft edges (within pixel limits), unusual color combinations
- **Gritty / weathered / post-apocalyptic**: rust / dust / sun-bleached tones, weathering accents, broken or improvised gear
- **Regal / royal / heroic**: gold accents, rich purples / deep blues, ornate filigree, dignified pose

---

## Body / silhouette vocabulary

- **Chibi 1:1 head-body** (1 head tall): extreme super-deformation, head as big as the body itself
- **Chibi 1:2 head-body** (2 heads tall): head as tall as body, super-deformed cute
- **Chibi 1:3 head-body** (3 heads tall): head ~1/3 of body, cute compact (common for SNES JRPG overworld)
- **Semi-chibi 1:4 head-body** (4 heads tall): cartoony but more adult-proportioned
- **Adult anime 1:6 head-body** (6 heads tall): stylized adult, slim
- **Realistic-heroic 1:7 head-body** (7 heads tall): close to real anatomy, muscular adult
- **Compact stocky**: wider than tall, broad-shouldered, sturdy
- **Slim tall**: elongated thin, slender adult
- **Mech / robot vertical**: rectangular or trapezoidal silhouette, large legs / small upper body, asymmetric weapon mounts
- **Creature quadruped**: low-slung body, wider than tall, simple legs
- **Bird / winged biped**: vertical upper body with wing volume, slim limbs
- **Compact creature**: round egg-shape with minimal limbs (small-mammal archetype)

---

## Palette family vocabulary

- **NES-constrained primary**: red / blue / green / yellow / brown / orange / pink / cyan, ~4-8 colors total per sprite
- **Game Boy DMG 4-shade**: 4 shades of a single hue (green-tinted or grayscale)
- **SNES vibrant fantasy**: bright reds / blues / greens / yellows with selective bright accents, ~16-24 colors
- **Genesis moody 16-color**: deeper / atmospheric / 16-color hardware palette, darker night-time tones
- **Warm earthy cottagecore**: cream / tan / brown / dark green / sky blue / warm muted accents
- **Cool moody industrial**: deep blue / cyan / dark grey / silver / occasional warm accent
- **Cyberpunk neon-on-dark**: hot pink / electric cyan / magenta / deep purple / near-black / lime accents
- **Dark fantasy grim**: deep maroon / dried crimson / charcoal / dim gold / cold stone gray
- **Bright cartoon primary**: pure red / pure blue / yellow / green / orange, saturated primaries and secondaries
- **Anime fantasy pastel**: pastels with bright accents (lavender / mint / coral / sky-blue / pale pink)
- **Post-apocalyptic gritty**: rust orange / dust khaki / olive drab / sun-bleached white / sickly radiation green
- **Painterly modern indie**: rich palette ~32-64 colors with deep saturated shadows and warm/golden highlights
- **Painted VGA adventure**: 256-color hand-painted illustration palette, warm earth tones with sky blues and fabric reds

---

## Camera / pose vocabulary

- **Front 3/4 view**: subject facing slightly toward camera-left or camera-right, standard sprite-art pose
- **Side view (profile)**: pure side-on, common for platformers and beat'em-ups
- **Top-down (3/4 elevated)**: viewed from above at angle, common for action-RPG and tile-based games
- **Pure top-down**: viewed straight down, common for tiles and very-zoomed-out games
- **Isometric 3/4**: viewed from elevated 3/4 angle with isometric foreshortening
- **Idle stance**: feet planted, weapon at side or relaxed, looking forward, calm
- **Ready stance**: feet shoulder-width, weapon up or at chest, alert posture
- **Action pose**: dynamic mid-movement (running / jumping / attacking)
- **Combat stance**: feet wide, fists / weapon up, ready to fight
- **Crouched / sneaking**: low to ground, weapon ready
- **Sitting / resting**: low energy, often used for NPC sprites
- **Floating / hovering**: for spirits / orbs / floating creatures, no ground contact
