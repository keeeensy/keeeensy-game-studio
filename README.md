<p align="center">
  <img src="assets/banner.png" alt="Keeeensy Game Studio — 3 игры, 2 мода для Minecraft, единый лаунчер" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-a78bfa?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/C++-17-a78bfa?style=flat-square&logo=cplusplus&logoColor=white" alt="C++17">
  <img src="https://img.shields.io/badge/Java-25-ff8a65?style=flat-square&logo=openjdk&logoColor=white" alt="Java 25">
  <img src="https://img.shields.io/badge/PowerShell-5.1-ff8a65?style=flat-square&logo=powershell&logoColor=white" alt="PowerShell 5.1">
  <img src="https://img.shields.io/badge/Windows-10+-8888a0?style=flat-square&logo=windows&logoColor=white" alt="Windows 10+">
</p>

<p align="center">
  <b>Монорепозиторий инди-игр и модов для Minecraft.</b><br>
  Вся графика и звук в играх генерируются кодом — без единого внешнего ассета.
</p>

<p align="center">
  <a href="#проекты">Проекты</a> ·
  <a href="#игры">Игры</a> ·
  <a href="#моды-для-minecraft">Моды</a> ·
  <a href="#лаунчеры">Лаунчеры</a> ·
  <a href="#быстрый-старт">Быстрый старт</a> ·
  <a href="#структура">Структура</a>
</p>

---

## Проекты

| Проект | Что это | Стек |
|---|---|---|
| [**Gem Hunter 2D**](gem_hunter/) | Процедурный dungeon crawler: 15 уровней, враги, ачивки, редактор уровней | Python · Pygame |
| [**Gem Hunter 3D**](3d_maze/) | 3D-лабиринт от первого лица: 10 уровней, 3 типа врагов, миникарта | C++17 · raylib · CMake |
| [**Zombie Survival**](zombie_survival/) | Волновой survival-шутер: 4 типа зомби, апгрейды, бесконечные волны | Python · Pygame |
| [**RPG Levels**](rpg_levels_mod/) | Мод: уровни монстров 1–100, масштабирование урона, XP за убийство | Java · Fabric |
| [**Death Marker**](death_marker_mod/) | Мод: вечный Soul Torch на месте смерти игрока | Java · Fabric |
| [**Лаунчер**](launcher.pyw) | GUI для запуска всех игр и профилей Minecraft | Python · tkinter |
| [**Minecraft Profiles**](minecraft_profiles/) | Переключение наборов модов Fabric одной командой | PowerShell |

К каждой игре и моду есть свой README и дизайн-документ (`GDD.md`).

---

## Игры

### Gem Hunter 2D

Собери все сферы на уровне, чтобы открыть выход, и не попадись врагам.

- **Процедурные подземелья** — лабиринты от 10×10 до 24×24, связность каждого уровня проверяется BFS
- **4 типа врагов** — сложность растёт вместе с плотностью стен, числом врагов и сфер
- **Редактор уровней** — 5 кистей, зум и панорамирование, сохранение в JSON
- **4 ачивки** — Speedrunner, Collector, Survivor, Explorer
- **Без ассетов** — графика из примитивов Pygame, звук синтезируется в WAV

<details>
<summary><b>Управление и запуск</b></summary>

| Клавиша | Действие |
|---|---|
| WASD / стрелки | Движение |
| Shift | Спринт (×1.6) |
| Esc | Пауза |
| Enter | Пропустить интро уровня |

```bash
cd gem_hunter
pip install pygame
python main.py
```

Сборка exe: `python -m PyInstaller gem_hunter.spec` → `dist/gem_hunter.exe`
</details>

### Gem Hunter 3D

Трёхмерная версия Gem Hunter 2D на C++ и raylib — тот же игровой цикл, но от первого лица.

- **10 процедурных уровней** — от 8×8 до 26×26
- **3 типа врагов** — Scout (быстрый), Soldier (сбалансированный), Brute (медленный и живучий)
- **Миникарта** с исследованными зонами, сферами и выходом
- **Greedy mesh merge** — стены склеиваются в крупные меши ради производительности
- **Процедурный звук** и настройки громкости и чувствительности мыши

<details>
<summary><b>Управление и сборка</b></summary>

| Клавиша | Действие |
|---|---|
| WASD / стрелки | Движение |
| Shift | Спринт (×1.7) |
| Мышь | Обзор |
| Esc | В меню |
| Enter | Пропустить интро / подтвердить |

Нужны CMake 3.15+ и MinGW g++. raylib CMake скачает сам.

```bash
cd 3d_maze
cmake -B build -G "MinGW Makefiles"
cmake --build build
```

Или просто `build.bat` — готовый `maze_run_3d.exe` появится в папке `3d_maze`.
</details>

### Zombie Survival

Держи оборону против бесконечных волн зомби и прокачивайся между волнами.

- **4 типа врагов** — Normal, Fast, Tank, Spitter открываются по ходу волн
- **Апгрейды** — после каждой волны выбор: урон, скорострельность, скорость или Max HP
- **Процедурный звук** — без внешних аудиофайлов

<details>
<summary><b>Управление и запуск</b></summary>

| Клавиша | Действие |
|---|---|
| W / S, ↑ / ↓ | Движение вверх и вниз |
| ЛКМ | Выстрел в сторону курсора |
| Esc | Пауза |
| Q | Выход в меню (на паузе) |

```bash
cd zombie_survival
pip install pygame
python main.py
```

Сборка exe:

```bash
pyinstaller zombie_survival.spec
xcopy /E /I sprites dist\zombie_survival\sprites
```
</details>

---

## Моды для Minecraft

Оба мода работают на **Minecraft 26.1.2**, Fabric Loader **0.19.2** и Fabric API **0.149.1+26.1.2**.

| Мод | Что делает | Как устроен |
|---|---|---|
| [**RPG Levels**](rpg_levels_mod/) | Монстры получают уровень 1–100 и цветной ник `Lvl X Zombie`. Урон масштабируется в обе стороны, за убийство — `level × 10` XP. Уровень моба видно до 256 блоков. | 3 миксина, данные синхронизируются через ванильный `customName` — без своих пакетов |
| [**Death Marker**](death_marker_mod/) | При смерти ставит вечный Soul Torch на месте гибели. Ищет подходящее место в области 3×3×2 — работает в воде, лаве и в воздухе. | Только события Fabric API, без миксинов, работает на сервере |

<details>
<summary><b>Сборка и установка</b></summary>

Нужен JDK 25.

```powershell
cd rpg_levels_mod        # или death_marker_mod
.\gradlew build
```

Готовый `.jar` появится в `build/libs/`. Скопируй его в папку `mods/` своего Fabric-профиля вместе с Fabric API.
</details>

---

## Лаунчеры

### Единый лаунчер — [`launcher.pyw`](launcher.pyw)

Окно в стиле [сайта-портфолио](https://keeeensy.github.io/), из которого запускаются все три игры и четыре профиля Minecraft. Интерфейс — HTML/CSS в нативном окне ([pywebview](https://pywebview.flowrl.com/) + Edge WebView2, есть в Windows 10/11), логика запуска — на Python.

- **Статус сборки** у каждой игры: собрано, нет exe (тогда игра запустится из исходников) или не собрано, с подсказкой, как собрать
- **Отлов ошибок** — если игра или Minecraft падает сразу после запуска, лаунчер покажет уведомление с кнопкой открыть лог (`logs/`)
- **Управление с клавиатуры** — ↑ ↓ выбор, Enter запуск, Esc выход; двойной клик по плитке тоже запускает
- **Быстрые действия** — открыть папку проекта или его страницу на GitHub
- **Плавные переходы** и чёткий текст на экранах с любым масштабом

```bash
pip install pywebview
launcher.bat
```

Ярлык «Keeeensy Launcher» с иконкой на рабочем столе:

```powershell
.\create_shortcut.ps1
```

### Minecraft Profiles — [`minecraft_profiles/`](minecraft_profiles/)

PowerShell-скрипт, который перед запуском Minecraft подставляет нужный набор модов в `.minecraft/mods`, запускает игру и после выхода возвращает исходные моды на место.

| Профиль | Моды | Быстрый запуск |
|---|---|---|
| `vanilla` | Чистый Fabric | `minecraft_vanilla.bat` |
| `rpg_levels` | Fabric API + RPG Levels | `minecraft_rpg_mod.bat` |
| `death_marker` | Fabric API + Death Marker | `minecraft_death_marker_mod.bat` |
| `all_mods` | Fabric API + оба мода | `minecraft_all_mods.bat` |

```powershell
.\minecraft_profiles\launch_fabric.ps1 -Profile rpg_levels
```

---

## Быстрый старт

```bash
git clone https://github.com/keeeensy/keeeensy-game-studio.git
cd keeeensy-game-studio
pip install pygame
python gem_hunter/main.py
```

Остальные проекты запускаются и собираются по инструкциям в их разделах выше.

<details>
<summary><b>Системные требования</b></summary>

| Компонент | Версия | Для чего |
|---|---|---|
| Windows | 10+ | Все проекты |
| Python | 3.11+ | Python-игры и лаунчер |
| Pygame | 2.6+ | Gem Hunter 2D, Zombie Survival |
| pywebview | 5.3+ | Лаунчер |
| CMake + MinGW g++ | 3.15+ | Gem Hunter 3D |
| JDK | 25.0.3+ | Сборка модов |
| Minecraft + Fabric Loader | 26.1.2 + 0.19.2 | Моды |
</details>

---

## Структура

```
keeeensy-game-studio/
├── gem_hunter/           Gem Hunter 2D — Python + Pygame
├── 3d_maze/              Gem Hunter 3D — C++17 + raylib
├── zombie_survival/      Zombie Survival — Python + Pygame
├── rpg_levels_mod/       мод RPG Levels — Java + Fabric
├── death_marker_mod/     мод Death Marker — Java + Fabric
├── minecraft_profiles/   профили модов Minecraft — PowerShell
├── launcher.pyw          единый лаунчер — Python + tkinter
├── launcher.bat          запуск лаунчера
└── minecraft_*.bat       быстрый запуск профилей Minecraft
```

---

## Автор

**Keeeensy** — начинающий сисадмин и разработчик игр.
Сайт-портфолио: [keeeensy.github.io](https://keeeensy.github.io/)

## Лицензия

Все проекты распространяются под лицензией MIT, если в папке проекта не указано иное.
