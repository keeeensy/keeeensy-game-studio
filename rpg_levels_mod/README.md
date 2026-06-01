<p align="center">
  <img src="https://img.shields.io/badge/minecraft-26.1.2-green?logo=minecraft" alt="Minecraft">
  <img src="https://img.shields.io/badge/fabric%20loader-0.19.2-blue?logo=fabric" alt="Fabric Loader">
  <img src="https://img.shields.io/badge/fabric%20api-0.149.1%2B26.1.2-purple" alt="Fabric API">
  <img src="https://img.shields.io/badge/java-25.0.3-orange?logo=openjdk" alt="Java">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

<h1 align="center">⚔️ RPG Levels Mod</h1>
<p align="center"><i>Мод для Minecraft Fabric — назначает уровни монстрам, масштабирует урон и даёт XP за убийство</i></p>

---

Каждый монстр появляется с уровнем (1–100). Мобы выше уровнем наносят тебе больше урона, а ты — меньше им. Убивай их за XP. Просто, серверно, без кастомных пакетов.

## ✨ Возможности

- **Отображение уровня** — цветные ники в формате `"Lvl X Zombie"`. Цвет меняется от белого (1 ур.) до тёмно-красного (100 ур.).
- **Масштабирование урона** — двунаправленный модификатор: игрок наносит меньше урона мобам выше уровнем; мобы выше уровнем наносят больше урона игроку.
- **XP за убийство** — `level × 10` XP с выводом в чат.
- **Ники на большом расстоянии** — уровень видно до 256 блоков, если прицел на мобе (в обход лимита ванилы в 64 блока). Проверка прямой видимости после 64 блоков.
- **Без кастомных пакетов** — все данные уровня синхронизируются через ванильный компонент `customName`. Миксины на клиенте управляют только видимостью ника.
- **Без зависимостей** — только Fabric API.

## 📦 Установка

### Требования

- Minecraft **26.1.2**
- Fabric Loader **0.19.2**
- Fabric API **0.149.1+26.1.2**

### Сборка

```bash
./gradlew build
```

Результат: `build/libs/rpg-levels-1.0.0.jar`

### Установка

Скопируй JAR в папку `mods/` своего Fabric-профиля вместе с Fabric API.

## 🔧 Как это работает

### Серверная часть

1. При спавне моба назначается случайный уровень (1–100, смещение в сторону низких)
2. Уровень хранится в persistent data моба через UUID
3. `LivingEntityHurtMixin` перехватывает расчёт урона:
   - Если `levelVictim > levelAttacker`, урон уменьшается на `ratio × 0.5`
   - Если `levelAttacker > levelVictim`, урон увеличивается на `ratio × 0.5`
4. При смерти моба: XP = `level × 10` выводится в чат

### Клиентская часть

- `EntityRendererMixin` (`shouldShowName` RETURN) — показывает ник только когда прицел на мобе (≤64 блока)
- `EntityRendererDistanceMixin` (`extractRenderState` RETURN) — увеличивает видимость ника до 256 блоков с прицелом + прямая видимость
- Определение прицела — собственный рейкаст (`camera.forwardVector()` + `AABB.clip()`) в обход лимита ванильного взаимодействия

## 📁 Структура проекта

```
rpg_levels_mod/
├── src/main/java/com/keeeensy/rpglevels/
│   ├── RPGLevelsMod.java           # Инициализатор мода
│   ├── LevelManager.java           # Назначение уровня + сохранение
│   └── mixin/
│       ├── LivingEntityHurtMixin.java       # Масштабирование урона
│       ├── EntityRendererMixin.java         # Видимость ника
│       └── EntityRendererDistanceMixin.java # Дальность ника
├── src/main/resources/
│   ├── fabric.mod.json
│   └── mixins.rpglevels.json
├── build.gradle
├── settings.gradle
├── gradle.properties
├── README.md
└── GDD.md
```

## 📄 Лицензия

MIT
