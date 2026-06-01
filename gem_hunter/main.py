import pygame, sys, math, random
from game import Game

W, H = 800, 600
FPS = 60
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)
screen = pygame.display.set_mode((W, H), pygame.SRCALPHA)
pygame.display.set_caption("Gem Hunter 2D")
clock = pygame.time.Clock()
font_lg = pygame.font.SysFont("segoeui", 72, bold=True)
font_md = pygame.font.SysFont("segoeui", 36, bold=True)
font_sm = pygame.font.SysFont("segoeui", 24)

def splash():
    surf = pygame.Surface((W, H))
    surf.fill((255, 255, 255))
    txt = font_lg.render("Keeeensy", True, (0, 0, 0))
    r = txt.get_rect(center=(W // 2, H // 2))
    start = pygame.time.get_ticks()
    duration = 1500
    while True:
        elapsed = pygame.time.get_ticks() - start
        if elapsed >= duration:
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN: return True
            if event.type == pygame.MOUSEBUTTONDOWN: return True
        alpha = int(255 * (1 - elapsed / duration))
        surf.set_alpha(max(0, alpha - 50))
        screen.blit(surf, (0, 0))
        txt.set_alpha(alpha)
        screen.blit(txt, r)
        pygame.display.flip()
        clock.tick(60)
    return True

class Menu:
    def __init__(self):
        self.items = ["Играть", "Выбор уровня", "Редактор уровней", "Достижения", "Выход"]
        self.sel = 0
        self.scroll = 0
        self.particles = []
        for _ in range(80):
            self.particles.append({
                "x": random.uniform(0, W),
                "y": random.uniform(0, H),
                "vx": random.uniform(-20, 20),
                "vy": random.uniform(-20, 20),
                "size": random.uniform(2, 5),
                "phase": random.uniform(0, 6.28),
                "speed": random.uniform(0.5, 1.5),
                "alpha_base": random.uniform(80, 200),
            })

    def run(self):
        while True:
            mx, my = pygame.mouse.get_pos()
            dt = clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_w, pygame.K_UP):
                        self.sel = (self.sel - 1) % len(self.items)
                    if event.key in (pygame.K_s, pygame.K_DOWN):
                        self.sel = (self.sel + 1) % len(self.items)
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return str(self.sel)
                if event.type == pygame.MOUSEWHEEL:
                    self.scroll += event.y
                    self.sel = max(0, min(len(self.items) - 1, self.scroll))
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, item in enumerate(self.items):
                        r = pygame.Rect(W // 2 - 100, 280 + i * 60, 200, 44)
                        if r.collidepoint(mx, my):
                            self.sel = i
                            return str(i)
            self.sel = self._hover_button(mx, my)
            self._update_particles(dt, mx, my)
            self.draw()
            clock.tick(FPS)

    def _hover_button(self, mx, my):
        for i, item in enumerate(self.items):
            r = pygame.Rect(W // 2 - 100, 280 + i * 60, 200, 44)
            if r.collidepoint(mx, my):
                return i
        return self.sel

    def _update_particles(self, dt, mx, my):
        for p in self.particles:
            dx = p["x"] - mx
            dy = p["y"] - my
            dist = math.hypot(dx, dy)
            if dist < 200 and dist > 1:
                force = (200 - dist) / 200 * 300
                p["vx"] += (dx / dist) * force * dt
                p["vy"] += (dy / dist) * force * dt
            p["vx"] *= 0.95
            p["vy"] *= 0.98
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["phase"] += dt * 2
            if p["x"] < 0 or p["x"] > W: p["vx"] *= -1
            if p["y"] < 0 or p["y"] > H: p["vy"] *= -1

    def draw(self):
        screen.fill((15, 15, 25))
        t = pygame.time.get_ticks() / 1000
        for p in self.particles:
            alpha = int((math.sin(p["phase"] + t * 1.5) * 0.3 + 0.5) * p["alpha_base"])
            size = p["size"] * (math.sin(p["phase"] + t * 1.5) * 0.2 + 0.8)
            s = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (120, 200, 255, max(0, min(255, alpha))), (int(size), int(size)), int(size))
            screen.blit(s, (int(p["x"] - size), int(p["y"] - size)))
        for i, item in enumerate(self.items):
            r = pygame.Rect(W // 2 - 100, 280 + i * 60, 200, 44)
            hovered = i == self.sel
            if hovered:
                pygame.draw.rect(screen, (30, 40, 60), r, border_radius=8)
                pygame.draw.rect(screen, (60, 160, 220), r, 2, border_radius=8)
            txt = font_sm.render(item, True, (100, 200, 255) if hovered else (150, 150, 180))
            screen.blit(txt, txt.get_rect(center=r.center))
        title = font_md.render("Gem Hunter 2D", True, (100, 200, 255))
        screen.blit(title, title.get_rect(center=(W // 2, 80)))
        sub = font_sm.render("Собери все орбы", True, (150, 150, 180))
        screen.blit(sub, sub.get_rect(center=(W // 2, 120)))
        pygame.display.flip()

def main():
    if not splash(): return
    menu = Menu()
    g = Game(screen, clock)
    while True:
        res = menu.run()
        if res == "quit": break
        if res == "0":
            g.run("levels")
        elif res == "1":
            g.run("select")
        elif res == "2":
            g.run("editor")
        elif res == "3":
            g.show_achievements()
        elif res == "4":
            break
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
