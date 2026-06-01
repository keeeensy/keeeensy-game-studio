import pygame, sys, math, random, traceback, os, array, struct

W, H = 900, 600
FPS = 60
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=4)
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Zombie Survival")
clock = pygame.time.Clock()
font_lg = pygame.font.SysFont("segoeui", 72, bold=True)
font_md = pygame.font.SysFont("segoeui", 36, bold=True)
font_sm = pygame.font.SysFont("segoeui", 24)
font_tiny = pygame.font.SysFont("segoeui", 16)

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

def load_sprite(path, scale=1):
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        if scale != 1:
            w, h = img.get_width(), img.get_height()
            img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
        return img
    return None

sprites_dir = os.path.join(base_dir, "sprites")
zombie_img = load_sprite(os.path.join(sprites_dir, "zombie.png"))
player_sheet = load_sprite(os.path.join(sprites_dir, "player_new.png"))
if player_sheet:
    player_sprite = player_sheet.subsurface((0, 0, 48, 48))
    player_sprite = pygame.transform.scale(player_sprite, (48, 48))
else:
    player_sprite = None

volume = 0.5

DARK_BG = (25, 2, 6)

def make_sound(freq, duration, wave_type="square", vol=0.3):
    n_samples = int(22050 * duration)
    buf = array.array('h', [0]) * n_samples
    for i in range(n_samples):
        t = i / 22050.0
        if wave_type == "square":
            val = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        elif wave_type == "noise":
            val = random.uniform(-1, 1)
        elif wave_type == "sweep":
            f = freq + (freq * 2 - freq) * (t / duration)
            val = math.sin(2 * math.pi * f * t)
        elif wave_type == "chime":
            val = math.sin(2 * math.pi * freq * t) * math.exp(-t * 3)
            val += math.sin(2 * math.pi * freq * 1.5 * t) * math.exp(-t * 4) * 0.5
        else:
            val = math.sin(2 * math.pi * freq * t)
        envelope = 1.0 - t / duration if duration > 0 else 0
        buf[i] = int(val * envelope * vol * 0.8 * 32767)
    return pygame.mixer.Sound(buffer=buf.tobytes())

snd_shoot = make_sound(800, 0.08, "sweep", 0.25)
snd_hit = make_sound(100, 0.15, "square", 0.4)
snd_kill = make_sound(200, 0.1, "noise", 0.3)
snd_wave = make_sound(523, 0.3, "chime", 0.3)

particles = []
for _ in range(80):
    particles.append({
        "x": random.uniform(0, W),
        "y": random.uniform(0, H),
        "size": random.uniform(1, 3),
        "speed": random.uniform(10, 30),
        "angle": random.uniform(0, math.pi * 2),
        "phase": random.uniform(0, math.pi * 2),
        "base_alpha": random.uniform(100, 220),
    })

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

class SettingsMenu:
    def __init__(self):
        self.sel = 0
        self.dragging = False

    def run(self):
        global volume
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    sr = pygame.Rect(W // 2 - 100, 250, 200, 20)
                    if sr.collidepoint(mx, my):
                        self.dragging = True
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.dragging = False
                if event.type == pygame.MOUSEMOTION and self.dragging:
                    mx = event.pos[0]
                    volume = max(0, min(1, (mx - (W // 2 - 100)) / 200))
                    pygame.mixer.music.set_volume(volume)
                    snd_shoot.set_volume(volume)
                    snd_hit.set_volume(volume)
                    snd_kill.set_volume(volume)
                    snd_wave.set_volume(volume)
                if event.type == pygame.MOUSEWHEEL:
                    volume = max(0, min(1, volume + event.y * 0.05))
                    pygame.mixer.music.set_volume(volume)
                    snd_shoot.set_volume(volume)
                    snd_hit.set_volume(volume)
                    snd_kill.set_volume(volume)
                    snd_wave.set_volume(volume)
            self.draw()
            clock.tick(FPS)

    def draw(self):
        screen.fill(DARK_BG)
        t = font_md.render("Настройки", True, (255, 255, 255))
        screen.blit(t, t.get_rect(center=(W // 2, 100)))
        lbl = font_sm.render("Громкость", True, (255, 255, 255))
        screen.blit(lbl, lbl.get_rect(center=(W // 2, 200)))
        sr = pygame.Rect(W // 2 - 100, 250, 200, 20)
        pygame.draw.rect(screen, (50, 50, 50), sr, border_radius=4)
        fr = pygame.Rect(W // 2 - 100, 250, int(200 * volume), 20)
        pygame.draw.rect(screen, (60, 160, 220), fr, border_radius=4)
        pygame.draw.rect(screen, (150, 150, 150), sr, 2, border_radius=4)
        pct = font_sm.render(f"{int(volume * 100)}%", True, (255, 255, 255))
        screen.blit(pct, pct.get_rect(center=(W // 2, 290)))
        esc = font_tiny.render("ESC — назад", True, (200, 200, 200))
        screen.blit(esc, esc.get_rect(center=(W // 2, H - 30)))
        pygame.display.flip()

class Menu:
    def __init__(self):
        self.items = ["Играть", "Настройки", "Выход"]
        self.sel = 0
        self.scroll = 0

    def run(self):
        while True:
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
                    mx, my = event.pos
                    for i, item in enumerate(self.items):
                        r = pygame.Rect(W // 2 - 100, 280 + i * 60, 200, 44)
                        if r.collidepoint(mx, my):
                            self.sel = i
                            return str(i)
            self.draw()
            clock.tick(FPS)

    def draw(self):
        mx, my = pygame.mouse.get_pos()
        screen.fill(DARK_BG)
        title = font_md.render("Zombie Survival", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(W // 2, 100)))
        for i, item in enumerate(self.items):
            r = pygame.Rect(W // 2 - 100, 280 + i * 60, 200, 44)
            hovered = r.collidepoint(mx, my)
            if hovered:
                self.sel = i
            c = (255, 255, 255) if i == self.sel else (180, 180, 180)
            if i == self.sel:
                pygame.draw.rect(screen, (30, 40, 60), r, border_radius=8)
                pygame.draw.rect(screen, (60, 160, 220), r, 2, border_radius=8)
            txt = font_sm.render(item, True, c)
            screen.blit(txt, txt.get_rect(center=r.center))
        pygame.display.flip()

class UpgradeMenu:
    def __init__(self, stats):
        self.stats = stats
        self.items = [
            ("Урон", 10, "damage", "+25% урона"),
            ("Скорость стрельбы", 10, "fire_rate", "+20% скорости"),
            ("Скорость", 10, "speed", "+15% передвижения"),
            ("Макс. HP", 10, "max_hp", "+20 HP"),
        ]
        self.sel = 0
        self.scroll = 0

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_w, pygame.K_UP):
                        self.sel = (self.sel - 1) % len(self.items)
                    if event.key in (pygame.K_s, pygame.K_DOWN):
                        self.sel = (self.sel + 1) % len(self.items)
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return self.items[self.sel][2]
                    if event.key == pygame.K_ESCAPE:
                        return None
                if event.type == pygame.MOUSEWHEEL:
                    self.scroll += event.y
                    self.sel = max(0, min(len(self.items) - 1, self.scroll))
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    for i, item in enumerate(self.items):
                        r = pygame.Rect(W // 2 - 150, 180 + i * 70, 300, 55)
                        if r.collidepoint(mx, my):
                            self.sel = i
                            return self.items[i][2]
            self.draw()
            clock.tick(FPS)

    def draw(self):
        screen.fill(DARK_BG)
        t = font_md.render("Выберите улучшение", True, (255, 255, 255))
        screen.blit(t, t.get_rect(center=(W // 2, 50)))
        pts = self.stats.get("points", 1)
        pt_txt = font_sm.render(f"Очки улучшений: {pts}", True, (255, 255, 255))
        screen.blit(pt_txt, pt_txt.get_rect(center=(W // 2, 100)))
        for i, (name, cost, key, desc) in enumerate(self.items):
            r = pygame.Rect(W // 2 - 150, 180 + i * 70, 300, 55)
            hl = i == self.sel
            bg = (50, 30, 30) if hl else (30, 20, 20)
            pygame.draw.rect(screen, bg, r, border_radius=6)
            if hl:
                pygame.draw.rect(screen, (200, 150, 50), r, 2, border_radius=6)
            lvl = self.stats.get(key, 1)
            nm = font_sm.render(f"{name} Ур.{lvl}", True, (255, 255, 255) if hl else (200, 200, 200))
            screen.blit(nm, (r.x + 12, r.y + 6))
            ds = font_tiny.render(desc, True, (200, 200, 200))
            screen.blit(ds, (r.x + 12, r.y + 30))
        esc = font_tiny.render("ESC — пропустить", True, (200, 200, 200))
        screen.blit(esc, esc.get_rect(center=(W // 2, H - 30)))
        pygame.display.flip()

class Bullet:
    def __init__(self, x, y, angle, damage, color=None):
        self.x, self.y = x, y
        self.angle = angle
        self.speed = 500
        self.damage = damage
        self.radius = 4
        self.alive = True
        self.color = color or (255, 255, 100)

    def update(self, dt):
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt
        if self.x < -20 or self.x > W + 20 or self.y < -20 or self.y > H + 20:
            self.alive = False

    def draw(self, surf):
        pygame.draw.circle(surf, (255, 255, 100), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, (255, 200, 50), (int(self.x), int(self.y)), self.radius, 1)

class Enemy:
    images = {}

    @classmethod
    def init_images(cls):
        if zombie_img:
            cls.images["normal"] = pygame.transform.scale(zombie_img, (32, 32))
            cls.images["fast"] = pygame.transform.scale(zombie_img, (24, 24))
            cls.images["tank"] = pygame.transform.scale(zombie_img, (44, 44))
            cls.images["spitter"] = pygame.transform.scale(zombie_img, (28, 28))
            for key in cls.images:
                cls.images[key] = pygame.transform.flip(cls.images[key], True, False)

    def __init__(self, x, y, etype):
        self.x, self.y = x, y
        self.type = etype
        if etype == "normal":
            self.hp = 30
            self.max_hp = 30
            self.speed = 80
            self.damage = 10
            self.radius = 16
            self.color = (60, 140, 60)
        elif etype == "fast":
            self.hp = 15
            self.max_hp = 15
            self.speed = 150
            self.damage = 7
            self.radius = 12
            self.color = (180, 180, 50)
        elif etype == "tank":
            self.hp = 100
            self.max_hp = 100
            self.speed = 50
            self.damage = 20
            self.radius = 22
            self.color = (100, 40, 40)
        elif etype == "spitter":
            self.hp = 20
            self.max_hp = 20
            self.speed = 60
            self.damage = 5
            self.radius = 14
            self.color = (120, 60, 140)
            self.shoot_timer = 0
        else:
            self.hp = 30
            self.max_hp = 30
            self.speed = 80
            self.damage = 10
            self.radius = 16
            self.color = (60, 140, 60)
        self.projectiles = []
        self.alive = True
        self.hit_flash = 0

    def update(self, dt, px, py):
        dx, dy = px - self.x, py - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            dx, dy = dx / dist, dy / dist
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt
        if self.hit_flash > 0:
            self.hit_flash -= dt
        if self.type == "spitter":
            self.shoot_timer -= dt
            if self.shoot_timer <= 0 and dist < 300:
                self.shoot_timer = random.uniform(1.5, 3.0)
                sp = Bullet(self.x, self.y, math.atan2(py - self.y, px - self.x), 5)
                sp.speed = 200
                sp.radius = 5
                sp.color = (180, 100, 200)
                self.projectiles.append(sp)
        for sp in self.projectiles[:]:
            sp.update(dt)
            if not sp.alive:
                self.projectiles.remove(sp)

    def draw(self, surf):
        c = self.color
        if self.hit_flash > 0:
            c = (255, 255, 255)
        img = self.images.get(self.type)
        if img:
            tinted = img.copy()
            tinted.fill(c, special_flags=pygame.BLEND_MULT)
            r = tinted.get_rect(center=(int(self.x), int(self.y)))
            surf.blit(tinted, r)
        bw = self.radius * 2
        pygame.draw.rect(surf, (40, 40, 40), (self.x - bw // 2, self.y - self.radius - 12, bw, 4))
        hp_pct = self.hp / self.max_hp
        hp_c = (int(200 * (1 - hp_pct)), int(200 * hp_pct), 30)
        pygame.draw.rect(surf, hp_c, (self.x - bw // 2, self.y - self.radius - 12, bw * hp_pct, 4))
        for sp in self.projectiles:
            pygame.draw.circle(surf, sp.color, (int(sp.x), int(sp.y)), sp.radius)

Enemy.init_images()

def main():
    if not splash(): return
    menu = Menu()
    while True:
        res = menu.run()
        if res == "quit": break
        if res == "0":
            try:
                run_game()
            except Exception as e:
                with open("crash.log", "w", encoding="utf-8") as f:
                    f.write(f"Zombie Survival Crash Log\n")
                    f.write(f"{type(e).__name__}: {e}\n")
                    traceback.print_exc(file=f)
                screen.fill((0, 0, 0))
                t = font_sm.render(f"Ошибка: {e}", True, (200, 40, 40))
                screen.blit(t, t.get_rect(center=(W // 2, H // 2)))
                pygame.display.flip()
                pygame.time.wait(3000)
        elif res == "1":
            sm = SettingsMenu()
            sm.run()
        elif res == "2":
            break
    pygame.quit()
    sys.exit()

def run_game():
    stats = {"damage": 1, "fire_rate": 1, "speed": 1, "max_hp": 1, "points": 0}
    player_x = 60
    player_y = H // 2
    player_radius = 16
    player_hp = 100
    player_max_hp = 100
    player_speed = 200
    bullets = []
    enemies = []
    wave = 0
    score = 0
    wave_timer = 0.5
    enemies_in_wave = 0
    enemies_spawned = 0
    shoot_cooldown = 0
    spawn_timer = 0
    running = True
    paused = False
    damage_flash = 0.0
    hit_sound_cooldown = 0.0
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((20, 20, 20, 180))
    flash_surf = pygame.Surface((W, H), pygame.SRCALPHA)


    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                if paused and event.key == pygame.K_q:
                    return

        if paused:
            s = pygame.Surface((W, H), pygame.SRCALPHA)
            s.fill((0, 0, 0, 160))
            screen.blit(s, (0, 0))
            t = font_md.render("ПАУЗА", True, (255, 255, 255))
            screen.blit(t, t.get_rect(center=(W // 2, H // 2)))
            t2 = font_tiny.render("ESC — продолжить | Q — выход", True, (180, 180, 180))
            screen.blit(t2, t2.get_rect(center=(W // 2, H // 2 + 40)))
            pygame.display.flip()
            continue

        damage_flash = max(0, damage_flash - dt)
        hit_sound_cooldown = max(0, hit_sound_cooldown - dt)

        keys = pygame.key.get_pressed()
        dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy = 1
        spd = player_speed * (1 + stats["speed"] * 0.15)
        player_y = max(player_radius, min(H - player_radius, player_y + dy * spd * dt))

        shoot_cooldown -= dt
        mx, my = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and shoot_cooldown <= 0:
            angle = math.atan2(my - player_y, mx - player_x)
            dmg = 15 * (1 + stats["damage"] * 0.25)
            bullets.append(Bullet(player_x, player_y, angle, dmg))
            snd_shoot.play()
            shoot_cooldown = 0.3 / (1 + stats["fire_rate"] * 0.2)

        for b in bullets[:]:
            b.update(dt)
            if not b.alive:
                bullets.remove(b)
                continue
            for e in enemies[:]:
                if math.hypot(b.x - e.x, b.y - e.y) < e.radius + b.radius:
                    e.hp -= b.damage
                    e.hit_flash = 0.1
                    b.alive = False
                    if e.hp <= 0:
                        e.alive = False
                        enemies.remove(e)
                        snd_kill.play()
                        score += 10 * (1 + (1 if e.type == "tank" else 0) * 2)
                    break

        for e in enemies[:]:
            e.update(dt, player_x, player_y)
            for sp in e.projectiles[:]:
                if math.hypot(sp.x - player_x, sp.y - player_y) < player_radius + sp.radius:
                    player_hp -= sp.damage
                    damage_flash = max(damage_flash, 0.2)
                    snd_hit.play()
                    sp.alive = False
                    e.projectiles.remove(sp)
            if math.hypot(e.x - player_x, e.y - player_y) < player_radius + e.radius:
                player_hp -= e.damage * dt
                damage_flash = max(damage_flash, 0.3)
                if player_hp > 0 and hit_sound_cooldown <= 0:
                    snd_hit.play()
                    hit_sound_cooldown = 0.3
                if player_hp <= 0:
                    show_death(score, wave)
                    return

        if len(enemies) == 0:
            wave_timer -= dt
            if wave_timer <= 0:
                wave += 1
                enemies_in_wave = 5 + wave * 3
                enemies_spawned = 0
                wave_timer = max(0.3, 1.5 - wave * 0.1)
                if wave > 1:
                    stats["points"] = stats.get("points", 0) + 1
                    um = UpgradeMenu(stats)
                    choice = um.run()
                    if choice and choice in stats:
                        stats[choice] += 1
                    player_max_hp = 100 + (stats["max_hp"] - 1) * 20
                    player_hp = min(player_max_hp, player_hp + 30)
                    snd_wave.play()

        if enemies_spawned < enemies_in_wave:
            spawn_timer -= dt
            if spawn_timer <= 0:
                spawn_interval = max(0.15, 0.6 - wave * 0.03)
                spawn_timer = spawn_interval
                enemies_spawned += 1
                sx, sy = W + 30, random.randint(30, H - 30)
                types = ["normal"]
                if wave >= 2: types.append("fast")
                if wave >= 3: types.append("tank")
                if wave >= 4: types.append("spitter")
                etype = random.choice(types)
                enemies.append(Enemy(sx, sy, etype))

        screen.fill((20, 20, 25))
        t = pygame.time.get_ticks() / 1000.0
        for p in particles:
            p["x"] += math.cos(p["angle"]) * p["speed"] * dt * 0.3
            p["y"] += math.sin(p["angle"]) * p["speed"] * dt * 0.3
            p["angle"] += random.uniform(-0.3, 0.3) * dt
            if p["x"] < -5: p["x"] = W + 5
            if p["x"] > W + 5: p["x"] = -5
            if p["y"] < -5: p["y"] = H + 5
            if p["y"] > H + 5: p["y"] = -5
            alpha = int(p["base_alpha"] * (0.5 + 0.5 * math.sin(t * 2 + p["phase"])))
            c = (255, 255, 255, max(0, min(255, alpha)))
            sz = int(p["size"])
            pygame.draw.circle(screen, c[:3], (int(p["x"]), int(p["y"])), sz)
        for e in enemies:
            e.draw(screen)
        for b in bullets:
            b.draw(screen)
        if player_sprite:
            pr = player_sprite.get_rect(center=(int(player_x), int(player_y)))
            screen.blit(player_sprite, pr)
        else:
            player_rect = pygame.Rect(int(player_x) - player_radius, int(player_y) - player_radius - 8, player_radius * 2, player_radius * 2 + 8)
            pygame.draw.ellipse(screen, (80, 180, 220), player_rect)
            pygame.draw.ellipse(screen, (120, 210, 240), player_rect, 2)

        for i in range(int(player_max_hp / 10)):
            hx = 10 + i * 14
            filled = player_hp > i * 10
            c = (200, 60, 60) if filled else (40, 40, 40)
            pygame.draw.rect(screen, c, (hx, 10, 12, 14))
            pygame.draw.rect(screen, (100, 100, 100), (hx, 10, 12, 14), 1)
        if damage_flash > 0:
            flash_alpha = int(80 * (damage_flash / 0.3))
            flash_surf.fill((180, 0, 0, min(flash_alpha, 80)))
            screen.blit(flash_surf, (0, 0))
        screen.blit(font_sm.render(f"Волна: {wave}", True, (200, 200, 200)), (10, 30))
        screen.blit(font_sm.render(f"Счёт: {score}", True, (200, 200, 200)), (10, 55))
        screen.blit(font_sm.render(f"Врагов: {len(enemies)}", True, (180, 180, 180)), (10, 80))

        if len(enemies) == 0 and wave_timer > 0:
            screen.blit(overlay, (0, 0))
            wt = font_lg.render(f"Волна {wave + 1} пройдена!", True, (200, 200, 100))
            screen.blit(wt, wt.get_rect(center=(W // 2, H // 2)))
            wave_timer_display = max(0, int(wave_timer * 10)) / 10
            st = font_sm.render(f"Следующая через {wave_timer_display:.1f}с", True, (150, 150, 150))
            screen.blit(st, st.get_rect(center=(W // 2, H // 2 + 50)))

        cross = font_sm.render("+", True, (255, 255, 255))
        cr = cross.get_rect(center=(mx, my))
        screen.blit(cross, cr)
        pygame.display.flip()

def show_death(score, wave):
    screen.fill((0, 0, 0))
    t = font_lg.render("Вы погибли!", True, (200, 40, 40))
    screen.blit(t, t.get_rect(center=(W // 2, H // 2 - 40)))
    s = font_sm.render(f"Счёт: {score} | Волна: {wave}", True, (200, 200, 200))
    screen.blit(s, s.get_rect(center=(W // 2, H // 2 + 20)))
    h = font_tiny.render("Нажмите любую клавишу", True, (120, 120, 120))
    screen.blit(h, h.get_rect(center=(W // 2, H // 2 + 60)))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.KEYDOWN: waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN: waiting = False

if __name__ == "__main__":
    main()
