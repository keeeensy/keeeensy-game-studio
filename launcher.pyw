"""Keeeensy Launcher — запуск игр и профилей Minecraft из монорепозитория.

Интерфейс рисуется на tkinter Canvas. Всё «тяжёлое» (фон, скруглённые карточки,
градиенты, иконки) рендерится через Pillow один раз и кешируется, а в цикле
анимации обновляются только звёзды, метеоры, тосты и индикаторы запуска.
"""
import ctypes
import math
import os
import random
import subprocess
import sys
import time
import webbrowser
import tkinter as tk
from tkinter import font as tkfont, messagebox

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageTk
except ImportError:
    _root = tk.Tk()
    _root.withdraw()
    messagebox.showerror("Keeeensy Launcher", "Для лаунчера нужен Pillow:\n\npip install pillow")
    sys.exit(1)


BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets", "launcher")
ICONS = os.path.join(ASSETS, "icons")
LOGS = os.path.join(BASE, "logs")
REPO_URL = "https://github.com/keeeensy/keeeensy-game-studio/tree/master/"
SITE_URL = "https://keeeensy.github.io/"

# Логический размер окна; реальный умножается на масштаб экрана Windows
W, H = 1100, 700
FPS_MS = 33

# Палитра как на сайте
BG = "#0b0b12"
TEXT = "#ececf4"
SOFT = "#bdbdd0"
MUTED = "#9b9bb3"
DIM = "#6b6b82"
VIOLET = "#a78bfa"
VIOLET_L = "#c4b5fd"
ORANGE = "#ff8a65"
OK = "#4ade80"
WARN = "#fbbf24"
ERR = "#f87171"

CREATE_NO_WINDOW = 0x08000000

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
        "stack": ["C++17", "raylib", "CMake"],
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


def enable_dpi_awareness():
    """Чёткий текст на экранах с масштабом 125%/150%."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def rgb(hexc):
    h = hexc.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def blend(c1, c2, t):
    a, b = rgb(c1), rgb(c2)
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Painter:
    """Рендер скруглённых карточек, градиентов и иконок через Pillow с кешем."""

    SS = 3  # суперсэмплинг для сглаженных краёв

    def __init__(self, scale):
        self.s = scale
        self.cache = {}

    def px(self, v):
        return int(round(v * self.s))

    def _mask(self, w, h, r, outline=0):
        k = self.SS
        m = Image.new("L", (w * k, h * k), 0)
        d = ImageDraw.Draw(m)
        box = (0, 0, w * k - 1, h * k - 1)
        if outline:
            d.rounded_rectangle(box, r * k, outline=255, width=max(1, int(outline * k)))
        else:
            d.rounded_rectangle(box, r * k, fill=255)
        return m.resize((w, h), Image.LANCZOS)

    @staticmethod
    def _hgrad(w, h, c1, c2):
        ramp = Image.new("L", (256, 1))
        ramp.putdata(range(256))
        mask = ramp.resize((w, h), Image.BILINEAR)
        return Image.composite(Image.new("RGBA", (w, h), c2), Image.new("RGBA", (w, h), c1), mask)

    def shape(self, w, h, r, fill, border=None, glow=None):
        """Карточка w×h (логические px). fill — RGBA или ("grad", rgba1, rgba2).
        Возвращает (PhotoImage, отступ под свечение в реальных px)."""
        key = ("shape", w, h, r, fill, border, glow)
        if key in self.cache:
            return self.cache[key]
        pw, ph, pr = self.px(w), self.px(h), self.px(r)
        if isinstance(fill, tuple) and fill and fill[0] == "grad":
            body = self._hgrad(pw, ph, fill[1], fill[2])
        else:
            body = Image.new("RGBA", (pw, ph), fill)
        body.putalpha(ImageChops.multiply(body.getchannel("A"), self._mask(pw, ph, pr)))
        if border:
            ring = self._mask(pw, ph, pr, outline=self.s)
            layer = Image.new("RGBA", (pw, ph), border[:3] + (0,))
            layer.putalpha(ImageChops.multiply(ring, Image.new("L", (pw, ph), border[3])))
            body = Image.alpha_composite(body, layer)
        pad = 0
        if glow:
            pad = self.px(glow[1] * 2)
            out = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), glow[0][:3] + (0,))
            halo = Image.new("L", out.size, 0)
            halo.paste(self._mask(pw, ph, pr), (pad, pad))
            halo = halo.filter(ImageFilter.GaussianBlur(self.px(glow[1])))
            out.putalpha(ImageChops.multiply(halo, Image.new("L", out.size, glow[0][3])))
            out.alpha_composite(body, (pad, pad))
            body = out
        result = (ImageTk.PhotoImage(body), pad)
        self.cache[key] = result
        return result

    def icon(self, name, size, color):
        key = ("icon", name, size, color)
        if key not in self.cache:
            n = self.px(size)
            mask = Image.open(os.path.join(ICONS, name + ".png")).getchannel("A").resize((n, n), Image.LANCZOS)
            im = Image.new("RGBA", (n, n), rgb(color) + (255,))
            im.putalpha(mask)
            self.cache[key] = ImageTk.PhotoImage(im)
        return self.cache[key]

    def gradient_text(self, text, size, c1, c2):
        """Надпись с градиентом, как заголовки на сайте. None, если нет шрифта."""
        key = ("gtext", text, size)
        if key in self.cache:
            return self.cache[key]
        result = None
        for fname in ("seguibl.ttf", "segoeuib.ttf"):
            path = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", fname)
            if os.path.exists(path):
                f = ImageFont.truetype(path, self.px(size))
                l, t, r, b = f.getbbox(text)
                mask = Image.new("L", (r - l + 2, b - t + 2), 0)
                ImageDraw.Draw(mask).text((-l + 1, -t + 1), text, font=f, fill=255)
                img = self._hgrad(mask.width, mask.height, rgb(c1) + (255,), rgb(c2) + (255,))
                img.putalpha(mask)
                result = ImageTk.PhotoImage(img)
                break
        self.cache[key] = result
        return result

    def background(self, w, h):
        """Фон окна: тёмная база, цветные пятна света и сетка, затухающая к краям."""
        pw, ph = self.px(w), self.px(h)
        q = 4  # пятна размываются на уменьшенной копии — быстро и всё равно гладко
        glow = Image.new("RGB", (pw // q, ph // q), (0, 0, 0))
        d = ImageDraw.Draw(glow)
        gw, gh = glow.size
        d.ellipse((-gw * 0.25, -gh * 0.35, gw * 0.45, gh * 0.55), fill=(52, 34, 120))
        d.ellipse((gw * 0.6, gh * 0.5, gw * 1.25, gh * 1.35), fill=(110, 46, 24))
        d.ellipse((gw * 0.35, gh * 0.2, gw * 0.75, gh * 0.75), fill=(0, 34, 44))
        glow = glow.filter(ImageFilter.GaussianBlur(gw * 0.12)).resize((pw, ph), Image.BICUBIC)
        img = ImageChops.add(Image.new("RGB", (pw, ph), rgb(BG)), glow)

        grid = Image.new("L", (pw, ph), 0)
        gd = ImageDraw.Draw(grid)
        step = self.px(48)
        for x in range(0, pw, step):
            gd.line((x, 0, x, ph), fill=255)
        for y in range(0, ph, step):
            gd.line((0, y, pw, y), fill=255)
        fade = Image.radial_gradient("L").resize((pw, ph), Image.BILINEAR)
        fade = ImageChops.invert(fade).point(lambda v: max(0, v - 90) * 9 // 100)
        grid = ImageChops.multiply(grid, fade)
        img = Image.composite(Image.new("RGB", (pw, ph), (255, 255, 255)), img, grid)
        return ImageTk.PhotoImage(img)


class Launcher:
    def __init__(self):
        enable_dpi_awareness()
        self.root = tk.Tk()
        self.root.title("Keeeensy Launcher")
        self.root.configure(bg=BG)
        self.root.report_callback_exception = self.on_error

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        dpi_scale = self.root.winfo_fpixels("1i") / 96
        self.s = min(dpi_scale, sw * 0.94 / W, sh * 0.9 / H)
        self.p = Painter(self.s)
        px = self.p.px
        self.root.geometry(f"{px(W)}x{px(H)}+{(sw - px(W)) // 2}+{(sh - px(H)) // 2}")
        self.root.overrideredirect(True)
        try:
            self.root.iconbitmap(os.path.join(ASSETS, "icon.ico"))
        except tk.TclError:
            pass

        self.f = {
            "title": tkfont.Font(family="Segoe UI Semibold", size=-px(30)),
            "h": tkfont.Font(family="Segoe UI Semibold", size=-px(16)),
            "hs": tkfont.Font(family="Segoe UI Semibold", size=-px(14)),
            "body": tkfont.Font(family="Segoe UI", size=-px(15)),
            "sm": tkfont.Font(family="Segoe UI", size=-px(13)),
            "xs": tkfont.Font(family="Segoe UI", size=-px(12)),
            "label": tkfont.Font(family="Segoe UI Semibold", size=-px(11)),
            "btn": tkfont.Font(family="Segoe UI Semibold", size=-px(15)),
        }

        self.items = [dict(g, kind="game") for g in GAMES] + [dict(p, kind="mc") for p in PROFILES]
        self.selected = 0
        self.hover = None
        self.procs = {}          # key -> {"proc", "start", "log"}
        self.last_log = {}       # key -> путь к последнему логу
        self.toasts = []
        self.t = 0.0
        self.next_meteor = time.time() + 3
        self.meteor = None
        self.drag = None

        self.cv = tk.Canvas(self.root, width=px(W), height=px(H), bg=BG, highlightthickness=0)
        self.cv.pack(fill="both", expand=True)

        self.build_static()
        self.build_tiles()
        self.draw_detail()
        self.bind_keys()
        self.root.after(30, self.show_in_taskbar)
        self.root.after(FPS_MS, self.tick)
        self.root.after(600, self.watch_processes)
        self.root.mainloop()

    # ---------- окно ----------

    def show_in_taskbar(self):
        """Окно без системной рамки по умолчанию пропадает из панели задач — возвращаем."""
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            style = (style & ~0x00000080) | 0x00040000  # -TOOLWINDOW, +APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
            self.root.withdraw()
            self.root.after(10, self.root.deiconify)
            self.hwnd = hwnd
        except Exception:
            self.hwnd = None

    def minimize(self):
        if getattr(self, "hwnd", None):
            ctypes.windll.user32.ShowWindow(self.hwnd, 6)  # SW_MINIMIZE
        else:
            self.root.iconify()

    def on_press(self, e):
        self.drag = (e.x_root - self.root.winfo_x(), e.y_root - self.root.winfo_y())

    def on_drag(self, e):
        if self.drag:
            self.root.geometry(f"+{e.x_root - self.drag[0]}+{e.y_root - self.drag[1]}")

    def bind_keys(self):
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<Up>", lambda e: self.select((self.selected - 1) % len(self.items)))
        self.root.bind("<Down>", lambda e: self.select((self.selected + 1) % len(self.items)))
        self.root.bind("<Return>", lambda e: self.launch(self.items[self.selected]))
        self.root.focus_force()

    def on_error(self, exc, val, tb):
        import traceback
        os.makedirs(LOGS, exist_ok=True)
        with open(os.path.join(LOGS, "launcher.log"), "a", encoding="utf-8") as f:
            f.write(time.strftime("[%Y-%m-%d %H:%M:%S]\n"))
            traceback.print_exception(exc, val, tb, file=f)
        self.toast("Ошибка лаунчера", "Подробности в logs/launcher.log", kind="err",
                   action=lambda: os.startfile(os.path.join(LOGS, "launcher.log")))

    # ---------- статичная часть ----------

    def build_static(self):
        px, cv = self.p.px, self.cv
        self.bg_img = self.p.background(W, H)
        cv.create_image(0, 0, image=self.bg_img, anchor="nw", tags=("bg",))

        self.stars = []
        for _ in range(70):
            x, y = random.uniform(0, px(W)), random.uniform(0, px(H))
            r = random.uniform(0.6, 1.5) * self.s
            item = cv.create_oval(x - r, y - r, x + r, y + r, fill=BG, outline="", tags=("bg", "star"))
            self.stars.append((item, random.uniform(0.15, 0.55), random.uniform(0.6, 2.2), random.uniform(0, 6.3)))

        cv.tag_bind("bg", "<ButtonPress-1>", self.on_press)
        cv.tag_bind("bg", "<B1-Motion>", self.on_drag)

        # Шапка: бейдж и градиентная надпись
        img, pad = self.p.shape(132, 30, 15, (255, 255, 255, 15), border=(255, 255, 255, 30))
        cv.create_image(px(28), px(22), image=img, anchor="nw", tags=("bg",))
        cv.create_text(px(28 + 66), px(37), text="✦  K E E E E N S Y", fill=MUTED,
                       font=self.f["label"], tags=("bg",))
        word = self.p.gradient_text("Launcher", 24, "#f5f0ff", ORANGE)
        if word:
            cv.create_image(px(174), px(37), image=word, anchor="w", tags=("bg",))
        else:
            cv.create_text(px(174), px(37), text="Launcher", fill=TEXT, font=self.f["h"], anchor="w", tags=("bg",))

        self.make_button("site", 846, 20, 150, 34, None, "keeeensy.github.io",
                         lambda: webbrowser.open(SITE_URL), style="ghost")
        self.make_button("min", 1004, 20, 34, 34, "minus", None, self.minimize, style="ghost")
        self.make_button("close", 1046, 20, 34, 34, "x", None, self.root.destroy, style="close")

        cv.create_text(px(28), px(92), text="ИГРЫ", fill=DIM, font=self.f["label"], anchor="w", tags=("bg",))
        cv.create_text(px(28), px(420), text="MINECRAFT  ·  FABRIC", fill=DIM, font=self.f["label"],
                       anchor="w", tags=("bg",))
        cv.create_text(px(28), px(664), text="↑ ↓  выбор      Enter  запуск      Esc  выход",
                       fill=DIM, font=self.f["xs"], anchor="w", tags=("bg",))

        img, _ = self.p.shape(676, 588, 22, (255, 255, 255, 10), border=(255, 255, 255, 20))
        cv.create_image(px(396), px(84), image=img, anchor="nw", tags=("bg", "panel"))

    # ---------- плитки слева ----------

    def tile_rect(self, i):
        if i < len(GAMES):
            return 28, 106 + i * 96, 344, 84
        j = i - len(GAMES)
        return 28 + (j % 2) * 178, 436 + (j // 2) * 76, 166, 64

    def tile_image(self, i):
        _, _, w, h = self.tile_rect(i)
        if i == self.selected:
            return self.p.shape(w, h, 16, ("grad", (120, 80, 255, 52), (255, 107, 53, 32)),
                                border=(167, 139, 250, 150), glow=((124, 92, 255, 60), 10))
        if i == self.hover:
            return self.p.shape(w, h, 16, (255, 255, 255, 18), border=(167, 139, 250, 90))
        return self.p.shape(w, h, 16, (255, 255, 255, 11), border=(255, 255, 255, 20))

    def build_tiles(self):
        px, cv = self.p.px, self.cv
        self.tile_bg, self.tile_dot = {}, {}
        for i, it in enumerate(self.items):
            x, y, w, h = self.tile_rect(i)
            tag = f"tile{i}"
            tags = ("ui", tag)
            img, pad = self.tile_image(i)
            self.tile_bg[i] = cv.create_image(px(x) - pad, px(y) - pad, image=img, anchor="nw", tags=tags)
            game = it["kind"] == "game"
            isz = 52 if game else 40
            ix, iy = x + 12, y + (h - isz) / 2
            tile, _ = self.p.shape(isz, isz, 12 if game else 10, ("grad", (120, 80, 255, 46), (255, 107, 53, 31)),
                                   border=(167, 139, 250, 51))
            cv.create_image(px(ix), px(iy), image=tile, anchor="nw", tags=tags)
            cv.create_image(px(ix + isz / 2), px(iy + isz / 2), image=self.p.icon(it["icon"], 26 if game else 20, VIOLET_L),
                            tags=tags)
            tx = ix + isz + 14
            if game:
                cv.create_text(px(tx), px(y + 30), text=it["name"], fill=TEXT, font=self.f["h"], anchor="w", tags=tags)
                cv.create_text(px(tx), px(y + 54), text=" · ".join(it["stack"]), fill=MUTED, font=self.f["sm"],
                               anchor="w", tags=tags)
            else:
                cv.create_text(px(tx), px(y + 23), text=it["name"], fill=TEXT, font=self.f["hs"], anchor="w", tags=tags)
                cv.create_text(px(tx), px(y + 43), text=it["sub"], fill=MUTED, font=self.f["xs"], anchor="w", tags=tags)
            r = 4
            dx, dy = x + w - 18, (y + h / 2) if game else (y + 12)
            self.tile_dot[i] = cv.create_oval(px(dx - r), px(dy - r), px(dx + r), px(dy + r), outline="",
                                              fill=self.status_color(i), tags=tags)
            if not game:
                # У профилей Minecraft нет статуса сборки — точка видна только во время запуска
                cv.itemconfig(self.tile_dot[i], state="hidden")
            cv.tag_bind(tag, "<Enter>", lambda e, i=i: self.set_hover(i))
            cv.tag_bind(tag, "<Leave>", lambda e, i=i: self.set_hover(None, i))
            cv.tag_bind(tag, "<Button-1>", lambda e, i=i: self.select(i))
            cv.tag_bind(tag, "<Double-Button-1>", lambda e, i=i: self.launch(self.items[i]))

    def refresh_tile(self, i):
        x, y, _, _ = self.tile_rect(i)
        img, pad = self.tile_image(i)
        self.cv.itemconfig(self.tile_bg[i], image=img)
        self.cv.coords(self.tile_bg[i], self.p.px(x) - pad, self.p.px(y) - pad)

    def set_hover(self, i, leaving=None):
        if i is None and self.hover != leaving:
            return
        old, self.hover = self.hover, i
        for j in {old, i} - {None}:
            self.refresh_tile(j)
        self.cv.config(cursor="hand2" if i is not None else "")

    def select(self, i):
        if i == self.selected:
            return
        old, self.selected = self.selected, i
        self.refresh_tile(old)
        self.refresh_tile(i)
        self.draw_detail()

    # ---------- статус сборки ----------

    def status(self, it):
        if it["key"] in self.procs:
            return "run", "Запущено", "Процесс работает. Закрой игру, чтобы запустить снова."
        if it["kind"] == "mc":
            return "ok", "Готово к запуску", "Скрипт minecraft_profiles/launch_fabric.ps1"
        if os.path.exists(os.path.join(BASE, it["exe"])):
            return "ok", "Собрано", it["exe"]
        if it["source"] and os.path.exists(os.path.join(BASE, it["source"])):
            return "warn", "exe не собран — запуск из исходников", f"python {it['source']} · нужен pygame"
        return "err", "Не собрано", it["build"]

    def status_color(self, i):
        return {"ok": OK, "warn": WARN, "err": ERR, "run": VIOLET}[self.status(self.items[i])[0]]

    # ---------- правая панель ----------

    def draw_detail(self):
        px, cv = self.p.px, self.cv
        cv.delete("detail")
        for name in list(self.buttons):
            if name.startswith("d_"):
                del self.buttons[name]
        it = self.items[self.selected]
        tags = ("ui", "detail")
        x0 = 428

        tile, _ = self.p.shape(96, 96, 22, ("grad", (120, 80, 255, 60), (255, 107, 53, 40)), border=(167, 139, 250, 70))
        cv.create_image(px(x0), px(116), image=tile, anchor="nw", tags=tags)
        cv.create_image(px(x0 + 48), px(164), image=self.p.icon(it["icon"], 46, VIOLET_L), tags=tags)

        tx = x0 + 120
        cv.create_text(px(tx), px(118), text=it["name"], fill=TEXT, font=self.f["title"], anchor="nw", tags=tags)
        cv.create_text(px(tx), px(162), text=it["tagline"], fill=MUTED, font=self.f["body"], anchor="nw", tags=tags)

        cx = tx
        for chip in (it["stack"] if it["kind"] == "game" else MC_STACK):
            w = self.f["xs"].measure(chip) / self.s + 24
            img, _ = self.p.shape(int(w), 26, 13, (255, 255, 255, 14), border=(255, 255, 255, 28))
            cv.create_image(px(cx), px(190), image=img, anchor="nw", tags=tags)
            cv.create_text(px(cx + w / 2), px(203), text=chip, fill=SOFT, font=self.f["xs"], tags=tags)
            cx += w + 8

        cv.create_text(px(x0), px(240), text=it["desc"], fill=SOFT, font=self.f["body"], anchor="nw",
                       width=px(616), tags=tags)

        cv.create_text(px(x0), px(326), text="ВОЗМОЖНОСТИ", fill=DIM, font=self.f["label"], anchor="nw", tags=tags)
        for k, feat in enumerate(it["features"]):
            y = 356 + k * 30
            cv.create_oval(px(x0 + 1), px(y + 6), px(x0 + 7), px(y + 12), fill=VIOLET, outline="", tags=tags)
            cv.create_text(px(x0 + 20), px(y), text=feat, fill=TEXT, font=self.f["body"], anchor="nw", tags=tags)

        hint_icon = it.get("hint_icon", "puzzle")
        hint = it.get("hint", MC_HINT)
        cv.create_image(px(x0 + 9), px(470), image=self.p.icon(hint_icon, 18, MUTED), tags=tags)
        cv.create_text(px(x0 + 28), px(470), text=hint, fill=MUTED, font=self.f["sm"], anchor="w", tags=tags)

        kind, title, detail = self.status(it)
        color = {"ok": OK, "warn": WARN, "err": ERR, "run": VIOLET}[kind]
        icon = {"ok": "circle-check", "warn": "triangle-alert", "err": "triangle-alert", "run": "loader-circle"}[kind]
        cv.create_image(px(x0 + 9), px(536), image=self.p.icon(icon, 18, color), tags=tags)
        cv.create_text(px(x0 + 28), px(536), text=title, fill=color, font=self.f["hs"], anchor="w", tags=tags)
        cv.create_text(px(x0 + 28 + self.f["hs"].measure(title) / self.s + 10), px(536), text=detail, fill=DIM,
                       font=self.f["sm"], anchor="w", tags=tags)

        can_launch = kind in ("ok", "warn")
        label = "Играть" if it["kind"] == "game" else "Запустить"
        self.make_button("d_play", x0, 580, 196, 54, "play", label, lambda: self.launch(it),
                         style="primary" if can_launch else "disabled", extra_tags=("detail",))
        bx = x0 + 196 + 12
        folder = os.path.join(BASE, it["folder"])
        bx += self.make_button("d_folder", bx, 580, None, 54, "folder-open", "Папка",
                               lambda: os.startfile(folder), extra_tags=("detail",)) + 10
        bx += self.make_button("d_github", bx, 580, None, 54, "github", "GitHub",
                               lambda: webbrowser.open(REPO_URL + it["folder"]), extra_tags=("detail",)) + 10
        log = self.last_log.get(it["key"])
        if log and os.path.exists(log):
            self.make_button("d_log", bx, 580, None, 54, "file-text", "Лог",
                             lambda: os.startfile(log), extra_tags=("detail",))

    # ---------- кнопки ----------

    buttons = {}

    def button_image(self, name):
        b = self.buttons[name]
        hover = b["hover"]
        w, h, style = b["w"], b["h"], b["style"]
        r = h / 2 if style in ("primary", "secondary", "disabled") else 10
        if style == "primary":
            a = 255 if hover else 215
            glow = ((124, 92, 255, 90), 10) if hover else None
            return self.p.shape(w, h, r, ("grad", (124, 92, 255, a), (255, 107, 53, a)), glow=glow)
        if style == "disabled":
            return self.p.shape(w, h, r, (255, 255, 255, 10), border=(255, 255, 255, 18))
        if style == "close" and hover:
            return self.p.shape(w, h, r, (248, 113, 113, 210))
        if style in ("ghost", "close"):
            return self.p.shape(w, h, r, (255, 255, 255, 22 if hover else 0))
        if hover:
            return self.p.shape(w, h, r, (255, 255, 255, 26), border=(167, 139, 250, 110))
        return self.p.shape(w, h, r, (255, 255, 255, 12), border=(255, 255, 255, 28))

    def make_button(self, name, x, y, w, h, icon, text, command, style="secondary", extra_tags=()):
        """Кнопка из картинки-подложки, иконки и текста. Возвращает ширину (логич. px)."""
        px, cv = self.p.px, self.cv
        font = self.f["btn"] if h >= 44 else self.f["sm"]
        isz = 20 if h >= 44 else 18
        if w is None:
            w = int(28 + isz + 10 + font.measure(text) / self.s + 24)
        tag = "btn_" + name
        tags = ("ui", tag) + tuple(extra_tags)
        self.buttons[name] = {"w": w, "h": h, "style": style, "hover": False, "x": x, "y": y}
        img, pad = self.button_image(name)
        self.buttons[name]["item"] = cv.create_image(px(x) - pad, px(y) - pad, image=img, anchor="nw", tags=tags)
        fg = DIM if style == "disabled" else (MUTED if style == "ghost" and text else TEXT)
        if icon and text:
            content_w = isz + 10 + font.measure(text) / self.s
            sx = x + (w - content_w) / 2
            cv.create_image(px(sx + isz / 2), px(y + h / 2), image=self.p.icon(icon, isz, fg), tags=tags)
            cv.create_text(px(sx + isz + 10), px(y + h / 2), text=text, fill=fg, font=font, anchor="w", tags=tags)
        elif icon:
            cv.create_image(px(x + w / 2), px(y + h / 2), image=self.p.icon(icon, 18, SOFT), tags=tags)
        else:
            cv.create_text(px(x + w / 2), px(y + h / 2), text=text, fill=fg, font=font, tags=tags)
        if style != "disabled":
            cv.tag_bind(tag, "<Enter>", lambda e: self.button_hover(name, True))
            cv.tag_bind(tag, "<Leave>", lambda e: self.button_hover(name, False))
            cv.tag_bind(tag, "<ButtonRelease-1>", lambda e: command())
        return w

    def button_hover(self, name, on):
        b = self.buttons.get(name)
        if not b or b["hover"] == on:
            return
        b["hover"] = on
        img, pad = self.button_image(name)
        self.cv.itemconfig(b["item"], image=img)
        self.cv.coords(b["item"], self.p.px(b["x"]) - pad, self.p.px(b["y"]) - pad)
        self.cv.config(cursor="hand2" if on else "")

    # ---------- запуск ----------

    def launch(self, it):
        kind, _, detail = self.status(it)
        if kind == "run":
            self.toast(it["name"], "Уже запущено", kind="info")
            return
        if kind == "err":
            self.toast(f"{it['name']} не собран", detail, kind="err")
            return

        os.makedirs(LOGS, exist_ok=True)
        log_path = os.path.join(LOGS, f"{it['key']}.log")
        if it["kind"] == "mc":
            script = os.path.join(BASE, "minecraft_profiles", "launch_fabric.ps1")
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script, "-Profile", it["key"]]
            cwd = os.path.dirname(script)
            message = "Minecraft запускается — это может занять до минуты"
        elif kind == "ok":
            exe = os.path.join(BASE, it["exe"])
            cmd, cwd = [exe], os.path.dirname(exe)
            message = "Запускаю…"
        else:
            src = os.path.join(BASE, it["source"])
            pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            cmd = [pyw if os.path.exists(pyw) else sys.executable, src]
            cwd = os.path.dirname(src)
            message = "Запускаю из исходников…"

        try:
            with open(log_path, "w", encoding="utf-8") as log:
                proc = subprocess.Popen(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT,
                                        stdin=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
        except OSError as err:
            self.toast(f"Не удалось запустить {it['name']}", str(err), kind="err")
            return

        self.procs[it["key"]] = {"proc": proc, "start": time.time(), "log": log_path, "item": it}
        self.last_log[it["key"]] = log_path
        self.toast(it["name"], message, kind="ok")
        self.refresh_status(it["key"])

    def watch_processes(self):
        """Следит за запущенными процессами: быстрое падение показывает тостом с логом."""
        for key, info in list(self.procs.items()):
            code = info["proc"].poll()
            if code is None:
                continue
            del self.procs[key]
            lived = time.time() - info["start"]
            if code != 0 and lived < 30:
                log = info["log"]
                self.toast(f"{info['item']['name']} завершился с ошибкой",
                           f"Код {code}. Нажми, чтобы открыть лог", kind="err", action=lambda: os.startfile(log))
            self.refresh_status(key)
        self.root.after(600, self.watch_processes)

    def refresh_status(self, key):
        for i, it in enumerate(self.items):
            if it["key"] == key:
                state = "normal" if it["kind"] == "game" or key in self.procs else "hidden"
                self.cv.itemconfig(self.tile_dot[i], fill=self.status_color(i), state=state)
                if i == self.selected:
                    self.draw_detail()

    # ---------- тосты ----------

    def toast(self, title, body, kind="info", action=None):
        px, cv = self.p.px, self.cv
        tid = f"toast{time.time_ns()}"
        w, h = 360, 64
        img, _ = self.p.shape(w, h, 14, (22, 22, 34, 248), border=(255, 255, 255, 26))
        color = {"ok": OK, "err": ERR, "info": VIOLET_L}[kind]
        icon = {"ok": "circle-check", "err": "triangle-alert", "info": "sparkles"}[kind]
        tags = ("toast", tid)
        cv.create_image(0, 0, image=img, anchor="nw", tags=tags)
        cv.create_image(px(26), px(h / 2), image=self.p.icon(icon, 20, color), tags=tags)
        cv.create_text(px(48), px(22), text=title, fill=TEXT, font=self.f["hs"], anchor="w", tags=tags)
        cv.create_text(px(48), px(43), text=body, fill=MUTED, font=self.f["xs"], anchor="w",
                       width=px(w - 60), tags=tags)
        if action:
            cv.tag_bind(tid, "<Button-1>", lambda e: action())
            cv.tag_bind(tid, "<Enter>", lambda e: cv.config(cursor="hand2"))
            cv.tag_bind(tid, "<Leave>", lambda e: cv.config(cursor=""))
        # стартуем за правым краем, дальше выезжает в tick()
        cv.move(tid, px(W + 10), px(76))
        self.toasts.append({"tag": tid, "born": time.time(), "w": w, "h": h, "x": W + 10, "y": 76})
        self.layout_toasts()

    def layout_toasts(self):
        y = 76
        for t in self.toasts:
            t["ty"] = y
            y += t["h"] + 10

    def update_toasts(self):
        now = time.time()
        for t in list(self.toasts):
            life = now - t["born"]
            target_x = W - 28 - t["w"] if life < 5 else W + 10
            nx = t["x"] + (target_x - t["x"]) * 0.25
            ny = t["y"] + (t["ty"] - t["y"]) * 0.25
            self.cv.move(t["tag"], self.p.px(nx) - self.p.px(t["x"]), self.p.px(ny) - self.p.px(t["y"]))
            t["x"], t["y"] = nx, ny
            if life > 5.6:
                self.cv.delete(t["tag"])
                self.toasts.remove(t)
                self.layout_toasts()
        self.cv.tag_raise("toast")

    # ---------- анимация ----------

    def tick(self):
        self.t += FPS_MS / 1000
        for n, (item, base, speed, phase) in enumerate(self.stars):
            if n % 2 == int(self.t * 30) % 2:
                v = base * (0.55 + 0.45 * math.sin(self.t * speed + phase))
                self.cv.itemconfig(item, fill=blend(BG, "#ffffff", v))

        pulse = 0.5 + 0.5 * math.sin(self.t * 5)
        for i, it in enumerate(self.items):
            if it["key"] in self.procs:
                self.cv.itemconfig(self.tile_dot[i], fill=blend(DIM, VIOLET_L, pulse))

        self.update_meteor()
        if self.toasts:
            self.update_toasts()
        self.root.after(FPS_MS, self.tick)

    def update_meteor(self):
        """Редкий метеор по фону — как на сайте."""
        px, cv = self.p.px, self.cv
        now = time.time()
        if self.meteor is None and now >= self.next_meteor:
            angle = math.radians(random.uniform(25, 38))
            self.meteor = {"x": random.uniform(W * 0.35, W * 1.05), "y": random.uniform(-20, H * 0.3),
                           "vx": -math.cos(angle) * 11, "vy": math.sin(angle) * 11, "life": 0, "max": 42}
        cv.delete("meteor")
        if self.meteor is None:
            return
        m = self.meteor
        m["life"] += 1
        m["x"] += m["vx"]
        m["y"] += m["vy"]
        t = m["life"] / m["max"]
        alpha = t / 0.2 if t < 0.2 else 1 - (t - 0.2) / 0.8
        segs = 8
        for k in range(segs):
            a = 1 - k / segs
            x1, y1 = m["x"] - m["vx"] * k * 1.6, m["y"] - m["vy"] * k * 1.6
            x2, y2 = m["x"] - m["vx"] * (k + 1) * 1.6, m["y"] - m["vy"] * (k + 1) * 1.6
            col = blend(BG, blend(VIOLET_L, "#ffffff", a), max(0.0, alpha * a))
            cv.create_line(px(x1), px(y1), px(x2), px(y2), fill=col, width=max(1, px(1.6)),
                           capstyle="round", tags=("meteor",))
        cv.tag_lower("meteor", "ui")
        cv.tag_raise("meteor", "bg")
        if m["life"] >= m["max"]:
            self.meteor = None
            cv.delete("meteor")
            self.next_meteor = now + random.uniform(5, 10)


if __name__ == "__main__":
    Launcher()
