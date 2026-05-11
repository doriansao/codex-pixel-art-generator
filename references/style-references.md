# Style References

Quick reference list of game names by era / mood. The agent uses these to **add specific named-game references** to the imagegen prompt when the user gives a directional style hint (or to provide era-appropriate defaults when the user is vague).

This is NOT a curated anchor library with prescriptive sprite-size / palette / shading parameters — those are dead weight. The agent's job is to interpret the user's intent and pick 2-4 relevant game names to plug into the prompt as style references.

The model's training data has each of these games specifically — naming them gives the model a precise visual target. Saying "in the style of Stardew Valley" anchors the model FAR better than "modern chunky pixel art with chibi proportions and a warm earthy palette."

## How the agent uses this file

- **User gives a directional style hint** ("16-bit JRPG", "cyberpunk", "GBA Castlevania") → agent picks 2-4 specific game names from the relevant section and integrates them verbatim into the prompt's Subject line.
- **User mentions a specific game** ("River City Ransom style") → agent uses that game name plus 1-2 sibling references from the same section for reinforcement.
- **User is completely vague** → agent defaults to "modern indie chunky pixel art (Stardew Valley / Cave Story / Pokemon Crystal overworld feel)".

The agent picks references that **match the user's intent** — don't pile on unrelated games.

---

## Eras / hardware

### 8-bit / pre-NES (1977-84)

- **Atari 2600**: Adventure, Pitfall!, Yars' Revenge, Space Invaders (2600 port). Ultra-primitive 2-4 colors per sprite, blocky silhouettes.
- **ColecoVision / Intellivision**: Donkey Kong (ColecoVision), Burgertime. Slightly more refined than 2600.

### 8-bit home computers (1982-90)

- **Commodore 64**: The Last Ninja, Wizball, Turrican, Mayhem in Monsterland, Defender of the Crown. Signature 16-color C64 fixed palette with dither-shading.
- **ZX Spectrum**: Jet Set Willy, Manic Miner, Skool Daze, R-Type. Attribute-clash 8-color palette.
- **Amstrad CPC**: similar era to Spectrum, slightly different palette.
- **MSX**: Metal Gear (MSX), Vampire Killer (Castlevania MSX origin).

### Amiga 16-bit (1985-92)

- **Amiga OCS/ECS**: Shadow of the Beast, Lionheart, Turrican II, Wings of Death, Lemmings, Eye of the Beholder (Amiga port). Heavy dithering, sword-and-sorcery / sci-fi mood.

### Classic NES Nintendo first-party (1985-92)

- **Mario**: Super Mario Bros. 1-3, Super Mario World (SNES, sister style)
- **Zelda**: The Legend of Zelda (NES), Zelda II
- **Metroid**: Metroid (NES), Kid Icarus
- **Other Nintendo NES**: Ice Climber, Balloon Fight, Excitebike, Punch-Out!!
- Hallmark: iconic chibi silhouettes at 16-24 px, 3-color sprites per region.

### NES action-platformer (1987-93)

- **Capcom NES action**: Mega Man 1-6, Duck Tales, Chip 'n Dale Rescue Rangers, Little Nemo: The Dream Master
- **Konami NES**: Castlevania 1-3, Contra, Super C, TMNT (NES), TMNT II: Arcade Game (NES port), TMNT III, Tiny Toon Adventures
- **Tecmo / Sunsoft**: Ninja Gaiden 1-3 (NES), Batman (Sunsoft NES), Journey to Silius
- **Rare**: Battletoads, Battletoads & Double Dragon

### NES beat'em-up / brawler (1986-93)

- **Technos**: Kunio-kun, Nekketsu Kakutou Densetsu, River City Ransom (Downtown Nekketsu Monogatari), Renegade, Double Dragon (NES)
- **Other**: Bad Dudes (NES), Crash 'n the Boys: Street Challenge

### Early NES brawler / arcade port (1984-86)

- Urban Champion (1984), Kung Fu Master / Kung-Fu (1985), Karate Champ, Pro Wrestling, Ring King. Flattest NES shading; minimal palette.

### NES JRPG overworld (1986-92)

- **Dragon Quest (Dragon Warrior)**: Dragon Quest 1-4 NES
- **Final Fantasy**: Final Fantasy 1-3 NES
- **Mother**: Mother (Earthbound Beginnings / EarthBound Zero)
- **Master System / early Ys**: Phantasy Star (Master System), early Ys
- Tiny 16-24 px chibi sprites, 4-8 color sprites.

### Game Boy (1989-98)

- **Game Boy DMG (monochrome)**: Tetris, Super Mario Land 1-2, The Legend of Zelda: Link's Awakening (DMG, 1993), Metroid II, Final Fantasy Adventure, Mega Man V (DMG). Strict 4-shade green-tinted or grayscale palette.
- **Game Boy Color**: Pokemon Gold/Silver/Crystal, Zelda: Oracle of Ages/Seasons, Wario Land 3, Dragon Warrior Monsters, Shantae (GBC).

### Arcade golden age (1989-95)

- **Konami arcade beat'em-up** (cartoon-licensed): The Simpsons Arcade Game, X-Men: The Arcade Game, TMNT (1989 arcade), TMNT: Turtles in Time (arcade), Vendetta, Sunset Riders, Bucky O'Hare
- **Capcom arcade beat'em-up**: Final Fight, Cadillacs and Dinosaurs, Captain Commando, Knights of the Round, The King of Dragons, Armored Warriors
- **Sega Genesis brawler**: Streets of Rage 1-3 (Bare Knuckle), Golden Axe 1-3
- **Genesis platformer**: Sonic the Hedgehog 1/2/3/&Knuckles, Earthworm Jim, Vectorman, Ristar, Comix Zone, Rocket Knight Adventures
- **SNK Metal Slug**: Metal Slug 1, 2, 3, X
- **Classic 16-bit arcade fighter**: Street Fighter II, Super SF II Turbo, King of Fighters '94-'97, Samurai Shodown 1-3, Mortal Kombat (early), Killer Instinct

### SNES (1990-97)

- **SNES JRPG (Toriyama/Square)**: Chrono Trigger, Final Fantasy VI (FF6), Secret of Mana, Seiken Densetsu 3 (Trials of Mana), Terranigma, Lufia II
- **SNES platformer**: Super Mario World, Yoshi's Island, Donkey Kong Country (pre-rendered 2D look), Kirby Super Star, Super Mario All-Stars
- **SNES action-RPG (top-down)**: The Legend of Zelda: A Link to the Past, Secret of Mana, Soul Blazer, Lufia, Illusion of Gaia
- **SNES tactical**: Final Fantasy Tactics (PS1, included here), Tactics Ogre: Let Us Cling Together, Ogre Battle

### Late 90s 2D fighter / Neo Geo (1995-2003)

- **SNK late Neo Geo**: King of Fighters '98-2003, Garou: Mark of the Wolves, The Last Blade 1-2, Samurai Shodown IV-V Special
- **Capcom late Neo Geo**: Marvel vs Capcom, Capcom vs SNK 2, Street Fighter Alpha 3
- **PS1 2D**: Castlevania: Symphony of the Night (32-bit 2D bridge)

### Handheld GBA (2001-08)

- **Castlevania GBA**: Castlevania: Aria of Sorrow, Castlevania: Harmony of Dissonance, Castlevania: Circle of the Moon
- **Pokemon GBA**: Ruby/Sapphire/Emerald, FireRed/LeafGreen
- **Other GBA**: Advance Wars 1-2, Mario & Luigi: Superstar Saga, Metroid: Zero Mission, Metroid Fusion, Golden Sun 1-2
- **DS sister**: Mario & Luigi: Partners in Time, Pokemon Diamond/Pearl overworld

### PC adventure / DOS (1990-95)

- **LucasArts SCUMM**: Monkey Island 2: LeChuck's Revenge, Day of the Tentacle, Sam & Max Hit the Road, Full Throttle, Indiana Jones and the Fate of Atlantis
- **Sierra VGA**: King's Quest VI, Quest for Glory III/IV, Space Quest IV, Gabriel Knight
- **MS-DOS 256-color hand-painted feel**

### Western RPG (1988-2000)

- **Fallout 1-2 (Interplay)**, Wasteland (1988), Wasteland 2 (modern), Atom RPG. Top-down 3/4 perspective, post-apocalyptic gritty palette.
- **Baldur's Gate (sprite portraits)**, Icewind Dale, Planescape Torment portraits.

### Japanese PC-98 (1989-95)

- **Princess Maker 2**, Touhou Project (PC-98 era), early Leaf / Key visual novels (To Heart, Kanon PC-98), Cosmo Tank, Yu-No, Rusty. 16-color anime visual-novel art with heavy dithering.

---

## Modern indie (2010s-now)

### Modern indie chunky

- **Cozy / cottagecore**: Stardew Valley, Terraria, Forager, Graveyard Keeper, Animal Well, Coral Island
- **Aseprite community sprite work** (general reference: search "aseprite character sprite")
- **Cave Story**, Eastward (small sprites), Pokemon Crystal/HGSS overworld
- **Modern crunchy action**: Celeste (full version), Katana Zero, Spelunky / Spelunky 2, Downwell, Risk of Rain (original), Enter the Gungeon, Nuclear Throne

### Modern indie painterly

- **Painterly with dithering**: Hyper Light Drifter, Owlboy, Eastward (larger scenes), Sea of Stars, Songs of Conquest, Hades (pixel-art moments)

### HD-2D (Square Enix)

- **Octopath Traveler 1-2**, Triangle Strategy, Live A Live remake (2022), Dragon Quest III HD-2D remake. Chibi SNES-style sprites in 3D environments with DOF blur.

### Pico-8

- Celeste Classic, Pico-8 jam games, Pico-8-style demakes. Strict 16-color Pico-8 fixed palette.

### Roguelike (top-down)

- Caves of Qud, Dwarf Fortress (Steam graphics), Stoneshard, Shiren the Wanderer, Mystery Dungeon, Cogmind. Tiny 12-24 px sprites for tile-density.

### Cyberpunk pixel

- VA-11 HALL-A: Cyberpunk Bartender Action, The Red Strings Club, Read Only Memories, 198X, Citizen Sleeper, Anodyne. Neon accents on dark backgrounds.

### Dark fantasy / soulslike

- Blasphemous 1-2, Salt and Sanctuary, Death's Gambit, The Last Faith, Eldest Souls. Religious-horror / Spanish-Baroque mood.

### Pixel horror (lo-fi unsettling)

- Yume Nikki, Lone Survivor, Faith: The Unholy Trinity, World of Horror, Lisa: The Painful, IB.

---

## Asset categories (for non-character requests)

### Environment tilesets

- Cave Story tiles, Stardew Valley tiles, NES Zelda 1 / Castlevania tiles, classic SNES Mario World tiles. Always specify the tile size (16x16, 24x24, 32x32, 48x48) and that it should be seamlessly tileable.

### Item icons (UI / inventory)

- Stardew Valley inventory icons, Terraria item icons, Castlevania SOTN inventory, classic RPG item art (Dragon Quest, FF). Single item, centered, 16x16 / 24x24 / 32x32.

### Mech / robot pixel

- Front Mission 1-3, Cybernator / Assault Suits Valken, Metal Warriors (SNES), Mega Man X mechs.

### Pokemon-style monster sprites

- Pokemon Gold/Silver/Crystal (GBC), Pokemon RSE (GBA) front-view battle sprites. ~56-64 px square.

---

## Mood / atmosphere keywords (use sparingly)

When the user gives a mood instead of a style, the agent can include these alongside game references:

- **Cute / friendly**: chibi, big-eyed, cottagecore
- **Heroic / action**: dynamic pose, ready stance, comic-book energy
- **Dark / gothic**: somber, religious-horror, gaunt, candle-lit
- **Sci-fi / cyber**: neon accents, holographic, tech-glow
- **Retro 8-bit**: hardware-constrained palette, blocky silhouettes
- **Painterly modern**: dithered shading, rich palette, atmospheric

Always pair the mood keyword with a SPECIFIC game reference so the model has a concrete training-data target.
