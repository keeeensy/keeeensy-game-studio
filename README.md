<p align="center">
  <img src="https://img.shields.io/badge/status-active-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/games-3-blue" alt="Games">
  <img src="https://img.shields.io/badge/minecraft%20mods-2-purple" alt="Mods">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

<h1 align="center">🎮 Keeeensy Game Studio</h1>
<p align="center"><i>Монорепозиторий инди-игр, инструментов и Minecraft-модов от KEEEENSY</i></p>

---

В этом репозитории собраны личные проекты: три игры (2D, 3D и survival), два мода для Minecraft Fabric и единый лаунчер, объединяющий всё вместе.

## 🚀 Быстрый старт

Запусти единый лаунчер:

```bash
launcher.bat
```

Или запускай проекты по отдельности (см. поддиректории).

## 📂 Проекты

<table>
  <tr>
    <th>Проект</th>
    <th>Стек</th>
    <th>Описание</th>
  </tr>
  <tr>
    <td><b>💎 <a href="gem_hunter/">Gem Hunter 2D</a></b></td>
    <td>Python + Pygame</td>
    <td>Процедурный 2D dungeon crawler. 15 уровней, враги, ачивки, встроенный редактор уровней. Вся графика и звук генерируются процедурно.</td>
  </tr>
  <tr>
    <td><b>🧊 <a href="3d_maze/">Gem Hunter 3D</a></b></td>
    <td>C++17 + raylib</td>
    <td>3D лабиринт от первого лица. 10 уровней, 3 типа врагов, миникарта, greedy mesh merge, процедурный звук.</td>
  </tr>
  <tr>
    <td><b>🧟 <a href="zombie_survival/">Zombie Survival</a></b></td>
    <td>Python + Pygame</td>
    <td>2D волновой survival-шутер. 4 типа зомби, система апгрейдов, бесконечные волны, процедурный звук.</td>
  </tr>
  <tr>
    <td><b>⚔️ <a href="rpg_levels_mod/">RPG Levels Mod</a></b></td>
    <td>Java + Fabric</td>
    <td>Мод для Minecraft Fabric. Назначает уровни монстрам, масштабирует урон, даёт XP за убийство.</td>
  </tr>
  <tr>
    <td><b>☠️ <a href="death_marker_mod/">Death Marker Mod</a></b></td>
    <td>Java + Fabric</td>
    <td>Мод для Minecraft Fabric. Ставит вечный Soul Torch на месте смерти.</td>
  </tr>
  <tr>
    <td><b>⚡ <a href="minecraft_profiles/">Minecraft Profiles</a></b></td>
    <td>PowerShell</td>
    <td>Профильный лаунчер Fabric. Управляет модами для 4 профилей (vanilla, RPG, Death Marker, All).</td>
  </tr>
</table>

## 🎯 Обзор игр

### Gem Hunter 2D
Процедурный dungeon crawler с 15 уровнями возрастающей сложности. Собирай магические сферы, избегай врагов, открывай выход. Полноценный редактор уровней с 5 кистями, система ачивок, полностью процедурная графика и звук — без внешних ресурсов.

### Gem Hunter 3D
3D-версия на C++17 и raylib. Процедурные 3D-лабиринты с greedy mesh merge, 3 типа врагов, миникарта, звук синтезируется на лету. 10 уровней от 8×8 до 26×26.

### Zombie Survival
Бесконечный волновый survival-шутер. 4 типа врагов (Normal, Fast, Tank, Spitter) открываются по ходу волн. Выбирай апгрейды после каждой волны (урон, скорострельность, скорость, HP). Весь звук синтезируется процедурно.

## 🧩 Minecraft-моды

Оба мода для Minecraft 26.1.2 с Fabric Loader 0.19.2 и Fabric API 0.149.1+26.1.2.

| Мод | События/Миксины | Описание |
|-----|-----------------|----------|
| RPG Levels | 3 миксина | Отображение уровня, масштабирование урона, XP за убийство, ники на большом расстоянии |
| Death Marker | Fabric API event | Ставит Soul Torch на месте смерти, вечный, на основе блока |

## 🖥️ Системные требования

| Компонент | Требование |
|-----------|------------|
| ОС | Windows 10+ |
| Python | 3.11+ (для Python-игр и лаунчера) |
| Pygame | 2.6+ |
| C++ | MinGW g++ (для 3D Maze) |
| CMake | 3.15+ (для 3D Maze) |
| Minecraft | 26.1.2 (для модов) |
| JDK | 25.0.3+ (для сборки модов) |
| Fabric Loader | 0.19.2 |

## 📄 Лицензия

Все проекты в этом репозитории распространяются под лицензией MIT, если не указано иное.
