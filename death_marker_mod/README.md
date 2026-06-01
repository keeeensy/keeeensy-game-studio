<p align="center">
  <img src="https://img.shields.io/badge/minecraft-26.1.2-green?logo=minecraft" alt="Minecraft">
  <img src="https://img.shields.io/badge/fabric%20loader-0.19.2-blue?logo=fabric" alt="Fabric Loader">
  <img src="https://img.shields.io/badge/fabric%20api-0.149.1%2B26.1.2-purple" alt="Fabric API">
  <img src="https://img.shields.io/badge/java-25.0.3-orange?logo=openjdk" alt="Java">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

<h1 align="center">☠️ Death Marker Mod</h1>
<p align="center"><i>Мод для Fabric, который ставит Soul Torch на месте смерти — вечный, серверный, без миксинов</i></p>

---

Когда ты умираешь, мод устанавливает факел `Soul Torch` на месте смерти со взрывом частиц. Факел остаётся навсегда — вечная отметка того, где ты пал.

## ✨ Возможности

- **Вечная метка** — настоящий блок в мире, а не сущность. Переживает перезагрузку чанков.
- **Умное размещение** — сканирует область 3×3×2 в поисках подходящего места. Работает в воде, лаве и в воздухе.
- **Визуальный эффект** — частицы `soul` при установке.
- **Не исчезает** — факел вечен, пока его не сломают или не застроят.
- **Только на сервере** — без миксинов, только Fabric API события.

## 📦 Установка

### Требования

- Minecraft **26.1.2**
- Fabric Loader **0.19.2**
- Fabric API **0.149.1+26.1.2**

### Сборка

```bash
./gradlew build
```

Результат: `build/libs/death-marker-1.0.0.jar`

### Установка

Скопируй `death-marker-1.0.0.jar` в папку `mods/` своего Fabric-профиля вместе с Fabric API.

## 🔧 Как это работает

1. Событие `ServerLivingEntityEvents.AFTER_DEATH` срабатывает при смерти игрока
2. Мод сканирует область 3×3×2 вокруг `blockPosition` игрока
3. Находит первый воздушный блок с твёрдым блоком под ним
4. Устанавливает туда `SOUL_TORCH` (или `SOUL_WALL_TORCH` у стены)
5. Спавнит частицы `soul`
6. Если подходящего места нет (смерть в пустоте), показывает только частицы

### Преимущества блока перед сущностью

- Настоящий блок = сохраняется в чанке, не пропадает при перезапуске
- Никакого AI, тактов и лагов
- Взаимодействует с редстоуном, водой и т.д. как обычный факел

## 📁 Структура проекта

```
death_marker_mod/
├── src/main/java/com/keeeensy/deathmarker/
│   ├── DeathMarkerMod.java        # Инициализатор мода + обработчик события
│   └── DeathMarkerModClient.java  # Частицы на клиенте
├── src/main/resources/
│   ├── fabric.mod.json
│   └── mixins.deathmarker.json
├── build.gradle
├── settings.gradle
├── gradle.properties
├── README.md
└── GDD.md
```

## 📄 Лицензия

MIT
