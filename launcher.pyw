import tkinter as tk
from tkinter.font import Font
import subprocess, os, math, random, sys

BASE = os.path.dirname(os.path.abspath(__file__))
W, H = 1100, 700

BG1, BG2 = "#0f0f1a", "#1a1a30"
ACCENT = "#4A7CFF"
ACCENT_HOVER = "#6B96FF"
WHITE = "#FFFFFF"
MUTED = "#8888A0"
DIM = "#555570"
CARD = "#1e1e38"
CARD_BORDER = "#2a2a48"
RED = "#E05050"
YELLOW = "#F0C040"

GAMES = [
    {"name": "Gem Hunter 2D",   "emoji": "💎",
     "exe": os.path.join(BASE, "gem_hunter", "dist", "gem_hunter.exe"),
     "alt": os.path.join(BASE, "gem_hunter", "main.py"),
     "desc": "Собирай сферы в 2D лабиринте\n15 уровней \u00b7 враги \u00b7 ачивки \u00b7 редактор",
     "color": "#4A7CFF"},
    {"name": "Gem Hunter 3D",   "emoji": "\U0001f9ca",
     "exe": os.path.join(BASE, "3d_maze", "maze_run_3d.exe"),
     "alt": None,
     "desc": "3D лабиринт от первого лица\n10 уровней \u00b7 враги \u00b7 миникарта \u00b7 raylib",
     "color": "#40C057"},
    {"name": "Zombie Survival", "emoji": "\U0001f9df",
     "exe": os.path.join(BASE, "zombie_survival", "dist", "zombie_survival", "zombie_survival.exe"),
     "alt": None,
     "desc": "Волновая survival-игра\n4 типа зомби \u00b7 апгрейды \u00b7 процедурный звук",
     "color": "#E05050"},
]

MC_PROFILES = [
    {"name": "RPG Levels",  "emoji": "\u2694\ufe0f", "profile": "rpg_levels",    "color": "#F0C040"},
    {"name": "Death Marker","emoji": "\u2620\ufe0f", "profile": "death_marker",  "color": "#A855F7"},
    {"name": "All Mods",    "emoji": "\U0001f9e9", "profile": "all_mods",      "color": "#4A7CFF"},
    {"name": "Vanilla",     "emoji": "\U0001f7e6", "profile": "vanilla",       "color": "#8888A0"},
]

PARTICLE_COUNT = 40


class Launcher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Keeeensy Launcher")
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
        self.root.overrideredirect(True)
        self.root.resizable(False, False)
        self.root.configure(bg=BG1)

        self.selected = 0
        self.t = 0.0
        self.mc_expanded = False
        self.hover_play = -1
        self.hover_mc = -1
        self.hover_close = False
        self._drag_start = None

        self.font_lg = Font(family="Segoe UI", size=20, weight="bold")
        self.font_md = Font(family="Segoe UI", size=15)
        self.font_sm = Font(family="Segoe UI", size=12)
        self.font_xs = Font(family="Segoe UI", size=10)

        self.font_emoji_lg = Font(family="Segoe UI", size=48)
        self.font_emoji_md = Font(family="Segoe UI", size=18)

        self.particles = []
        for _ in range(PARTICLE_COUNT):
            self.particles.append({
                "x": random.uniform(0, W), "y": random.uniform(0, H),
                "vx": random.uniform(-4, 4), "vy": random.uniform(-3, 3),
                "r": random.uniform(1.5, 3),
                "bright": random.uniform(0.3, 0.7),
                "phase": random.uniform(0, math.tau),
            })

        self.cv = tk.Canvas(self.root, width=W, height=H, highlightthickness=0, bg=BG1)
        self.cv.pack(fill="both", expand=True)

        self.cv.bind("<Button-1>", self.on_click)
        self.cv.bind("<B1-Motion>", self.on_drag)
        self.cv.bind("<ButtonPress-1>", self.on_press, add="+")
        self.cv.bind("<Button-3>", lambda e: self.root.destroy())
        self.cv.bind("<Motion>", self.on_motion)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.root.after(20, self.anim_loop)
        self.root.mainloop()

    @staticmethod
    def blend(c1, c2, t):
        def ch(c, i): return int(c.lstrip("#")[i:i+2], 16)
        r = int(ch(c1, 0) * (1-t) + ch(c2, 0) * t)
        g = int(ch(c1, 2) * (1-t) + ch(c2, 2) * t)
        b = int(ch(c1, 4) * (1-t) + ch(c2, 4) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def dim(hexc, factor):
        h = hexc.lstrip("#")
        r = int(int(h[0:2], 16) * factor)
        g = int(int(h[2:4], 16) * factor)
        b = int(int(h[4:6], 16) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def anim_loop(self):
        self.t += 0.02
        try:
            self.cv.delete("all")
            self.draw_bg()
            self.draw_particles()
            self.draw_titlebar()
            self.draw_sidebar()
            self.draw_content()
            self.draw_mc_section()
            self.draw_close_btn()
        except Exception:
            pass
        self.root.after(20, self.anim_loop)

    def draw_bg(self):
        for y in range(0, H, 4):
            t = y / H
            self.cv.create_rectangle(0, y, W, y+4,
                                     fill=self.blend(BG1, BG2, t),
                                     outline="")

    def draw_particles(self):
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["x"] < 0: p["x"] = W
            if p["x"] > W: p["x"] = 0
            if p["y"] < 0: p["y"] = H
            if p["y"] > H: p["y"] = 0
            brightness = p["bright"] * (0.7 + 0.3 * math.sin(self.t * 2 + p["phase"]))
            grey = int(255 * brightness)
            col = f"#{grey:02x}{grey:02x}{grey:02x}"
            r = p["r"]
            self.cv.create_oval(p["x"]-r, p["y"]-r, p["x"]+r, p["y"]+r,
                                fill=col, outline="")

    def draw_titlebar(self):
        self.cv.create_text(20, 18, text="Keeeensy Launcher",
                            fill=ACCENT, font=self.font_md, anchor="w")
        self.cv.create_text(20, 38, text="Выбери проект для запуска",
                            fill=MUTED, font=self.font_xs, anchor="w")

    def draw_close_btn(self):
        cx, cy, r = W-24, 24, 12
        col = RED if self.hover_close else DIM
        self.cv.create_oval(cx-r, cy-r, cx+r, cy+r, fill=col, outline="")
        self.cv.create_text(cx, cy, text="✕", fill=WHITE, font=self.font_sm)

    def draw_sidebar(self):
        sx, si = 50, 85
        for i, g in enumerate(GAMES):
            cy = 100 + i * si
            sel = i == self.selected
            glow = 6 * (0.5 + 0.5 * math.sin(self.t * 3 + i * 2.5))
            r = 24 + (glow if sel else 0)
            if sel:
                self.cv.create_oval(sx-r, cy-r, sx+r, cy+r,
                                    fill=g["color"], outline="")
            else:
                self.cv.create_oval(sx-r, cy-r, sx+r, cy+r,
                                    fill="", outline=DIM, width=2)
            self.cv.create_text(sx, cy, text=g["emoji"],
                                font=self.font_emoji_md if sel else self.font_sm)

    def draw_content(self):
        g = GAMES[self.selected]
        cx, cy = 140, 85
        pw = W - cx - 40

        self.cv.create_rectangle(cx, cy, cx+pw, cy+220,
                                 fill=CARD, outline=CARD_BORDER, width=1)

        bounce = 3 * math.sin(self.t * 4)
        self.cv.create_text(cx+60, cy+60+bounce,
                            text=g["emoji"], font=self.font_emoji_lg)

        self.cv.create_text(cx+125, cy+45, text=g["name"],
                            fill=WHITE, font=self.font_lg, anchor="w")

        for i, line in enumerate(g["desc"].split("\n")):
            self.cv.create_text(cx+125, cy+85+i*28, text=line,
                                fill=MUTED, font=self.font_sm, anchor="w")

        btn_x, btn_y = cx+20, cy+170
        bw, bh = 180, 42
        hover = self.hover_play == self.selected
        col = ACCENT_HOVER if hover else ACCENT
        self.cv.create_rectangle(btn_x, btn_y, btn_x+bw, btn_y+bh,
                                 fill=col, outline="")
        self.cv.create_text(btn_x+bw//2, btn_y+bh//2,
                            text="\u25b6  Play", fill=WHITE,
                            font=self.font_md)

        self.cv.create_text(cx+pw-15, cy+15,
                            text=f"{self.selected+1}/{len(GAMES)}",
                            fill=DIM, font=self.font_xs)

        by = cy + 240
        self.cv.create_rectangle(cx, by, cx+pw, by+110,
                                 fill=CARD, outline=CARD_BORDER, width=1)
        self.cv.create_text(cx+15, by+15, text="Другие проекты",
                            fill=WHITE, font=self.font_sm, anchor="w")

        oi = 0
        for i, og in enumerate(GAMES):
            if i == self.selected:
                continue
            ox, oy2 = cx+15 + oi*180, by+50
            ow, oh = 165, 48
            hover_o = self.hover_play == 100 + i
            bg_o = self.blend(CARD, og["color"], 0.15) if hover_o else CARD
            bo = og["color"] if hover_o else CARD_BORDER
            self.cv.create_rectangle(ox, oy2, ox+ow, oy2+oh,
                                     fill=bg_o, outline=bo)
            self.cv.create_text(ox+22, oy2+oh//2,
                                text=og["emoji"], font=self.font_sm)
            self.cv.create_text(ox+40, oy2+oh//2-6,
                                text=og["name"], fill=MUTED,
                                font=self.font_xs, anchor="w")
            self.cv.create_text(ox+40, oy2+oh//2+10,
                                text="\u25b6", fill=og["color"],
                                font=self.font_xs, anchor="w")
            oi += 1

    def draw_mc_section(self):
        cx, cy = 140, 440
        pw = W - cx - 40
        mh = 215

        self.cv.create_rectangle(cx, cy, cx+pw, cy+mh,
                                 fill=CARD, outline=CARD_BORDER, width=1)

        arrow = "\u25bc" if self.mc_expanded else "\u25b6"
        self.cv.create_text(cx+15, cy+20, text=arrow,
                            fill=YELLOW, font=self.font_sm, anchor="w")
        self.cv.create_text(cx+35, cy+20, text="Minecraft (Fabric)",
                            fill=WHITE, font=self.font_md, anchor="w")
        self.cv.create_text(cx+pw-15, cy+20, text="\u26a1",
                            fill=YELLOW, font=self.font_sm, anchor="e")

        if self.mc_expanded:
            for i, mp in enumerate(MC_PROFILES):
                col = i % 2
                row = i // 2
                cw = (pw - 50) // 2
                ch = 60
                gap = 12
                mx = cx + 20 + col * (cw + gap)
                my = cy + 50 + row * (ch + gap)
                hover = self.hover_mc == i
                bg = self.blend(CARD, mp["color"], 0.2) if hover else CARD
                bo = mp["color"] if hover else CARD_BORDER
                self.cv.create_rectangle(mx, my, mx+cw, my+ch,
                                         fill=bg, outline=bo)
                self.cv.create_text(mx+25, my+ch//2,
                                    text=mp["emoji"], font=self.font_sm)
                self.cv.create_text(mx+45, my+ch//2-7,
                                    text=mp["name"], fill=WHITE,
                                    font=self.font_sm, anchor="w")
                self.cv.create_text(mx+45, my+ch//2+10,
                                    text=f"{mp['profile']}",
                                    fill=mp["color"],
                                    font=self.font_xs, anchor="w")
        else:
            one = "  ".join([f"{mp['emoji']} {mp['name']}" for mp in MC_PROFILES])
            self.cv.create_text(cx+15, cy+52, text=one,
                                fill=MUTED, font=self.font_xs, anchor="w")

    def launch_game(self, idx):
        g = GAMES[idx]
        path = g["exe"]
        if os.path.exists(path):
            subprocess.Popen([path], cwd=os.path.dirname(path))
        elif g["alt"]:
            subprocess.Popen([sys.executable, g["alt"]],
                             cwd=os.path.dirname(g["alt"]))
        else:
            self.cv.create_text(W//2, 60, text=f"\u274c {g['name']} не найден",
                                fill=RED, font=self.font_md)

    def launch_mc(self, idx):
        mp = MC_PROFILES[idx]
        launcher = os.path.join(BASE, "minecraft_profiles", "launch_fabric.ps1")
        if os.path.exists(launcher):
            subprocess.Popen([
                "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-File", launcher, "-Profile", mp["profile"]
            ], cwd=os.path.join(BASE, "minecraft_profiles"))

    def on_motion(self, e):
        self.hover_close = ((e.x - (W-24))**2 + (e.y - 24)**2) < 256
        self.hover_play = -1
        self.hover_mc = -1

        if 160 <= e.x <= 340 and 255 <= e.y <= 297:
            self.hover_play = self.selected

        oi = 0
        for i in range(len(GAMES)):
            if i == self.selected:
                continue
            ox, oy = 155 + oi*180, 325
            if ox <= e.x <= ox+165 and oy <= e.y <= oy+48:
                self.hover_play = 100 + i
            oi += 1

        if self.mc_expanded:
            cx, cy = 140, 440
            pw = W - cx - 40
            for i in range(len(MC_PROFILES)):
                col = i % 2
                row = i // 2
                cw = (pw - 50) // 2
                ch = 60
                gap = 12
                mx = cx + 20 + col * (cw + gap)
                my = cy + 50 + row * (ch + gap)
                if mx <= e.x <= mx+cw and my <= e.y <= my+ch:
                    self.hover_mc = i

    def on_press(self, e):
        self._drag_start = (e.x, e.y)

    def on_drag(self, e):
        if self._drag_start:
            dx, dy = self._drag_start
            self.root.geometry(f"+{e.x_root-dx}+{e.y_root-dy}")

    def on_click(self, e):
        if self.hover_close:
            self.root.destroy()
            return

        if self.hover_play >= 0:
            if self.hover_play < 100:
                self.launch_game(self.hover_play)
            else:
                self.selected = self.hover_play - 100
            return

        if self.hover_mc >= 0:
            self.launch_mc(self.hover_mc)
            return

        if 140 <= e.x <= 140+(W-140-40) and 440 <= e.y <= 477:
            self.mc_expanded = not self.mc_expanded
            return

        for i in range(len(GAMES)):
            sx, si = 50, 85
            cy = 100 + i * si
            if (e.x - sx)**2 + (e.y - cy)**2 < 900:
                self.selected = i
                return


if __name__ == "__main__":
    Launcher()
