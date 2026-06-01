# Death Marker Mod — Design Document

## Overview

Death Marker Mod is a lightweight Fabric mod that places a persistent Soul Torch at the player's death location. The goal is purely practical: help players find their way back to their death point to retrieve dropped items, without intrusive UI elements or chat spam.

## Design Decisions

### Block Placement Instead of Entity

An earlier prototype used an invisible glowing ArmorStand with a Soul Lantern on its head, but this was replaced with a direct block placement for three reasons:

1. **No despawn concerns** — A block stays until broken. No need for entity tracking, lifecycle management, or tick events.
2. **Vanilla interaction** — The torch can be broken, blocked by building, or waterlogged naturally. Players interact with it as any other block.
3. **Particle accuracy** — Soul Torch naturally emits soul particles when placed on solid ground, reinforcing the visual cue.

### Position Fallback

When the player dies in water, lava, or mid-air, `findPlacePos()` scans a 3×3×2 volume (Y level first, then X and Z) for a valid air block above solid ground. If no position is found, only particles are spawned — no spamming logs or error messages.

### No Persistence

The mod keeps no state, no map, no file. The block is the state. On server restart, the torch stays where it was (vanilla chunk saving handles it). This makes the mod trivially compatible with any world format or backup system.

## Technical Architecture

### Single Class, Zero Mixins

- `DeathMarkerMod.java` implements `ModInitializer`
- Registers `ServerLivingEntityEvents.AFTER_DEATH` listener
- `findPlacePos(ServerLevel, BlockPos)` — 3D scan for valid placement
- `canPlaceTorch(ServerLevel, BlockPos)` — checks `isAir()` + `below().isSolid()`

### Dependencies

- Fabric API 0.149.1+26.1.2 (for the death event)
- No mixins, no client entrypoint, no config files
