# RPG Levels — Game Design Document

## Design Overview

RPG Levels adds a lightweight RPG layer to vanilla Minecraft without altering core gameplay. Every monster is assigned a level when it first ticks, its name tag displays `"Lvl X <Type>"` in a colour reflecting its threat, damage is scaled by level ratio, and players earn XP proportional to the monster's level on kill.

The mod targets Fabric 26.1.2, uses Mojang mappings, and runs without obfuscation (Loom's non-remap mode).

---

## Level Calculation

1. On first tick (`LivingEntityHurtMixin.onTick`), `RPGLevelsMod.setLevelDisplay` is called.
2. `getMobLevel` computes the level lazily and caches it per UUID:
   - `base = 1`
   - Find nearest `Player` within 32 blocks
   - If a `ServerPlayer` is found, `base = max(1, player.experienceLevel)`
   - Final level: `clamp(base + random(-1 .. +4), 1, 100)`
3. The level is cached forever. A mob's level never changes after its first tick.

---

## Damage Formula

Inside `LivingEntityHurtMixin.modifyDamage`:

### Player attacking Monster
```
ratio = mobLevel / max(1, playerLevel)
if ratio <= 1:  damage *= 0.5 + 0.5 / max(0.01, ratio)
if ratio > 1:   damage *= 1.0 / ratio
```
- Same level → normal damage
- Player outlevels mob → approaches 50% damage floor
- Mob outlevels player → inverse-linear decay (2× level → 50% damage)

### Monster attacking Player
```
ratio = mobLevel / max(1, playerLevel)
if ratio > 1:  damage *= ratio
else:          no change
```

---

## Name Tag Colour

Interpolation from white (level 1) to dark red (level 100):
```
t = clamp((level - 1) / 99, 0, 1)
r = 255 - t * 205
g = 255 - t * 255
b = 255 - t * 175
```

Format: `"Lvl 5 Zombie"`, `"Lvl 34 Creeper"` etc. Uses `LEVEL_PREFIX = "Lvl "`.

---

## Crosshair & Distance System

### Under 64 blocks — `EntityRendererMixin` (`shouldShowName`)
- Injects RETURN of `LivingEntityRenderer.shouldShowName`
- For level mobs: returns `isCrosshairTarget(entity)` — crosshair detection only, no LOS check
- `isCrosshairTarget` falls back to `isEntityUnderCrosshair` (own raycast using `camera.forwardVector()` + `AABB.clip()`), bypassing vanilla 3-block interaction range

### 64–256 blocks — `EntityRendererDistanceMixin` (`extractRenderState`)
- Injects RETURN of `EntityRenderer.extractRenderState`
- Vanilla method hard-caps at `distanceSq < 4096` (64 blocks)
- Overrides render state `nameTagVisibility` for level mobs within 256 blocks when crosshair + line-of-sight are satisfied
- `hasLineOfSight` uses `ClipContext(Block.COLLIDER)` from camera to mob eye position

### Why two mixins?
- Vanilla `shouldShowName` is only called when `distanceSq < 4096` — entities beyond 64 blocks never reach it
- `extractRenderState` is the only place to bypass the distance cap
- Line-of-sight is only required in the distance mixin to avoid false positives at long range

---

## Architecture

```
Server
├── RPGLevelsMod (ModInitializer)
│   ├── getMobLevel()            — lazy level calc + UUID cache
│   ├── getLevelColor()          — colour for name tag
│   ├── setLevelDisplay()        — write `"Lvl X <Type>"` custom name
│   ├── calcDamageModifier()     — damage ratio
│   └── ServerLivingEntityEvents.AFTER_DEATH → XP reward
└── LivingEntityHurtMixin
    ├── @Inject(tick)            — first-tick init
    └── @ModifyVariable(hurtServer) — damage scaling

Client
├── RPGLevelsClient (ClientModInitializer)
│   ├── isLevelMob()             — checks entity UUID in cache
│   ├── getCrosshairTarget()     — returns entity under crosshair
│   ├── isCrosshairTarget()      — true if entity is crosshair target
│   ├── isEntityUnderCrosshair() — own AABB raycast, bypasses interaction range
│   └── hasLineOfSight()         — ClipContext raycast
├── EntityRendererMixin
│   └── @Inject(shouldShowName) RETURN — crosshair only, ≤64 blocks
└── EntityRendererDistanceMixin
    └── @Inject(extractRenderState) RETURN — distance cap bypass, 64–256 blocks
```

---

## Future Ideas

- Config file for damage curve, XP multiplier, level range, colours
- Boss recognition (Wither, Dragon) with special formatting
- HUD overlay showing targeted mob's level and relative strength
- Per-player level scaling for multiplayer fairness
- Public API for other mods
