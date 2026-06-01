# Game Design Document — Zombie Survival

## 1. Game Overview

**Zombie Survival** is a 2D top-down wave survival shooter developed in Python with Pygame. The player controls a character that moves vertically on the left side of the screen and shoots horizontally at zombies that approach from the right. Each wave introduces more enemies and new types. Between waves, the player chooses an upgrade to power up their character. The game ends when the player's HP reaches zero.

- **Platform:** Windows (desktop)
- **Resolution:** 900 × 600
- **Target Framerate:** 60 FPS
- **Author:** KEEEENSY

---

## 2. Core Mechanics

### Movement
- Vertical-only movement using W/S or Up/Down arrow keys
- Player is constrained to the screen bounds (top/bottom edges)
- Speed: 200 px/s base, increased by Speed upgrade (+15% per level)

### Shooting
- Fires toward the mouse cursor with left mouse button
- Bullets travel at 500 px/s
- Base fire rate: 0.3s cooldown (reduced by Fire Rate upgrade)
- Base damage: 15 (increased by Damage upgrade, +25% per level)
- Bullets have a 5px radius with a yellow glow

### Wave Spawning
- Wave starts when all enemies from the previous wave are eliminated
- Brief delay between waves (1.5s, decreasing by 0.1s per wave, minimum 0.3s)
- Enemies per wave: `5 + wave × 3`
- Spawn interval: `0.6 − wave × 0.03` (minimum 0.15s)
- Enemies spawn at the right edge (`W + 30`) at a random Y position
- Enemy types unlocked progressively:
  - Wave 1: Normal
  - Wave 2+: Normal, Fast
  - Wave 3+: Normal, Fast, Tank
  - Wave 4+: Normal, Fast, Tank, Spitter

### Collision & Damage
- Bullet-enemy collision: distance-based (bullet radius + enemy radius)
- Enemy-player contact damage: continuous per-second damage
- Enemy projectiles (Spitter): one-shot damage on collision
- Hit flash (0.1s white tint) and damage flash overlay (red screen tint) provide visual feedback

---

## 3. Enemy Types

| Type | HP | Speed | Damage | Radius | Color | Wave | Behavior |
|------|----|-------|--------|--------|-------|------|----------|
| Normal | 30 | 80 | 10 | 16 | (60, 140, 60) | 1 | Chases player directly |
| Fast | 15 | 150 | 7 | 12 | (180, 180, 50) | 2 | Chases; high speed, low HP |
| Tank | 100 | 50 | 20 | 22 | (100, 40, 40) | 3 | Chases; slow, very tanky |
| Spitter | 20 | 60 | 5 | 14 | (120, 60, 140) | 4 | Chases + fires projectiles within 300px range (1.5–3s interval, 5 damage, 200 speed) |

All enemies display an HP bar above them and a colored tint when taking damage.

---

## 4. Upgrade System

After each wave (starting from wave 2), the player receives 1 upgrade point and chooses one of four upgrades via a menu overlay.

| Upgrade | Stat Key | Effect per Level | Formula |
|---------|----------|------------------|---------|
| Damage | `damage` | +25% bullet damage | `15 × (1 + level × 0.25)` |
| Fire Rate | `fire_rate` | +20% fire rate | `0.3 / (1 + level × 0.2)` seconds |
| Speed | `speed` | +15% movement speed | `200 × (1 + level × 0.15)` px/s |
| Max HP | `max_hp` | +20 max HP | `100 + (level − 1) × 20` |

- All upgrades start at level 1
- After each wave completion the player heals 30 HP (capped at max HP)
- The upgrade menu can be dismissed with ESC (point is saved)

---

## 5. Procedural Audio Design

All sounds are synthesized at runtime using Pygame's `mixer.Sound` with a custom sample buffer generator. There are no external audio files.

| Sound | Frequency | Duration | Wave Type | Volume | Description |
|-------|-----------|----------|-----------|--------|-------------|
| Shoot | 800 Hz | 0.08s | sweep | 0.25 | Rising frequency sweep for gunfire |
| Hit | 100 Hz | 0.15s | square | 0.40 | Low square wave for taking damage |
| Kill | 200 Hz | 0.10s | noise | 0.30 | White noise burst for enemy death |
| Wave Complete | 523 Hz | 0.30s | chime | 0.30 | Dual-tone chime with exponential decay |

The synthesis pipeline:
1. Generate raw samples at 22050 Hz, 16-bit signed
2. Apply waveform (square / noise / sweep / chime / sine)
3. Apply linear amplitude envelope (fade-out over duration)
4. Convert to `pygame.mixer.Sound` via `array.array` buffer

Volume is adjustable via the Settings menu slider (0–100%), persisted in the `volume` global and applied per-sound.

---

## 6. UI / UX

### Menu Flow
1. **Splash Screen** — White background with "Keeeensy" text, 1.5s fade-out. Click/key skips.
2. **Main Menu** — Three options: Play, Settings, Quit. Mouse hover highlights with blue border. Keyboard W/S and mouse wheel supported.
3. **Settings** — Volume slider (click-drag or scroll wheel). ESC to return.
4. **Game Loop** — Core gameplay with HUD.
5. **Upgrade Menu** — Overlay after each wave. Four cards with level and description.
6. **Death Screen** — Red "Вы погибли!" (You died!) with score and wave number. Any key or click to return to menu.
7. **Pause Overlay** — Semi-transparent black overlay. ESC to resume, Q to quit.

### HUD
- HP bar: horizontal segmented rectangles at top-left (each segment = 10 HP)
- Wave number, score, and alive enemy count displayed below HP
- Custom crosshair: white "+" symbol at mouse position

### Overlays
- **Wave Complete:** Dark semi-transparent overlay with "Wave N cleared!" and countdown to next wave
- **Damage Flash:** Red screen overlay that fades out over 0.3s

### Fonts
- Uses `segoeui` system font in three sizes: 72 (large), 36 (medium), 24 (small), 16 (tiny)
- UI text is in Russian in the current build

---

## 7. Art Style

- **Sprites:** Two PNG images (`player_new.png` and `zombie.png`)
  - Player sprite: 48×48, extracted from sheet via `subsurface((0, 0, 48, 48))`
  - Zombie sprites: scaled to different sizes per type (24–44px) and tinted via `BLEND_MULT`
- **Fallback shapes:** If sprites fail to load, enemies render as colored circles and the player as a cyan ellipse
- **Background:** Dark theme (`DARK_BG = (25, 2, 6)`) with a particle system of 80 white dots drifting and pulsing in alpha
- **Enemy HP bars:** Dark background bar with a green-to-red fill

---

## 8. Technical Architecture

- **Single-file design:** All code resides in `main.py` (~617 lines)
- **Rendering loop:** `pygame.time.Clock.tick(60)` for fixed timestep
- **Coordinate system:** Origin top-left, player on left, enemies spawn from right
- **Sprite loading path:** Resolves `base_dir` via `sys.executable` (frozen) or `__file__` (script), then loads `sprites/zombie.png` and `sprites/player_new.png`
- **State management:** Top-level functions (`splash`, `Menu.run`, `SettingsMenu.run`, `UpgradeMenu.run`, `run_game`, `show_death`) called sequentially from `main()`
- **Sound:** Global `pygame.mixer.Sound` objects created once at startup
- **Error handling:** Game crashes caught in `main()`, written to `crash.log` with traceback

### Enemy Sprite System
- Class-level `images` dictionary populated once via `Enemy.init_images()`
- Each enemy type uses the same zombie PNG scaled to different sizes
- Enemies tinted with `BLEND_MULT` using their type color

---

## 9. Build and Distribution

### Development
```bash
pip install pygame
python main.py
```

### Building with PyInstaller
```bash
pip install pyinstaller
pyinstaller zombie_survival.spec
```

The `.spec` file uses `--onedir` mode (COLLECT). The `datas=[]` field is intentionally empty — sprites must be copied manually after build:

```bash
xcopy /E /I sprites dist\zombie_survival\sprites
```

Output: `dist/zombie_survival/zombie_survival.exe`

---

## 10. Future Improvement Ideas

1. **Horizontal player movement** — Add left/right strafing or full 2D movement with camera scrolling for larger maps.

2. **More weapon types** — Shotgun spread, piercing rifle, explosive launcher, or a melee attack with knockback to add tactical depth.

3. **Map variety / arenas** — Multiple maps with obstacles, chokepoints, or interactive elements (barricades, turrets). Wave-based arena selection.

4. **Persistent progression** — Save player stats, high scores, and unlockable weapons/skins between sessions using JSON or SQLite.

5. **Power-ups and loot drops** — Health pickups, temporary damage boosts, or screen-clearing items dropped by killed enemies.

6. **Boss enemies** — Large, multi-phase boss zombies with unique attack patterns every 5 or 10 waves.

7. **Leaderboard** — Online or local high-score table tracking best wave and score across play sessions.
