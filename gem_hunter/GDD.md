# Gem Hunter 2D - Game Design Document

## 1. Game Overview / High Concept

Gem Hunter 2D is a procedurally generated 2D dungeon crawler/collect-a-thon where players navigate increasingly complex levels to collect all orbs (gems) and reach the exit portal. Built entirely with Python and Pygame, the game features no external assets—all visuals are procedurally generated primitives and all audio is synthesized in real-time.

**Genre**: 2D Action/Puzzle, Dungeon Crawler, Collect-a-thon  
**Perspective**: Top-down  
**Target Platform**: Windows (built with PyInstaller)  
**Resolution**: 800x600 @ 60 FPS  
**Core Loop**: Explore → Collect Gems → Avoid Enemies → Reach Exit → Progress to Next Level

## 2. Core Gameplay Mechanics

### Player Controls
- **Movement**: WASD or Arrow Keys for 8-directional movement
- **Sprint**: Hold Shift for 1.6x speed boost
- **Pause**: ESC key (opens pause menu)
- **Menu Navigation**: Arrow keys/WASD to select, Enter/Space to confirm

### Game Systems
- **Health System**: 3 lives total; enemy contact reduces lives by 1
- **Invincibility**: 2-second invincibility period after taking damage
- **Gem Collection**: Collect all orbs (gems) in a level to unlock the exit portal
- **Level Completion**: Reach the exit portal after collecting all gems
- **Progression**: 15 procedurally generated levels increasing in size and complexity

### Combat & Hazards
- **Enemy Contact**: Touching an enemy causes damage and respawns player at level start
- **Enemy Attack Cooldown**: Enemies can attack once per second when in contact
- **No Weapons**: Pure avoidance gameplay; player cannot attack enemies

## 3. Level Generation & Design

### Procedural Generation System
- **Algorithm**: BFS-based generation with wall placement rules
- **Level Count**: 15 total levels
- **Size Progression**: Starts at 10x10 tiles, increases by 1 tile per dimension each level (max 24x24)
- **Tile Size**: 60x60 pixels
- **Generation Elements**:
  - Walls (boundary and internal)
  - Empty spaces (walkable areas)
  - Gems (collectible orbs)
  - Exit portal (unlocks after all gems collected)
  - Enemy spawns (placed in accessible empty spaces)

### Generation Parameters by Level
- **Walls**: 4 + (level × 2) internal walls + optional corner chunks
- **Gems**: Random between (4 + level) and (7 + level×2), capped at 70% of accessible tiles
- **Enemies**: 2 + (level // 2) enemies per level
- **Exit Placement**: Farthest accessible point from start (using BFS distance)

### Level Structure
- **Start Position**: Fixed at (1,1) tile coordinates
- **Path Validation**: BFS ensures all placed gems and exit are reachable
- **Wall Placement Rules**:
  - Boundary walls always present
  - Internal walls avoid blocking start position
  - Corner chunks (3x3) added probabilistically based on level
  - 2x2 wall blocks added for levels ≥3

## 4. Enemy AI & Behavior

### Enemy Stats
- **Aggro Radius**: 160 pixels (≈2.67 tiles)
- **Speed**: Randomized between 60-100 pixels/second
- **HP**: 20 points (not visible to player)
- **Damage**: 10 HP per hit
- **Attack Cooldown**: 1 second between attacks

### Behavioral States
1. **Wander State** (Outside Aggro Radius):
   - Random direction changes every 0.8-2.5 seconds
   - Sine wave oscillation added to movement angle for organic movement
   - Direction randomized upon collision with walls

2. **Chase State** (Inside Aggro Radius):
   - Direct pursuit of player with calculated angle
   - Sine wave "wobble" applied to chase path (perpindicular oscillation)
   - Maintains pursuit until player exits aggro radius

### Movement Mechanics
- **Collision Detection**: Tile-based blocking with margin compensation
- **Movement Smoothing**: Velocity-based movement with delta-time scaling
- **Obstacle Avoidance**: Simple collision response (random direction change when blocked)

## 5. Achievement System

### Achievements
| Achievement | Description | Unlock Condition | Reward |
|-------------|-------------|------------------|--------|
| **Speedrunner** | Complete a level in under 30 seconds | Finish any level <30s | Visual notification |
| **Collector** | Collect 50 total gems | Accumulate ≥50 gems across playthrough | Visual notification |
| **Survivor** | Complete a level with <5 HP | Finish level with ≤4 HP remaining | Visual notification |
| **Explorer** | Reach level 3 | Complete first 3 levels | Visual notification + Explorer unlock |

### Implementation
- **Persistence**: Saved to `achievements.json` in game directory
- **Tracking**: 
  - Speedrunner: Checked per level completion
  - Collector: Tracks cumulative gems across all levels
  - Survivor: Checked via player HP at level completion
  - Explorer: Tracks highest level reached
- **Notifications**: On-screen toast with fade-in/hold/fade-out animation
- **Visual Display**: Achievements screen shows locked/unlocked status with ●/○ indicators

## 6. User Interface & Experience

### Menu System
- **Splash Screen**: 1.5-second fade-in/fade-out of "Keeeensy" title
- **Main Menu**: 
  - Animated particle background (80 particles with sine wave pulsation)
  - Menu options: Play Game, Level Select, Level Editor, Achievements, Quit
  - Hover highlighting and keyboard/mouse navigation
  - Title: "Gem Hunter 2D" with subtitle "Собери все орбы" (Collect all orbs)

### In-Game HUD
- **Top Left Corner**:
  - Gem counter: "Сферы: X / Y" (collected / total)
  - Lives display: Red circle icons (3 max)
  - Current level: "Уровень: X / 15"
  - Timer: "Время: MM:SS" format
- **Bottom Center**: Contextual hints
  - When doors closed: "Собери все сферы чтобы открыть выход"
  - When doors open: "Выход открыт! Найди зеленый маяк"
- **Achievement Notifications**: Bottom-right corner toast with gold/yellow theme
- **Pause Screen**: Semi-transparent overlay with "ПАУЗА" and control hints
- **Level Intro**: 1.5-second darkened screen with level number and "Приготовься..." text

### Visual Feedback
- **Player**: Blue circle with directional momentum indication
- **Enemies**: Red circles with darker outline
- **Gems**: Yellow circles
- **Walls**: Gray rectangles with darker outlines
- **Exit Portal**: 
  - Locked: Dark green pulse
  - Unlocked: Bright green pulse with white outline
- **Screen Shake**: Applied on enemy hit for impact feedback
- **Invincibility Flash**: Player character alternates visibility during invincibility period

## 7. Level Editor Design

### Editor Features
- **Grid-Based Editing**: Tile-based placement with 16x16 default grid
- **Zoom Control**: Ctrl + Mouse Wheel (0.3x to 3.0x zoom)
- **Pan Control**: Middle mouse button drag
- **Brush System**: 5 tile types accessible via number keys 1-5
  - 1: Floor (empty space)
  - 2: Wall (impassable)
  - 3: Gem (collectible orb)
  - 4: Exit (level completion point)
  - 5: Enemy (spawn point)
- **Placement**: Left-click to place, Right-click to erase
- **Save/Load**: Ctrl+S (save), Ctrl+L (load most recent)
- **Filename Input**: Text prompt for custom level names

### Editor Interface
- **Background**: Dark theme matching game aesthetic
- **UI Panel**: Bottom third of screen with controls
  - Tool labels and current brush indicator
  - Control hints: "Ctrl+колёсико — зум | Колёсико — скролл | Средняя кнопка — перемещение"
  - Action hints: "ЛКМ — установить | ПКМ — стереть | Ctrl+S — сохранить | Ctrl+L — загрузить | ESC — выход"
- **Tile Preview**: Selected tile highlighted with white outline
- **Current Brush**: Highlighted in yellow in brush selector

### Technical Implementation
- **TileMap Reuse**: Uses same TileMap class as main game
- **Coordinate Conversion**: Screen → world → tile coordinates with zoom compensation
- **Boundary Handling**: Automatic wall generation on map edges
- **Data Persistence**: JSON serialization of tile arrays
- **Integration**: Shares level loading/saving system with main game

## 8. Technical Architecture

### Core Modules
- **main.py** (152 lines): 
  - Game initialization, window setup
  - Splash screen implementation
  - Menu system with particle effects
  - Main game loop and state management
- **game.py** (861 lines):
  - Procedural audio synthesis system
  - TileMap generation and manipulation
  - Entity system (Player, Enemy base classes)
  - Game logic (level playing, achievement tracking)
  - Rendering system (all procedural graphics)
  - Level editor implementation
  - Save/load systems for levels and achievements

### Engine Systems
- **Rendering**: 
  - Pure Pygame primitives (rects, circles, ellipses)
  - No sprite sheets or external images
  - Procedural animations (pulsing, sine waves, particles)
  - Camera follow system with smooth movement
  - Screen shake effect for feedback
- **Audio**:
  - Real-time waveform synthesis
  - Four sound types: collect, hit, complete, enemy_hit
  - WAV format generation in memory
  - No external audio files
- **Physics**: 
  - Simple AABB collision detection
  - Tile-based blocking system
  - Velocity-based movement with delta-time
- **Data Management**:
  - JSON persistence for levels and achievements
  - Procedural level generation as fallback
  - Memory-efficient audio sample generation

### Technical Specifications
- **Language**: Python 3.x
- **Framework**: Pygame 2.x
- **Build Tool**: PyInstaller --onefile (gem_hunter.spec)
- **Audio Settings**: 22050 Hz, 16-bit, mono
- **Target FPS**: 60 (locked via clock.tick)
- **Memory Usage**: Minimal (procedural generation reduces asset load)

## 9. Audio Design (Procedural)

### Synthesis Approach
- **Waveform Generation**: Sine waves and white noise
- **Envelopes**: Linear decay (attack=0, decay=duration, sustain=0, release=0)
- **Effects**: Frequency sweeps, arpeggios, amplitude modulation

### Sound Effects Catalog
| Sound | Description | Synthesis Method |
|-------|-------------|------------------|
| **collect** | Gem pickup | 523Hz → 880Hz sweep over 120ms |
| **hit** | Player damage | White noise over 150ms |
| **complete** | Level finished | Arpeggio: C5-E5-G5-C6 (523-659-784-1047Hz) 80ms per note |
| **enemy_hit** | Enemy contact | 200Hz tone at 30% volume over 120ms |

### Audio Implementation Details
- **ProceduralAudio Class**: Centralized sound management
- **_build_wav()**: Creates WAV file structure in memory
- **_tone()**: Generates sine wave with optional frequency sweep
- **_noise()**: Creates white noise with amplitude envelope
- **_arpeggio()**: Chains multiple tones sequentially
- **_gen()**: Converts raw samples to pygame.mixer.Sound objects
- **play()**: Triggers sound playback by name

### Audio Design Philosophy
- **Retro Aesthetic**: Simple waveforms evoke classic chipphone sound
- **Feedback Clarity**: Distinct sounds for different game events
- **Zero Footprint**: No external audio files required
- **Procedural Flexibility**: Easy to adjust parameters for different effects

## 10. Build & Distribution

### Build Process
- **Tool**: PyInstaller
- **Command**: `pyinstaller --onefile gem_hunter.spec`
- **Output**: Single executable file (~10-30MB depending on compression)
- **Spec File**: gem_hunter.spec contains build configuration

### Distribution Characteristics
- **Portable**: Single .exe file, no installation required
- **Dependencies**: Bundles Python interpreter and Pygame
- **Startup**: Includes splash screen before main menu
- **File Structure**: 
  - Creates levels/ directory for user-generated content
  - Creates achievements.json for persistence
  - Executable runs from any location

### Technical Constraints
- **Windows Only**: Current build targets Windows platform
- **No Admin Rights**: Runs in user space without elevation
- **Antivirus Considerations**: Heuristic scanners may flag packed executables
- **Size Trade-off**: Single file convenience vs. larger download size

## 11. Future Improvement Ideas

### 1. Enhanced Enemy Variety
- **Add Enemy Types**: Different behaviors (stationary turrets, patrol paths, splitting enemies)
- **Visual Differentiation**: Unique shapes/colors for enemy types
- **Special Abilities**: Ranged attacks, area denial, buff/debuff auras
- **Implementation**: Extend Enemy class with type-specific update() methods

### 2. Power-Up System
- **Temporary Abilities**: Speed boost, invincibility, gem magnet, slow time
- **Spawn Mechanics**: Random placement or enemy drops
- **Visual Indicators**: Particle effects or aura around player
- **Duration Timers**: On-screen icons with countdown
- **Implementation**: Add power-up entity type and player status effects system

### 3. Expanded Level Features
- **Moving Platforms**: Timed or patrol-based moving tiles
- **Hazards**: Spikes, lava, poison (instant death or damage over time)
- **Keys & Doors**: Locked areas requiring key collection
- **Secrets**: Hidden areas with bonus gems or challenges
- **Implementation**: Extend TileMap data values and add special tile handling

### 4. Multiplayer Modes
- **Co-op**: Shared screen, collective gem collection
- **Versus**: Competitive gem racing or combat
- **Implementation**: 
  - Add second player entity with different controls
  - Implement shared or individual gem tracking
  - Add win/lose conditions for versus modes
  - Network or local multiplayer options

### 5. Accessibility & Polish Features
- **Control Remapping**: Customizable key bindings
- **Color Blind Modes**: Alternative color palettes
- **Difficulty Settings**: Adjust enemy speed, damage, lives
- **Visual Settings**: Particle density, screen shake intensity
- **Localization**: Support for multiple languages (currently Russian/English mix)
- **Implementation**: Settings menu with persistent configuration file

### 6. Level Editor Enhancements
- **Undo/Redo**: History buffer for editor actions
- **Brush Shapes**: Square/circle/line drawing tools
- **Level Testing**: Play button to test created levels
- **Object Properties**: Customize enemy count, gem placement rules
- **Template System**: Save/load room sections
- **Implementation**: Extend editor UI with additional panels and tools

### 7. Procedural Content Expansion
- **Biomes**: Different visual themes per level range (cave, forest, tech)
- **Music Generation**: Procedural background tracks
- **Level Themes**: Unique generation rules per biome
- **Visual Variations**: Different primitive styles (triangles, lines) per theme
- **Implementation**: Theme-based parameters in TileMap.generate()

### 8. Achievement Expansion
- **Challenge Achievements**: No damage, pacifist, speedrun combinations
- **Collection Achievements**: Specific gem counts, perfect level runs
- **Mastery Achievements**: Complete all levels with specific constraints
- **Implementation**: Expand achievement tracking and notification system

---

*Document Version: 1.0*  
*Created for: Gem Hunter 2D Portfolio/GitHub Presentation*  
*Technical Stack: Python 3.x, Pygame 2.x, PyInstaller*