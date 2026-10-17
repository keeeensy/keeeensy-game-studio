"""Keeeensy Launcher — запуск игр и профилей Minecraft из монорепозитория.

Интерфейс — HTML/CSS/JS в нативном окне (pywebview + Edge WebView2), лежит в
assets/launcher/ui. Этот файл — логика: статусы сборки, запуск процессов,
отслеживание падений и логи. JS вызывает методы класса Api.
"""
import os
import subprocess
import sys
import time
import webbrowser

try:
    import webview
except ImportError:
    import tkinter as tk
    from tkinter import messagebox
    _root = tk.Tk()
    _root.withdraw()
    messagebox.showerror("Keeeensy Launcher", "Для лаунчера нужен pywebview:\n\npip install pywebview")
    sys.exit(1)


BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets", "launcher")
LOGS = os.path.join(BASE, "logs")
REPO_URL = "https://github.com/keeeensy/keeeensy-game-studio/tree/master/"
SITE_URL = "https://keeeensy.github.io/"
CREATE_NO_WINDOW = 0x08000000
# Падение раньше этого срока считаем ошибкой запуска, а не обычным выходом из игры
CRASH_WINDOW_SEC = 30

GAMES = [
    {
        "key": "gem2d", "name": "Gem Hunter 2D", "icon": "gem",
        "tagline": "Процедурный dungeon crawler",
        "stack": ["Python", "Pygame"],
        "desc": "Собери все сферы на уровне, чтобы открыть выход, и не попадись врагам. "
                "Лабиринты генерируются процедурно, графика и звук — без единого внешнего ассета.",
        "features": ["15 уровней — от 10×10 до 24×24", "4 типа врагов и 4 ачивки",
                     "Встроенный редактор уровней"],
        "hint_icon": "keyboard", "hint": "WASD — движение · Shift — спринт · Esc — пауза",
        "folder": "gem_hunter",
        "exe": "gem_hunter/dist/gem_hunter.exe",
        "source": "gem_hunter/main.py",
        "build": "Собери exe: python -m PyInstaller gem_hunter.spec",
    },
    {
        "key": "gem3d", "name": "Gem Hunter 3D", "icon": "box",
        "tagline": "3D-лабиринт от первого лица",
        "stack": ["C++", "raylib", "CMake"],
        "desc": "Трёхмерная версия Gem Hunter: тот же игровой цикл, но от первого лица. "
                "Стены склеиваются в крупные меши (greedy mesh merge), звук синтезируется на лету.",
        "features": ["10 уровней — от 8×8 до 26×26", "3 типа врагов: Scout, Soldier, Brute",
                     "Миникарта и настройки чувствительности"],
        "hint_icon": "keyboard", "hint": "WASD — движение · мышь — обзор · Shift — спринт",
        "folder": "3d_maze",
        "exe": "3d_maze/maze_run_3d.exe",
        "source": None,
        "build": "Не собрано: запусти 3d_maze/build.bat (нужны CMake и MinGW)",
    },
    {
        "key": "zombie", "name": "Zombie Survival", "icon": "crosshair",
        "tagline": "Волновой survival-шутер",
        "stack": ["Python", "Pygame"],
        "desc": "Держи оборону против бесконечных волн зомби. После каждой волны выбираешь "
                "апгрейд, а новые типы врагов открываются по ходу игры.",
        "features": ["4 типа зомби: Normal, Fast, Tank, Spitter", "Апгрейды урона, скорострельности, скорости и HP",
                     "Процедурный звук"],
        "hint_icon": "keyboard", "hint": "W / S — движение · ЛКМ — выстрел · Esc — пауза",
        "folder": "zombie_survival",
        "exe": "zombie_survival/dist/zombie_survival/zombie_survival.exe",
        "source": "zombie_survival/main.py",
        "build": "Собери exe: pyinstaller zombie_survival.spec",
    },
]

MC_STACK = ["Minecraft 26.1.2", "Fabric 0.19.2"]
MC_HINT = "Моды подставляются в .minecraft/mods на время игры и возвращаются после выхода"

PROFILES = [
    {
        "key": "rpg_levels", "name": "RPG Levels", "icon": "swords", "sub": "уровни мобов",
        "tagline": "Уровни монстров и XP за убийство",
        "desc": "Монстры получают уровень от 1 до 100 и цветной ник. Урон масштабируется в обе стороны, "
                "а за убийство даётся level × 10 опыта.",
        "features": ["Уровень моба виден до 256 блоков", "Данные через ванильный customName — без своих пакетов",
                     "3 миксина на клиенте"],
        "folder": "rpg_levels_mod",
    },
    {
        "key": "death_marker", "name": "Death Marker", "icon": "skull", "sub": "метка смерти",
        "tagline": "Вечный факел на месте смерти",
        "desc": "При смерти мод ставит Soul Torch там, где ты погиб, — вещи больше не потеряются. "
                "Это настоящий блок, он переживает перезагрузку чанков.",
        "features": ["Ищет место в области 3×3×2", "Работает в воде, лаве и в воздухе",
                     "Только события Fabric API, без миксинов"],
        "folder": "death_marker_mod",
    },
    {
        "key": "all_mods", "name": "Все моды", "icon": "puzzle", "sub": "оба мода",
        "tagline": "RPG Levels и Death Marker вместе",
        "desc": "Оба мода сразу: уровни монстров, масштабирование урона и вечные метки на месте смерти.",
        "features": ["Fabric API", "RPG Levels", "Death Marker"],
        "folder": "minecraft_profiles",
    },
    {
        "key": "vanilla", "name": "Vanilla", "icon": "pickaxe", "sub": "без модов",
        "tagline": "Fabric без модов",
        "desc": "Чистый Fabric Loader без модов — чтобы поиграть в обычный Minecraft или проверить, "
                "что проблема не в модах.",
        "features": ["Без Fabric API", "Без модов", "Оригинальная папка mods не трогается"],
        "folder": "minecraft_profiles",
    },
]


ITEMS = [dict(g, kind="game") for g in GAMES] + [dict(p, kind="mc") for p in PROFILES]
BY_KEY = {it["key"]: it for it in ITEMS}


class Api:
    """Методы доступны из JS как window.pywebview.api.<имя>().
    Атрибуты с подчёркиванием pywebview наружу не отдаёт."""

    def __init__(self):
        self._window = None
        self._procs = {}      # key -> {"proc", "start", "log"}
        self._logs = {}       # key -> путь к последнему логу
        self._events = []     # уведомления для интерфейса

    # ---------- состояние ----------

    def _status(self, it):
        if it["key"] in self._procs:
            return {"kind": "run", "title": "Запущено", "detail": "Закрой игру, чтобы запустить снова"}
        if it["kind"] == "mc":
            return {"kind": "ok", "title": "Готово к запуску", "detail": "minecraft_profiles/launch_fabric.ps1"}
        if os.path.exists(os.path.join(BASE, it["exe"])):
            return {"kind": "ok", "title": "Собрано", "detail": it["exe"]}
        if it["source"] and os.path.exists(os.path.join(BASE, it["source"])):
            return {"kind": "warn", "title": "Запуск из исходников", "detail": "exe не собран · нужен pygame"}
        return {"kind": "err", "title": "Не собрано", "detail": it["build"]}

    def _public(self, it):
        game = it["kind"] == "game"
        return {
            "key": it["key"], "kind": it["kind"], "name": it["name"], "icon": it["icon"],
            "sub": " · ".join(it["stack"]) if game else it["sub"],
            "tagline": it["tagline"], "desc": it["desc"], "features": it["features"],
            "stack": it["stack"] if game else MC_STACK,
            "hint": it.get("hint", MC_HINT), "hint_icon": it.get("hint_icon", "puzzle"),
            "status": self._status(it),
            "has_log": bool(self._logs.get(it["key"]) and os.path.exists(self._logs[it["key"]])),
        }

    def state(self):
        return [self._public(it) for it in ITEMS]

    def poll(self):
        """Проверяет процессы; JS вызывает раз в секунду."""
        for key, info in list(self._procs.items()):
            code = info["proc"].poll()
            if code is None:
                continue
            del self._procs[key]
            if code != 0 and time.time() - info["start"] < CRASH_WINDOW_SEC:
                self._events.append({"kind": "err", "title": "Ошибка запуска",
                                     "body": f"{BY_KEY[key]['name']}: код {code}. Нажми, чтобы открыть лог",
                                     "log": key})
        events, self._events = self._events, []
        return {"items": self.state(), "events": events}

    # ---------- действия ----------

    def launch(self, key):
        it = BY_KEY[key]
        status = self._status(it)["kind"]
        if status == "run":
            return {"kind": "info", "title": it["name"], "body": "Уже запущено"}
        if status == "err":
            return {"kind": "err", "title": "Не собрано", "body": it["build"]}

        os.makedirs(LOGS, exist_ok=True)
        log_path = os.path.join(LOGS, f"{key}.log")
        if it["kind"] == "mc":
            script = os.path.join(BASE, "minecraft_profiles", "launch_fabric.ps1")
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script, "-Profile", key]
            cwd, body = os.path.dirname(script), "Minecraft запускается, это до минуты"
        elif status == "ok":
            exe = os.path.join(BASE, it["exe"])
            cmd, cwd, body = [exe], os.path.dirname(exe), "Запускаю…"
        else:
            src = os.path.join(BASE, it["source"])
            pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            cmd = [pyw if os.path.exists(pyw) else sys.executable, src]
            cwd, body = os.path.dirname(src), "Запускаю из исходников…"

        try:
            with open(log_path, "w", encoding="utf-8") as log:
                proc = subprocess.Popen(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT,
                                        stdin=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
        except OSError as err:
            return {"kind": "err", "title": "Не удалось запустить", "body": str(err)}
        self._procs[key] = {"proc": proc, "start": time.time(), "log": log_path}
        self._logs[key] = log_path
        return {"kind": "ok", "title": it["name"], "body": body}

    def open_folder(self, key):
        os.startfile(os.path.join(BASE, BY_KEY[key]["folder"]))

    def open_github(self, key):
        webbrowser.open(REPO_URL + BY_KEY[key]["folder"])

    def open_log(self, key):
        path = self._logs.get(key)
        if path and os.path.exists(path):
            os.startfile(path)

    def open_site(self):
        webbrowser.open(SITE_URL)

    def minimize(self):
        self._window.minimize()

    def close(self):
        self._window.destroy()


def set_window_icon(window):
    """У pywebview на Windows нет параметра иконки — ставим через WinForms."""
    try:
        import clr  # noqa: F401  (pythonnet, ставится вместе с pywebview)
        from System.Drawing import Icon
        window.native.Icon = Icon(os.path.join(ASSETS, "icon.ico"))
    except Exception:
        pass


def main():
    api = Api()
    window = webview.create_window(
        "Keeeensy Launcher", os.path.join(ASSETS, "ui", "index.html"), js_api=api,
        # pywebview вычитает из размера рамку окна даже без рамки — добавляем её обратно,
        # чтобы видимая область была ровно 1100×700
        width=1100 + 18, height=700 + 46, resizable=False, frameless=True, easy_drag=False,
        background_color="#0b0b12",
    )
    api._window = window
    window.events.shown += lambda: set_window_icon(window)
    webview.start(http_server=True)


if __name__ == "__main__":
    main()
