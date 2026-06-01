# Gem Hunter 3D — Game Design Document

## 1. Overview

**Gem Hunter 3D** is a first-person 3D maze game built with C++17 and raylib. It is the 3D counterpart to Gem Hunter 2D (Python/Pygame), sharing the same core loop: navigate a procedural maze, collect all orbs to open the exit, avoid enemies. 10 levels with increasing difficulty.

- **Engine**: raylib 5.5+
- **Build**: CMake + MinGW g++
- **Resolution**: 1280×720 @ 60 FPS
- **Author**: KEEEENSY

## 2. Maze Generation

### Algorithm
Each level generates a maze using the same BFS-based algorithm as Gem Hunter 2D:
1. Place boundary walls
2. Add internal walls (count scales with level)
3. Validate connectivity via BFS from spawn point
4. Place exit at farthest reachable cell from spawn
5. Re-validate — if exit is unreachable, find the nearest reachable cell and move exit there
6. Place orbs at random reachable cells (min distance 2 cells from spawn and exit)
7. Place enemies at random reachable cells

### Level Parameters

| Level | Rows×Cols | Internal Walls | Orbs (min–max) |
|-------|-----------|----------------|-----------------|
| 1 | 8×8 | 3 | 4–6 |
| 2 | 9×9 | 5 | 5–8 |
| 3 | 10×10 | 7 | 6–10 |
| 4 | 12×12 | 9 | 7–10 |
| 5 | 14×14 | 12 | 8–12 |
| 6 | 16×16 | 15 | 9–12 |
| 7 | 18×18 | 18 | 10–12 |
| 8 | 20×20 | 22 | 10–12 |
| 9 | 22×22 | 26 | 11–12 |
| 10 | 24×24 | 30 | 12–12 |

### Rendering (Greedy Mesh Merge)

Instead of rendering each wall cell as an individual cube, `Maze::BuildMesh()` groups adjacent wall cells into larger rectangles and creates a single pair of quads per rectangle. This reduces draw calls from thousands to tens.

## 3. Player

- **Height**: 1.6 units (eye level)
- **Radius**: 0.25 units (cylindrical collision)
- **Walk speed**: 6.0 units/s
- **Sprint multiplier**: 1.7× (Shift)
- **Mouse look**: Yaw/pitch with configurable sensitivity
- **Collision**: Axis-separated X/Z sweeps against maze walls

### Camera
- FOV: 80°
- Perspective projection
- Position at player eye height, target forward along yaw/pitch vector
- No camera smoothing (instant response)

## 4. Enemies

Spawned via `SpawnEnemies()` in `Enemy.cpp`.

| Type | HP | Speed | Radius | Color | Unlock Level |
|------|----|-------|--------|-------|-------------|
| Scout | 1 | 3.5 | 0.30 | (200,200,80) | 2 |
| Soldier | 2 | 2.5 | 0.35 | (200,80,80) | 4 |
| Brute | 3 | 1.5 | 0.45 | (120,40,40) | 6 |

### AI
- **State**: Wander (random direction, bounce off walls) or Hunt (chase player when within aggro radius)
- **Aggro radius**: 8 cells
- **Movement**: Velocity-based with delta-time, collision against maze walls
- **Visual**: Red sphere with floating HP bar, pulsing brightness based on aggro state

### Combat
- Contact damage on overlap (sum of radii check)
- 2-second invincibility after hit (screen flash + blinking player)
- 3 lives total
- Death respawns at level start

## 5. UI / UX

### Menu Flow
1. **Splash** — White screen with "Keeeensy", 2-second fade. Click/Enter to skip.
2. **Main Menu** — Particles floating in 3D space. Options: Start Game, Settings, Quit. Keyboard (W/S, arrows) and mouse hover selection.
3. **Settings** — Volume bar (0–100%) and mouse sensitivity bar. ← → to adjust, ESC to return.
4. **Level Intro** — "Level X / 10" overlay with "Get ready..." for 1.5 seconds.
5. **Playing** — First-person movement with DisableCursor (hidden, locked). HUD overlay.
6. **Level Complete** — "Level X cleared!" with time. Enter to continue.
7. **Win** — "YOU WIN!" with total time. Enter to return to menu.
8. **Game Over** — Red "GAME OVER". Enter to return to menu.

### HUD
- Top-left: orbs counter, lives (red circles), level number, level timer
- Bottom-center: contextual hint ("Collect all orbs to open exit" / "Exit open! Find the green beacon")
- Minimap: 160px square at top-right showing walls, player, orbs, exit

### Cursor Behavior
- Menu/Settings/Intro: `EnableCursor()` — visible, free
- Playing: `DisableCursor()` — hidden, locked to window center

## 6. Audio

All sounds synthesized at runtime (no external files):
- **Orb collect**: Rising sweep 523→880 Hz, 120ms
- **Enemy hit**: 100 Hz square wave, 150ms
- **Level complete**: Rising arpeggio 523→1047 Hz, 300ms

Volume controlled by settings slider, applied per-sound.

## 7. Technical Notes

### Architecture
```
main.cpp              — Window init, Game creation, main loop
Game.h/.cpp           — State machine, level loading, update/draw, UI, orb logic
Player.h/.cpp         — First-person movement, camera, collision
Maze.h/.cpp           — Maze generation, collision queries, mesh building, minimap
Enemy.h/.cpp          — Enemy types, AI, spawning, rendering
```

### Build System
- CMake with FetchContent for raylib
- `build.bat` runs CMake configure + build, copies exe to root
- `--validate` CLI flag runs maze validation for all 10 levels

### Future Ideas
- Splash screen animation (fade "Keeeensy")
- Settings menu (volume already done, sensitivity already done)
- Shadows on walls/enemies
- Death sound
- More enemy variety (ranged, boss)
- Level-select screen
- Persistent high scores
