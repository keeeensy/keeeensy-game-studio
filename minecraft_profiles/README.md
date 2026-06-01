<p align="center">
  <img src="https://img.shields.io/badge/minecraft-26.1.2-green?logo=minecraft" alt="Minecraft">
  <img src="https://img.shields.io/badge/fabric%20loader-0.19.2-blue?logo=fabric" alt="Fabric Loader">
  <img src="https://img.shields.io/badge/fabric%20api-0.149.1%2B26.1.2-purple" alt="Fabric API">
  <img src="https://img.shields.io/badge/runtime-PowerShell%205.1-blue" alt="PowerShell">
  <img src="https://img.shields.io/badge/jdk-25.0.3%20Microsoft-orange" alt="JDK">
</p>

<h1 align="center">⚡ Minecraft Fabric Profiles</h1>
<p align="center"><i>Модульная система профилей для запуска Minecraft Fabric с разными комбинациями модов</i></p>

---

Скриптовый лаунчер на PowerShell, управляющий несколькими профилями модов Fabric. Устанавливает нужные моды в `.minecraft/mods`, запускает игру через KnotClient и восстанавливает оригинальные моды при выходе.

## 📦 Профили

| Профиль | Fabric API | RPG Levels | Death Marker | Описание |
|---------|:----------:|:----------:|:------------:|----------|
| `vanilla` | ❌ | ❌ | ❌ | Чистый Fabric (без модов) |
| `rpg_levels` | ✅ | ✅ | ❌ | Только RPG Levels Mod |
| `death_marker` | ✅ | ❌ | ✅ | Только Death Marker Mod |
| `all_mods` | ✅ | ✅ | ✅ | Оба мода |

## ⚙️ Использование

### PowerShell

```powershell
.\launch_fabric.ps1 -Profile <имя_профиля>
```

Профили: `vanilla`, `rpg_levels`, `death_marker`, `all_mods` (по умолчанию)

### Batch-файлы (корневая папка)

```
minecraft_vanilla.bat     → vanilla
minecraft_rpg_mod.bat     → rpg_levels
minecraft_death_marker_mod.bat → death_marker
minecraft_all_mods.bat    → all_mods
```

## 🔧 Как это работает

1. **`Sync-ProfileMods`** — копирует собранные JAR из `rpg_levels_mod/` и `death_marker_mod/` в папки профилей. Автоматически скачивает Fabric API, если его нет.
2. **`Deploy-Mods`** — бэкапит текущий `.minecraft/mods` → `mods_backup_launcher/`, затем копирует JAR выбранного профиля в `.minecraft/mods/`.
3. **`Get-Libraries`** — собирает все зависимости ванилы и Fabric Loader из JSON-файлов версий.
4. **`Extract-Natives`** — извлекает нативные DLL для LWJGL.
5. **Запускает** `KnotClient` с ZGC, pre-touch и compact headers.
6. **`Restore-Mods`** — восстанавливает оригинальную папку `mods/` при выходе.

## 📁 Структура проекта

```
minecraft_profiles/
├── launch_fabric.ps1    # Главный скрипт лаунчера
├── launcher.cs          # C# версия (справочно/альтернатива)
├── shared/              # Кэшированный JAR Fabric API
├── profiles/
│   ├── vanilla/         # Пусто (без модов)
│   ├── rpg_levels/      # fabric-api + rpg-levels
│   ├── death_marker/    # fabric-api + death-marker
│   └── all_mods/        # fabric-api + rpg-levels + death-marker
├── README.md
└── [Launcher] Minecraft.bat
```

## 📦 Требования

- Minecraft **26.1.2** (установлен через официальный лаунчер)
- Fabric Loader **0.19.2** (профиль установлен в `.minecraft/versions/`)
- Fabric API **0.149.1+26.1.2** (скачивается автоматически)
- JDK **25.0.3** (сборка Microsoft) в `C:\Users\keeeensy\AppData\Local\Programs\Microsoft\jdk-25.0.3.9-hotspot\`
- JAR-файлы модов, собранные из исходников (`./gradlew build` в каждом проекте мода)

## 🔄 Сборка модов

```bash
# RPG Levels Mod
cd ../rpg_levels_mod
./gradlew build

# Death Marker Mod
cd ../death_marker_mod
./gradlew build
```

Функция `Sync-ProfileMods` лаунчера подхватит собранные JAR-файлы автоматически.

## ⚠️ Заметки

- Лаунчер **бэкапит и восстанавливает** твою папку `.minecraft/mods/` — оригинальные моды остаются нетронутыми.
- Нативные DLL извлекаются во временную папку и удаляются при выходе.
- Офлайн-режим (без учётной записи Microsoft).
- JVM-аргументы: ZGC, compact headers, 2–4 ГБ heap.

## 📄 Лицензия

MIT
