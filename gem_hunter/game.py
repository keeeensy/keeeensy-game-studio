import pygame, json, os, math, random, struct
from collections import deque
from io import BytesIO

TILE = 60
W, H = 800, 600
COLS, ROWS = 10, 10
BASE = os.path.dirname(os.path.abspath(__file__))
LVL_DIR = os.path.join(BASE, "levels")
ACH_FILE = os.path.join(BASE, "achievements.json")
os.makedirs(LVL_DIR, exist_ok=True)

def _build_wav(samples, sr=22050):
    n = len(samples)
    bufsize = n * 2
    def _b(v):
        return struct.pack("<h", max(-32768, min(32767, int(v))))
    with BytesIO() as f:
        f.write(struct.pack("<4sI4s", b"RIFF", 36 + bufsize, b"WAVE"))
        f.write(struct.pack("<4sIHHIIHH", b"fmt ", 16, 1, 1, sr, sr * 2, 2, 16))
        f.write(struct.pack("<4sI", b"data", bufsize))
        for s in samples:
            f.write(_b(s))
        return f.getvalue()

class ProceduralAudio:
    def __init__(self):
        self.sounds = {}
        self._gen("collect", self._tone(523, 0.12, sweep=880))
        self._gen("hit", self._noise(0.15))
        self._gen("complete", self._arpeggio([523, 659, 784, 1047], 0.08))
        self._gen("enemy_hit", self._tone(200, 0.12, vol=0.3))

    def _tone(self, freq, dur, sweep=None, vol=0.5):
        sr, n = 22050, int(22050 * dur)
        samples = []
        for i in range(n):
            t = i / sr
            f = freq + (sweep - freq) * (i / n) if sweep else freq
            v = vol * 32767 * math.sin(2 * math.pi * f * t) * max(0, 1 - i / n)
            samples.append(v)
        return _build_wav(samples, sr)

    def _noise(self, dur, vol=0.4):
        sr, n = 22050, int(22050 * dur)
        samples = [vol * 32767 * (random.random() * 2 - 1) * max(0, 1 - i / n) for i in range(n)]
        return _build_wav(samples, sr)

    def _arpeggio(self, freqs, note_dur):
        sr = 22050
        samples = []
        for f in freqs:
            n = int(sr * note_dur)
            for i in range(n):
                t = i / sr
                v = 0.4 * 32767 * math.sin(2 * math.pi * f * t) * max(0, 1 - i / n)
                samples.append(v)
        return _build_wav(samples, sr)

    def _gen(self, name, data):
        s = pygame.mixer.Sound(BytesIO(data))
        self.sounds[name] = s

    def play(self, name):
        s = self.sounds.get(name)
        if s: s.play()

class TileMap:
    def __init__(self, cols, rows):
        self.cols, self.rows = cols, rows
        self.data = [[0] * cols for _ in range(rows)]

    def to_list(self):
        return self.data

    def from_list(self, data):
        self.data = data
        self.rows = len(data)
        self.cols = len(data[0]) if data else 0

    @staticmethod
    def generate(level=0):
        cols = 10 + level
        rows = 10 + level
        m = TileMap(cols, rows)
        WALL, EMPTY, DOT, EXIT, ENEMY = 1, 0, 2, 3, 4
        for y in range(rows):
            for x in range(cols):
                m.data[y][x] = WALL if (x == 0 or x == cols - 1 or y == 0 or y == rows - 1) else EMPTY

        m.data[1][1] = EMPTY
        num_walls = 4 + level * 2
        for _ in range(num_walls):
            wx = random.randint(2, cols - 3)
            wy = random.randint(2, rows - 3)
            if (wx, wy) != (1, 1):
                m.data[wy][wx] = WALL

        chunk_prob = min(0.5 + level * 0.03, 0.9)
        chunks = [(2, 2), (cols - 3, 2), (2, rows - 3), (cols - 3, rows - 3)]
        for cx, cy in chunks:
            if random.random() < chunk_prob:
                for dy in range(3):
                    for dx in range(3):
                        if 0 < cx + dx < cols - 1 and 0 < cy + dy < rows - 1:
                            if (cx + dx, cy + dy) != (1, 1):
                                m.data[cy + dy][cx + dx] = WALL

        if level >= 3:
            for _ in range((level - 2) // 2):
                bx = random.randint(3, cols - 5)
                by = random.randint(3, rows - 5)
                for dy in range(2):
                    for dx in range(2):
                        if 0 < bx + dx < cols - 1 and 0 < by + dy < rows - 1:
                            if (bx + dx, by + dy) != (1, 1):
                                m.data[by + dy][bx + dx] = WALL

        px, py = 1, 1
        m.data[py][px] = EMPTY

        q = deque()
        q.append((px, py))
        dist = {(px, py): 0}
        while q:
            cx, cy = q.popleft()
            for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                if 1 <= nx < cols - 1 and 1 <= ny < rows - 1 and (nx, ny) not in dist:
                    if m.data[ny][nx] != WALL:
                        dist[(nx, ny)] = dist[(cx, cy)] + 1
                        q.append((nx, ny))

        open_cells = [(x, y) for x, y in dist if m.data[y][x] == EMPTY and (x, y) != (px, py)]
        random.shuffle(open_cells)
        num_orbs = min(random.randint(4 + level, 7 + level * 2), max(1, int(len(open_cells) * 0.7)))
        for i in range(num_orbs):
            m.data[open_cells[i][1]][open_cells[i][0]] = DOT
        orbed = set(open_cells[:num_orbs])

        exit_candidates = [p for p in dist if p not in orbed and p != (px, py)]
        if not exit_candidates:
            exit_candidates = [p for p in dist if p != (px, py)]
        ex, ey = max(exit_candidates, key=lambda p: dist[p])
        m.data[ey][ex] = EXIT

        spots = [(x, y) for x, y in dist if m.data[y][x] == EMPTY and (x, y) != (px, py) and (x, y) != (ex, ey)]
        random.shuffle(spots)
        num_enemies = min(2 + level // 2, len(spots))
        for i in range(num_enemies):
            m.data[spots[i][1]][spots[i][0]] = ENEMY
        return m

class Entity:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.w, self.h = TILE * 0.7, TILE * 0.7

    @property
    def rect(self):
        return pygame.Rect(self.x - self.w / 2, self.y - self.h / 2, self.w, self.h)

    def collide_rect(self, other):
        return self.rect.colliderect(other.rect)

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 150
        self.gems = 0
        self.hp = 100
        self.max_hp = 100
        self.angle = 0

    def update(self, dt, keys, tilemap):
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx = 1
        if dx or dy:
            self.angle = math.atan2(dy, dx)
            ln = math.hypot(dx, dy)
            dx, dy = dx / ln, dy / ln
        sprint = 1.6 if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 1.0
        nx = self.x + dx * self.speed * sprint * dt
        ny = self.y + dy * self.speed * sprint * dt
        if not self._blocked(nx, self.y, tilemap): self.x = nx
        if not self._blocked(self.x, ny, tilemap): self.y = ny

    def _blocked(self, px, py, tilemap):
        margin = self.w * 0.4
        cx, cy = int(px // TILE), int(py // TILE)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                tx, ty = cx + dx, cy + dy
                if 0 <= tx < tilemap.cols and 0 <= ty < tilemap.rows:
                    if tilemap.data[ty][tx] == 1:
                        rx, ry = tx * TILE, ty * TILE
                        r = pygame.Rect(rx, ry, TILE, TILE)
                        pr = pygame.Rect(px - margin, py - margin, margin * 2, margin * 2)
                        if pr.colliderect(r):
                            return True
        return False

class Enemy(Entity):
    AGGRO_RADIUS = 160

    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = random.uniform(60, 100)
        self.hp = 20
        self.damage = 10
        self.attack_cooldown = 0
        self.phase = random.random() * 100
        self.angle = random.uniform(0, 6.2832)
        self.move_timer = 0

    def update(self, dt, player, tilemap):
        self.phase += dt
        self.move_timer -= dt
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        chasing = dist < self.AGGRO_RADIUS and dist > 0
        if chasing:
            self.angle = math.atan2(dy, dx)
            perp = math.sin(self.phase * 4) * 0.3
            cx = math.cos(self.angle) - math.sin(self.angle) * perp
            cy = math.sin(self.angle) + math.cos(self.angle) * perp
            ln = math.hypot(cx, cy)
            if ln > 0:
                cx, cy = cx / ln, cy / ln
        else:
            if self.move_timer <= 0:
                self.angle = random.uniform(0, 6.2832)
                self.move_timer = random.uniform(0.8, 2.5)
            self.angle += math.sin(self.phase * 3) * 0.8 * dt
            cx = math.cos(self.angle)
            cy = math.sin(self.angle)
        nx = self.x + cx * self.speed * dt
        ny = self.y + cy * self.speed * dt
        bx = self._blocked(nx, self.y, tilemap)
        by = self._blocked(self.x, ny, tilemap)
        if not bx: self.x = nx
        if not by: self.y = ny
        if (bx or by) and not chasing:
            self.angle = random.uniform(0, 6.2832)
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if dist < TILE * 0.8 and self.attack_cooldown <= 0:
            player.hp -= self.damage
            self.attack_cooldown = 1.0
            return True
        return False

    def _blocked(self, px, py, tilemap):
        margin = self.w * 0.4
        cx, cy = int(px // TILE), int(py // TILE)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                tx, ty = cx + dx, cy + dy
                if 0 <= tx < tilemap.cols and 0 <= ty < tilemap.rows:
                    if tilemap.data[ty][tx] == 1:
                        r = pygame.Rect(tx * TILE, ty * TILE, TILE, TILE)
                        pr = pygame.Rect(px - margin, py - margin, margin * 2, margin * 2)
                        if pr.colliderect(r): return True
        return False

class Game:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.audio = ProceduralAudio()
        self.font_sm = pygame.font.SysFont("segoeui", 16)
        self.font_md = pygame.font.SysFont("segoeui", 24)
        self.font_lg = pygame.font.SysFont("segoeui", 48, bold=True)
        self.ach_data = self._load_achievements()
        self.sel_save = {}
        self.shake_timer = 0.0
        self.shake_intensity = 0.0
        self.lives = 3
        self.invincible_timer = 0.0
        self.current_level = 0
        self.total_levels = 15
        self.ach_notifications = []
        self.total_gems = 0
        self.last_gems = 0
        self.ach_names = {"speedrunner": "Скороход — пройти уровень за <30с",
                          "collector": "Коллекционер — собрать 50 самоцветов",
                          "survivor": "Живучий — выжить с <5 HP",
                          "explorer": "Исследователь — пройти 3 уровня"}

    def _load_achievements(self):
        if os.path.exists(ACH_FILE):
            try:
                with open(ACH_FILE) as f: return json.load(f)
            except: pass
        return {"speedrunner": False, "collector": False, "survivor": False, "explorer": False}

    def _save_achievements(self):
        with open(ACH_FILE, "w") as f:
            json.dump(self.ach_data, f)

    def _unlock(self, key):
        if not self.ach_data.get(key):
            self.ach_data[key] = True
            self._save_achievements()
            self.ach_notifications.append({"key": key, "phase": 0.0})
            return True
        return False

    def _load_level_file(self, name):
        path = os.path.join(LVL_DIR, f"{name}.json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None

    def _save_level_file(self, name, data):
        with open(os.path.join(LVL_DIR, f"{name}.json"), "w") as f:
            json.dump(data, f)

    def _get_levels(self):
        levels = [f.replace(".json", "") for f in os.listdir(LVL_DIR) if f.endswith(".json")]
        if not levels:
            for i in range(3):
                m = TileMap.generate(COLS, ROWS)
                self._save_level_file(f"level_{i + 1}", m.to_list())
                levels.append(f"level_{i + 1}")
        return sorted(levels)

    def show_achievements(self):
        items = list(self.ach_data.items())
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE): return
                if event.type == pygame.MOUSEBUTTONDOWN: return
            self.screen.fill((20, 20, 40))
            t = self.font_md.render("Достижения", True, (200, 200, 255))
            self.screen.blit(t, t.get_rect(center=(W // 2, 50)))
            for i, (k, v) in enumerate(items):
                lbl = self.ach_names.get(k, k)
                if v:
                    self.screen.blit(self.font_sm.render('●', True, (100, 240, 100)), (100, 120 + i * 40))
                    txt = self.font_sm.render(lbl, True, (120, 120, 120))
                    self.screen.blit(txt, (118, 120 + i * 40))
                else:
                    txt = self.font_sm.render(f'○ {lbl}', True, (120, 120, 120))
                    self.screen.blit(txt, (100, 120 + i * 40))
            back = self.font_sm.render("Нажмите ESC для выхода", True, (150, 150, 150))
            self.screen.blit(back, back.get_rect(center=(W // 2, H - 40)))
            pygame.display.flip()
            self.clock.tick(60)

    def run(self, mode="levels"):
        if mode == "levels":
            self._run_game()
        elif mode == "select":
            self._run_selected()
        elif mode == "editor":
            self._run_editor()

    def _run_game(self):
        self.current_level = 0
        self.lives = 3
        self.total_gems = 0
        total_timer = 0.0
        while self.current_level < self.total_levels:
            tm = TileMap.generate(self.current_level)
            result = self._play_level(tm, self.current_level)
            if result == "quit":
                return
            if result == "game_over":
                self._show_game_over(total_timer)
                return
            if result == "complete":
                self.total_gems += self.last_gems
                if self.total_gems >= 50:
                    self._unlock("collector")
                self.current_level += 1
                if self.current_level >= self.total_levels:
                    self._show_win(total_timer)
                    self._unlock("explorer")
                    return

    def _run_selected(self):
        name = self._select_level()
        if name is None:
            return
        data = self._load_level_file(name)
        if data is None:
            return
        tm = TileMap(1, 1)
        tm.from_list(data)
        self.lives = 3
        self.current_level = 0
        result = self._play_level(tm, 0)
        if result == "game_over":
            self._show_game_over(0)
        elif result == "complete":
            pass

    def _play_level(self, tilemap, level_idx):
        player = None
        enemies = []
        exit_pos = None
        gem_count = 0
        spawn_pos = None
        for y in range(tilemap.rows):
            for x in range(tilemap.cols):
                v = tilemap.data[y][x]
                px, py = x * TILE + TILE // 2, y * TILE + TILE // 2
                if v == 3:
                    exit_pos = (x, y)
                elif v == 4:
                    enemies.append(Enemy(px, py))
                    tilemap.data[y][x] = 0
                elif v == 2:
                    gem_count += 1
                if v == 0 and spawn_pos is None:
                    spawn_pos = (px, py)
        if spawn_pos is None:
            spawn_pos = (TILE * 1.5, TILE * 1.5)
        player = Player(spawn_pos[0], spawn_pos[1])
        gems_collected = 0
        gems_total = gem_count
        doors_open = False
        start_time = pygame.time.get_ticks()
        invincible_timer = 0.0
        paused = False
        show_intro = True
        intro_timer = 1.5
        level_result = None
        while level_result is None:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if show_intro:
                            show_intro = False
                        else:
                            paused = not paused
                    if paused and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return "quit"
                    if show_intro and event.key == pygame.K_RETURN:
                        show_intro = False
            keys = pygame.key.get_pressed()
            if show_intro:
                intro_timer -= dt
                if intro_timer <= 0:
                    show_intro = False
            elif not paused:
                if invincible_timer > 0:
                    invincible_timer -= dt
                player.update(dt, keys, tilemap)
                for e in enemies[:]:
                    if e.update(dt, player, tilemap):
                        if invincible_timer <= 0:
                            self.audio.play("enemy_hit")
                            self.shake_timer = 0.3
                            self.shake_intensity = 10
                            self.lives -= 1
                            invincible_timer = 2.0
                            player.x, player.y = spawn_pos
                            if self.lives <= 0:
                                level_result = "game_over"
                for e in enemies[:]:
                    if e.hp <= 0:
                        enemies.remove(e)
                cx, cy = int(player.x // TILE), int(player.y // TILE)
                for y in range(max(0, cy - 2), min(tilemap.rows, cy + 3)):
                    for x in range(max(0, cx - 2), min(tilemap.cols, cx + 3)):
                        if tilemap.data[y][x] == 2:
                            if abs(player.x - (x * TILE + TILE // 2)) < TILE * 0.6 and \
                               abs(player.y - (y * TILE + TILE // 2)) < TILE * 0.6:
                                tilemap.data[y][x] = 0
                                gems_collected += 1
                                self.audio.play("collect")
                if gems_collected >= gems_total:
                    doors_open = True
                    elapsed = (pygame.time.get_ticks() - start_time) / 1000
                    if elapsed < 30:
                        self._unlock("speedrunner")
                    if exit_pos:
                        ex, ey = exit_pos
                        if abs(player.x - (ex * TILE + TILE // 2)) < TILE * 0.6 and \
                           abs(player.y - (ey * TILE + TILE // 2)) < TILE * 0.6:
                            self.audio.play("complete")
                            pygame.time.wait(500)
                            level_result = "complete"
            self._draw_game(tilemap, player, enemies, exit_pos, doors_open,
                            gems_collected, gems_total, start_time, paused, invincible_timer,
                            level_idx, show_intro)
            pygame.display.flip()
        self.last_gems = gems_collected
        return level_result

    def _draw_game(self, tilemap, player, enemies, exit_pos, doors_open,
                   gems_collected, gems_total, start_time, paused,
                   invincible_timer, level_idx, show_intro):
        self.screen.fill((5, 5, 10))
        shake_off = [0, 0]
        if self.shake_timer > 0:
            intensity = self.shake_intensity * (self.shake_timer / 0.3)
            shake_off[0] = random.randint(-int(intensity), int(intensity))
            shake_off[1] = random.randint(-int(intensity), int(intensity))
            self.shake_timer -= 1 / 60
        cx, cy = player.x - W // 2 + shake_off[0], player.y - H // 2 + shake_off[1]
        for y in range(tilemap.rows):
            for x in range(tilemap.cols):
                v = tilemap.data[y][x]
                if v == 1: continue
                sx, sy = x * TILE - cx, y * TILE - cy
                if sx < -TILE or sx > W or sy < -TILE or sy > H: continue
                if v == 2 or v == 0 or v == 3:
                    pygame.draw.rect(self.screen, (35, 35, 45), (sx, sy, TILE, TILE))
        for e in enemies:
            sx, sy = e.x - cx, e.y - cy
            shadow_surf = pygame.Surface((e.w, int(e.w * 0.4)), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (0, 0, e.w, int(e.w * 0.4)))
            self.screen.blit(shadow_surf, (int(sx - e.w // 2 + 3), int(sy + e.w // 4 + 3)))
        if invincible_timer <= 0 or int(invincible_timer * 10) % 2 == 0:
            px, py = player.x - cx, player.y - cy
            shadow_surf = pygame.Surface((player.w, int(player.w * 0.4)), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (0, 0, player.w, int(player.w * 0.4)))
            self.screen.blit(shadow_surf, (int(px - player.w // 2 + 3), int(py + player.w // 4 + 3)))
        for y in range(tilemap.rows):
            for x in range(tilemap.cols):
                v = tilemap.data[y][x]
                if v == 0 or v == 2 or v == 3: continue
                sx, sy = x * TILE - cx, y * TILE - cy
                if sx < -TILE or sx > W or sy < -TILE or sy > H: continue
                if v == 1:
                    pygame.draw.rect(self.screen, (100, 100, 110), (sx, sy, TILE, TILE))
                    pygame.draw.rect(self.screen, (80, 80, 90), (sx, sy, TILE, TILE), 2)
        for y in range(tilemap.rows):
            for x in range(tilemap.cols):
                v = tilemap.data[y][x]
                if v != 2 and v != 3: continue
                sx, sy = x * TILE - cx, y * TILE - cy
                if sx < -TILE or sx > W or sy < -TILE or sy > H: continue
                if v == 2:
                    pygame.draw.circle(self.screen, (255, 255, 0), (sx + TILE // 2, sy + TILE // 2), 12)
                elif v == 3:
                    pulse = abs(math.sin(pygame.time.get_ticks() / 400)) * 0.3 + 0.7
                    if doors_open:
                        color = (int(50 * pulse), int(250 * pulse), int(50 * pulse))
                    else:
                        color = (int(10 * pulse), int(80 * pulse), int(10 * pulse))
                    pygame.draw.circle(self.screen, color, (sx + TILE // 2, sy + TILE // 2), TILE // 3)
                    if doors_open:
                        pygame.draw.circle(self.screen, (255, 255, 255), (sx + TILE // 2, sy + TILE // 2), TILE // 3, 1)
        for e in enemies:
            sx, sy = e.x - cx, e.y - cy
            if sx < -TILE or sx > W + TILE or sy < -TILE or sy > H + TILE: continue
            pygame.draw.circle(self.screen, (220, 50, 50), (int(sx), int(sy)), int(e.w // 2))
            pygame.draw.circle(self.screen, (180, 20, 20), (int(sx), int(sy)), int(e.w // 2), 2)
        if invincible_timer <= 0 or int(invincible_timer * 10) % 2 == 0:
            px, py = player.x - cx, player.y - cy
            pygame.draw.circle(self.screen, (80, 160, 255), (int(px), int(py)), int(player.w // 2))

        yy = 20
        c = (100, 255, 100) if doors_open else (255, 255, 255)
        self.screen.blit(self.font_md.render(f"Сферы: {gems_collected} / {gems_total}", True, c), (20, yy))
        yy += 36
        self.screen.blit(self.font_md.render("Жизни: ", True, (255, 255, 255)), (20, yy))
        for i in range(self.lives):
            pygame.draw.circle(self.screen, (220, 50, 50), (110 + i * 22, yy + 14), 8)
        yy += 36
        self.screen.blit(self.font_sm.render(f"Уровень: {level_idx + 1} / {self.total_levels}", True, (180, 180, 200)), (20, yy))
        yy += 30
        elapsed = (pygame.time.get_ticks() - start_time) / 1000
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        self.screen.blit(self.font_sm.render(f"Время: {minutes:02d}:{seconds:02d}", True, (180, 180, 200)), (20, yy))

        if not doors_open:
            hint = "Собери все сферы чтобы открыть выход"
            hw = self.font_sm.size(hint)[0]
            self.screen.blit(self.font_sm.render(hint, True, (180, 150, 60)),
                             ((W - hw) // 2, H - 44))
        else:
            hint = "Выход открыт! Найди зеленый маяк"
            hw = self.font_sm.size(hint)[0]
            pulse = abs(math.sin(pygame.time.get_ticks() / 300)) * 0.3 + 0.7
            c2 = (int(0 * pulse), int(200 * pulse), int(50 * pulse))
            self.screen.blit(self.font_sm.render(hint, True, c2),
                             ((W - hw) // 2, H - 44))

        self.ach_notifications[:] = [n for n in self.ach_notifications if n["phase"] < 3.6]
        for n in self.ach_notifications:
            n["phase"] += 1 / 60
            lbl = self.ach_names.get(n["key"], n["key"])
            pw, ph = 300, 70
            px = W - pw - 10
            if n["phase"] < 0.3:
                t = n["phase"] / 0.3
                py = int(-ph + t * (ph + 10))
            elif n["phase"] < 3.3:
                py = 10
            else:
                t = (n["phase"] - 3.3) / 0.3
                py = int(10 + t * (-ph - 10))
            s = pygame.Surface((pw, ph), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            self.screen.blit(s, (px, py))
            pygame.draw.rect(self.screen, (100, 240, 100), (px, py, pw, ph), 2, border_radius=4)
            t1 = self.font_sm.render("Достижение получено!", True, (255, 255, 100))
            self.screen.blit(t1, (px + 10, py + 6))
            t2 = self.font_sm.render(lbl, True, (200, 200, 200))
            self.screen.blit(t2, (px + 10, py + 32))

        if show_intro:
            s = pygame.Surface((W, H), pygame.SRCALPHA)
            s.fill((0, 0, 0, 120))
            self.screen.blit(s, (0, 0))
            t = self.font_lg.render(f"Уровень {level_idx + 1} / {self.total_levels}", True, (255, 255, 255))
            self.screen.blit(t, t.get_rect(center=(W // 2, H // 2 - 20)))
            t2 = self.font_sm.render("Приготовься...", True, (200, 200, 220))
            self.screen.blit(t2, t2.get_rect(center=(W // 2, H // 2 + 30)))
        if paused:
            s = pygame.Surface((W, H), pygame.SRCALPHA)
            s.fill((0, 0, 0, 128))
            self.screen.blit(s, (0, 0))
            t = self.font_lg.render("ПАУЗА", True, (255, 255, 255))
            self.screen.blit(t, t.get_rect(center=(W // 2, H // 2)))
            t2 = self.font_sm.render("ESC — продолжить, ENTER — выход", True, (180, 180, 180))
            self.screen.blit(t2, t2.get_rect(center=(W // 2, H // 2 + 50)))

    def _pause_menu(self):
        return False

    def _show_game_over(self, total_time):
        self.screen.fill((0, 0, 0))
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))
        t = self.font_lg.render("ИГРА ОКОНЧЕНА", True, (200, 50, 50))
        self.screen.blit(t, t.get_rect(center=(W // 2, H // 2 - 30)))
        t2 = self.font_sm.render("Нажми ENTER для возврата в меню", True, (200, 200, 220))
        self.screen.blit(t2, t2.get_rect(center=(W // 2, H // 2 + 30)))
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN: return

    def _show_win(self, total_time):
        self.screen.fill((0, 0, 0))
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))
        t = self.font_lg.render("ТЫ ПОБЕДИЛ!", True, (50, 200, 50))
        self.screen.blit(t, t.get_rect(center=(W // 2, H // 2 - 40)))
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        t2 = self.font_md.render(f"Общее время: {minutes:02d}:{seconds:02d}", True, (255, 255, 255))
        self.screen.blit(t2, t2.get_rect(center=(W // 2, H // 2 + 10)))
        t3 = self.font_sm.render("Нажми ENTER для возврата в меню", True, (200, 200, 220))
        self.screen.blit(t3, t3.get_rect(center=(W // 2, H // 2 + 50)))
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN: return

    def _text_input(self, prompt):
        text = ""
        active = True
        while active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and text.strip():
                        return text.strip()
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif event.unicode.isprintable() and len(text) < 40:
                        text += event.unicode
            self.screen.fill((5, 5, 10))
            s = pygame.Surface((W, H), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            self.screen.blit(s, (0, 0))
            t = self.font_md.render(prompt, True, (200, 200, 255))
            self.screen.blit(t, t.get_rect(center=(W // 2, H // 2 - 40)))
            txt_surf = self.font_lg.render(text + "|" if pygame.time.get_ticks() % 1000 < 500 else text, True, (255, 255, 255))
            self.screen.blit(txt_surf, txt_surf.get_rect(center=(W // 2, H // 2 + 20)))
            hint = self.font_sm.render("Enter — подтвердить, Esc — отмена", True, (150, 150, 150))
            self.screen.blit(hint, hint.get_rect(center=(W // 2, H // 2 + 70)))
            pygame.display.flip()
            self.clock.tick(60)

    def _select_level(self):
        levels = sorted([f.replace(".json", "") for f in os.listdir(LVL_DIR) if f.endswith(".json")])
        if not levels:
            return None
        sel = 0
        scroll = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        if event.key == pygame.K_RETURN and levels:
                            return levels[sel]
                        return None
                    if event.key in (pygame.K_w, pygame.K_UP):
                        sel = (sel - 1) % len(levels)
                    if event.key in (pygame.K_s, pygame.K_DOWN):
                        sel = (sel + 1) % len(levels)
                if event.type == pygame.MOUSEWHEEL:
                    scroll += event.y
                    sel = max(0, min(len(levels) - 1, scroll))
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    for i, name in enumerate(levels):
                        r = pygame.Rect(W // 2 - 120, 200 + i * 50, 240, 40)
                        if r.collidepoint(mx, my):
                            return name
            self.screen.fill((20, 20, 40))
            t = self.font_md.render("Выберите уровень", True, (200, 200, 255))
            self.screen.blit(t, t.get_rect(center=(W // 2, 80)))
            for i, name in enumerate(levels):
                c = (255, 255, 100) if i == sel else (180, 180, 180)
                r = pygame.Rect(W // 2 - 120, 200 + i * 50, 240, 40)
                if i == sel:
                    pygame.draw.rect(self.screen, (60, 60, 100), r, border_radius=6)
                    pygame.draw.rect(self.screen, (100, 100, 200), r, 2, border_radius=6)
                lbl = self.font_sm.render(name, True, c)
                self.screen.blit(lbl, lbl.get_rect(center=r.center))
            hint = self.font_sm.render("Esc — назад", True, (150, 150, 150))
            self.screen.blit(hint, hint.get_rect(center=(W // 2, H - 40)))
            pygame.display.flip()
            self.clock.tick(60)

    def _run_editor(self):
        cols, rows = 16, 16
        tm = TileMap(cols, rows)
        zoom = 1.0
        cam_x, cam_y = 0, 0
        dragging = False
        drag_start = None
        for y in range(rows):
            for x in range(cols):
                tm.data[y][x] = 1 if (x == 0 or x == cols - 1 or y == 0 or y == rows - 1) else 0
        brush = 0
        brushes = [0, 1, 2, 3, 4]
        labels = ["Пол", "Стена", "Самоцвет", "Выход", "Враг"]
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            mx, my = pygame.mouse.get_pos()
            y_off = H - 130
            in_ui = my >= y_off
            if not in_ui:
                tx = int((mx - cam_x) // (TILE * zoom))
                ty = int((my - cam_y) // (TILE * zoom))
            else:
                tx, ty = -1, -1
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: return
                    if event.key == pygame.K_1: brush = 0
                    if event.key == pygame.K_2: brush = 1
                    if event.key == pygame.K_3: brush = 2
                    if event.key == pygame.K_4: brush = 3
                    if event.key == pygame.K_5: brush = 4
                    if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        name = self._text_input("Имя уровня:")
                        if name:
                            self._save_level_file(name, tm.to_list())
                            print(f"Сохранено {name}")
                    if event.key == pygame.K_l and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        files = [f for f in os.listdir(LVL_DIR) if f.endswith(".json")]
                        if files:
                            name = files[-1]
                            data = self._load_level_file(name.replace(".json", ""))
                            if data:
                                tm.from_list(data)
                                cols, rows = tm.cols, tm.rows
                                print(f"Загружено {name}")
                if event.type == pygame.MOUSEWHEEL:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        old_zoom = zoom
                        zoom *= 1.2 if event.y > 0 else 0.8
                        zoom = max(0.3, min(3.0, zoom))
                    else:
                        cam_y -= event.y * 30
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if in_ui:
                            for i, (b, l) in enumerate(zip(brushes, labels)):
                                r = pygame.Rect(10 + i * 110, y_off + 50, 100, 28)
                                if r.collidepoint(mx, my):
                                    brush = b
                        elif 0 <= tx < tm.cols and 0 <= ty < tm.rows:
                            tm.data[ty][tx] = brush
                    elif event.button == 2:
                        dragging = True
                        drag_start = (mx - cam_x, my - cam_y)
                    elif event.button == 3:
                        if 0 <= tx < tm.cols and 0 <= ty < tm.rows:
                            tm.data[ty][tx] = 0
                if event.type == pygame.MOUSEBUTTONUP and event.button == 2:
                    dragging = False
                if event.type == pygame.MOUSEMOTION and dragging:
                    cam_x = mx - drag_start[0]
                    cam_y = my - drag_start[1]
            if pygame.mouse.get_pressed()[0] and not in_ui:
                if 0 <= tx < tm.cols and 0 <= ty < tm.rows:
                    tm.data[ty][tx] = brush
            self.screen.fill((5, 5, 10))
            for y in range(tm.rows):
                for x in range(tm.cols):
                    v = tm.data[y][x]
                    sx = x * TILE * zoom + cam_x
                    sy = y * TILE * zoom + cam_y
                    sz = int(TILE * zoom)
                    if sx + sz < -10 or sx > W + 10 or sy + sz < -10 or sy > H + 10:
                        continue
                    if v == 1:
                        pygame.draw.rect(self.screen, (100, 100, 110), (sx, sy, sz, sz))
                        if sz > 8:
                            pygame.draw.rect(self.screen, (80, 80, 90), (sx, sy, sz, sz), 2)
                    elif v == 2:
                        pygame.draw.rect(self.screen, (10, 10, 20), (sx, sy, sz, sz))
                        pygame.draw.circle(self.screen, (255, 255, 0), (int(sx + sz // 2), int(sy + sz // 2)), max(4, int(12 * zoom)))
                    elif v == 3:
                        pygame.draw.rect(self.screen, (10, 10, 20), (sx, sy, sz, sz))
                        pygame.draw.rect(self.screen, (50, 200, 50), (int(sx + 8 * zoom), int(sy + 8 * zoom), int(sz - 16 * zoom), int(sz - 16 * zoom)))
                    elif v == 4:
                        pygame.draw.rect(self.screen, (10, 10, 20), (sx, sy, sz, sz))
                        pygame.draw.circle(self.screen, (200, 40, 40), (int(sx + sz // 2), int(sy + sz // 2)), max(4, int(12 * zoom)))
                    else:
                        pygame.draw.rect(self.screen, (10, 10, 20), (sx, sy, sz, sz))
            if not in_ui and 0 <= tx < tm.cols and 0 <= ty < tm.rows:
                pygame.draw.rect(self.screen, (255, 255, 255),
                                 (tx * TILE * zoom + cam_x, ty * TILE * zoom + cam_y, int(TILE * zoom), int(TILE * zoom)), 2)
            self.screen.blit(self.font_sm.render("Ctrl+колёсико — зум | Колёсико — скролл | Средняя кнопка — перемещение", True, (200, 200, 200)), (10, y_off))
            self.screen.blit(self.font_sm.render("ЛКМ — установить | ПКМ — стереть | Ctrl+S — сохранить | Ctrl+L — загрузить | ESC — выход", True, (150, 150, 150)), (10, y_off + 20))
            for i, (b, l) in enumerate(zip(brushes, labels)):
                c = (255, 255, 100) if brush == b else (180, 180, 180)
                r = pygame.Rect(10 + i * 110, y_off + 50, 100, 28)
                bg = (60, 60, 80) if brush == b else (25, 25, 45)
                if r.collidepoint(mx, my):
                    bg = (80, 80, 100) if brush == b else (45, 45, 65)
                pygame.draw.rect(self.screen, bg, r, border_radius=4)
                self.screen.blit(self.font_sm.render(l, True, c), (r.x + 8, r.y + 4))
            pygame.display.flip()
