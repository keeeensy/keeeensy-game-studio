#include "Game.h"
#include <cmath>
#include <cstdio>
#include <queue>
#include <utility>
#include "raymath.h"

static const Color BG_COLOR = {15, 15, 25, 255};

static Color OrbColor(float t) {
    return {
        (unsigned char)(255),
        (unsigned char)((sinf(t * 2.0f) * 0.15f + 0.85f) * 215),
        (unsigned char)((sinf(t * 2.5f) * 0.2f + 0.6f) * 80),
        255
    };
}

Game::Game(int screenWidth, int screenHeight)
    : m_screenWidth(screenWidth), m_screenHeight(screenHeight) {
    m_player.SetSensitivity(m_sensitivity);

    m_menuCamera.position = { 0, 6, -12 };
    m_menuCamera.target = { 0, 0, 0 };
    m_menuCamera.up = { 0, 1, 0 };
    m_menuCamera.fovy = 50;
    m_menuCamera.projection = CAMERA_PERSPECTIVE;

    for (int i = 0; i < 250; ++i) {
        MenuParticle p;
        p.position = {
            (float)GetRandomValue(-150, 150) * 0.1f,
            (float)GetRandomValue(-50, 80) * 0.1f,
            (float)GetRandomValue(-150, 150) * 0.1f,
        };
        p.velocity = {
            (float)GetRandomValue(-20, 20) * 0.01f,
            (float)GetRandomValue(-10, 10) * 0.01f,
            (float)GetRandomValue(-20, 20) * 0.01f,
        };
        p.size = (float)GetRandomValue(5, 20) * 0.01f;
        int b = GetRandomValue(180, 255);
        p.color = { (unsigned char)b, (unsigned char)b, (unsigned char)b, 255 };
        p.phase = (float)GetRandomValue(0, 100) * 0.1f;
        m_menuParticles.push_back(p);
    }
}

static Color AlphaColor(Color c, float a) {
    return {c.r, c.g, c.b, (unsigned char)(a * 255.0f)};
}

void Game::InitFont() {
    if (m_fontLoaded) return;
    int cp[] = {
        ' ', '!', '"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        ':', ';', '<', '=', '>', '?', '@',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        '[', '\\', ']', '^', '_', '`',
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        '{', '|', '}', '~',
        0x0410, 0x0411, 0x0412, 0x0413, 0x0414, 0x0415, 0x0416, 0x0417,
        0x0418, 0x0419, 0x041A, 0x041B, 0x041C, 0x041D, 0x041E, 0x041F,
        0x0420, 0x0421, 0x0422, 0x0423, 0x0424, 0x0425, 0x0426, 0x0427,
        0x0428, 0x0429, 0x042A, 0x042B, 0x042C, 0x042D, 0x042E, 0x042F,
        0x0430, 0x0431, 0x0432, 0x0433, 0x0434, 0x0435, 0x0436, 0x0437,
        0x0438, 0x0439, 0x043A, 0x043B, 0x043C, 0x043D, 0x043E, 0x043F,
        0x0440, 0x0441, 0x0442, 0x0443, 0x0444, 0x0445, 0x0446, 0x0447,
        0x0448, 0x0449, 0x044A, 0x044B, 0x044C, 0x044D, 0x044E, 0x044F,
    };
    int n = sizeof(cp) / sizeof(cp[0]);

    const char* paths[] = {
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
    };
    for (int i = 0; i < 3; ++i) {
        if (FileExists(paths[i])) {
            m_font = LoadFontEx(paths[i], 64, cp, n);
            if (m_font.texture.id > 0) {
                m_fontLoaded = true;
                return;
            }
        }
    }
}

void Game::DestroyFont() {
    if (m_fontLoaded) {
        UnloadFont(m_font);
        m_fontLoaded = false;
    }
}

void Game::DrawTextGame(const char* text, int x, int y, int fontSize, Color color) {
    if (m_fontLoaded) {
        DrawTextEx(m_font, text, {(float)x, (float)y}, (float)fontSize, 1, color);
    } else {
        DrawText(text, x, y, fontSize, color);
    }
}

int Game::MeasureTextGame(const char* text, int fontSize) {
    if (m_fontLoaded) {
        return (int)MeasureTextEx(m_font, text, (float)fontSize, 1).x;
    }
    return MeasureText(text, fontSize);
}

void Game::InitAudio() {
    if (m_audioLoaded) return;
    InitAudioDevice();

    {
        float sr = 22050;
        int n = int(sr * 0.12f);
        short* data = new short[n];
        for (int i = 0; i < n; ++i) {
            float t = i / sr;
            float f = 523 + (880 - 523) * (i / float(n));
            float env = 1.0f - i / float(n);
            data[i] = short(32767 * 0.3f * sinf(2 * PI * f * t) * env);
        }
        Wave w = {};
        w.data = data; w.frameCount = n; w.sampleRate = int(sr); w.sampleSize = 16; w.channels = 1;
        m_orbSound = LoadSoundFromWave(w);
        delete[] data;
    }

    {
        float sr = 22050;
        int n = int(sr * 0.15f);
        short* data = new short[n];
        for (int i = 0; i < n; ++i) {
            float t = i / sr;
            float env = 1.0f - i / float(n);
            data[i] = short(32767 * 0.4f * sinf(2 * PI * 100 * t) * env * env);
        }
        Wave w = {};
        w.data = data; w.frameCount = n; w.sampleRate = int(sr); w.sampleSize = 16; w.channels = 1;
        m_hitSound = LoadSoundFromWave(w);
        delete[] data;
    }

    {
        float sr = 22050;
        int n = int(sr * 0.3f);
        short* data = new short[n];
        for (int i = 0; i < n; ++i) {
            float t = i / sr;
            float env = 1.0f - i / float(n);
            float freq = 523 + (1047 - 523) * (i / float(n));
            data[i] = short(32767 * 0.3f * sinf(2 * PI * freq * t) * env);
        }
        Wave w = {};
        w.data = data; w.frameCount = n; w.sampleRate = int(sr); w.sampleSize = 16; w.channels = 1;
        m_levelSound = LoadSoundFromWave(w);
        delete[] data;
    }

    SetSoundVolume(m_orbSound, m_volume);
    SetSoundVolume(m_hitSound, m_volume);
    SetSoundVolume(m_levelSound, m_volume);

    m_audioLoaded = true;
}

void Game::DestroyAudio() {
    if (!m_audioLoaded) return;
    UnloadSound(m_orbSound);
    UnloadSound(m_hitSound);
    UnloadSound(m_levelSound);
    CloseAudioDevice();
    m_audioLoaded = false;
}

Game::~Game() {
}

void Game::ComputeReachableCells() {
    m_reachableCells.assign(m_maze.GetRows(), std::vector<bool>(m_maze.GetCols(), false));
    int sc = int(m_maze.GetSpawnPos().x / m_maze.GetCellSize());
    int sr = int(m_maze.GetSpawnPos().z / m_maze.GetCellSize());
    if (m_maze.IsSolid(sc, sr)) return;
    std::queue<std::pair<int,int>> q;
    q.push({sc, sr});
    m_reachableCells[sr][sc] = true;
    int dirs[] = {-1,0, 1,0, 0,-1, 0,1};
    while (!q.empty()) {
        auto [c, r] = q.front(); q.pop();
        for (int d = 0; d < 4; ++d) {
            int nc = c + dirs[d*2];
            int nr = r + dirs[d*2+1];
            if (nc >= 0 && nc < m_maze.GetCols() && nr >= 0 && nr < m_maze.GetRows() &&
                !m_reachableCells[nr][nc] && !m_maze.IsSolid(nc, nr)) {
                m_reachableCells[nr][nc] = true;
                q.push({nc, nr});
            }
        }
    }
}

void Game::LoadLevel(int index) {
    m_currentLevel = index;
    m_maze.Generate(index);
    ComputeReachableCells();

    int sc = int(m_maze.GetSpawnPos().x / m_maze.GetCellSize());
    int sr = int(m_maze.GetSpawnPos().z / m_maze.GetCellSize());
    int ec = int(m_maze.GetExitPos().x / m_maze.GetCellSize());
    int er = int(m_maze.GetExitPos().z / m_maze.GetCellSize());

    if (!m_reachableCells[er][ec]) {
        bool fixed = false;
        for (int d = 1; d < 30 && !fixed; ++d) {
            for (int dr = -d; dr <= d && !fixed; ++dr) {
                for (int dc = -d; dc <= d && !fixed; ++dc) {
                    int nr = er + dr, nc = ec + dc;
                    if (nr < 0 || nr >= m_maze.GetRows() || nc < 0 || nc >= m_maze.GetCols()) continue;
                    if (m_maze.IsSolid(nc, nr)) continue;
                    if (m_reachableCells[nr][nc]) {
                        m_maze.SetExitCell(nc, nr);
                        ec = nc; er = nr;
                        fixed = true;
                    }
                }
            }
        }
    }

    m_player.Reset(m_maze.GetSpawnPos());
    SpawnOrbs();
    SpawnEnemiesForLevel();
    m_orbsCollected = 0;
    m_exitUnlocked = false;
    m_levelTimer = 0.0f;
    m_invincibleTimer = 0.0f;
}

void Game::SpawnOrbs() {
    m_orbs.clear();
    int count = 4 + m_currentLevel * 2;
    if (count > 12) count = 12;

    int spawnCol = int(m_maze.GetSpawnPos().x / m_maze.GetCellSize());
    int spawnRow = int(m_maze.GetSpawnPos().z / m_maze.GetCellSize());
    int exitCol = int(m_maze.GetExitPos().x / m_maze.GetCellSize());
    int exitRow = int(m_maze.GetExitPos().z / m_maze.GetCellSize());

    std::vector<std::pair<int,int>> candidates;
    for (int r = 1; r < m_maze.GetRows() - 1; ++r) {
        for (int c = 1; c < m_maze.GetCols() - 1; ++c) {
            if (m_maze.IsSolid(c, r)) continue;
            if (!m_reachableCells[r][c]) continue;
            float dx = (c - spawnCol) * m_maze.GetCellSize();
            float dz = (r - spawnRow) * m_maze.GetCellSize();
            if (sqrtf(dx * dx + dz * dz) < m_maze.GetCellSize() * 2.0f) continue;
            dx = (c - exitCol) * m_maze.GetCellSize();
            dz = (r - exitRow) * m_maze.GetCellSize();
            if (sqrtf(dx * dx + dz * dz) < m_maze.GetCellSize() * 2.0f) continue;
            candidates.push_back({c, r});
        }
    }

    int placed = 0;
    int attempts = 0;
    while (placed < count && attempts < 200 && !candidates.empty()) {
        ++attempts;
        int idx = GetRandomValue(0, (int)candidates.size() - 1);
        auto [c, r] = candidates[idx];

        Vector3 pos = {
            (c + 0.5f) * m_maze.GetCellSize(),
            1.0f,
            (r + 0.5f) * m_maze.GetCellSize()
        };

        bool tooClose = false;
        for (const auto& orb : m_orbs) {
            if (Vector3Distance(pos, orb.position) < m_maze.GetCellSize() * 1.5f) {
                tooClose = true;
                break;
            }
        }
        if (tooClose) {
            candidates.erase(candidates.begin() + idx);
            continue;
        }

        m_orbs.push_back({pos, false, (float)GetRandomValue(0, 100)});
        ++placed;
        candidates.erase(candidates.begin() + idx);
    }
    m_totalOrbs = (int)m_orbs.size();
}

void Game::SpawnEnemiesForLevel() {
    ::SpawnEnemies(m_enemies, m_maze, m_currentLevel, m_reachableCells);
}

void Game::HitByEnemy() {
    if (m_invincibleTimer > 0.0f) return;
    --m_lives;
    m_invincibleTimer = 2.0f;
    if (m_audioLoaded) {
        SetSoundVolume(m_hitSound, m_volume);
        PlaySound(m_hitSound);
    }
    if (m_lives <= 0) {
        EnableCursor();
        m_state = State::GAME_OVER;
    } else {
        m_player.Reset(m_maze.GetSpawnPos());
    }
}

void Game::Restart() {
    m_state = State::MENU_MAIN;
    EnableCursor();
    m_menuSelection = 0;
    m_currentLevel = 0;
    m_lives = 3;
    m_timer = 0.0f;
    m_orbs.clear();
    m_enemies.clear();
}

void Game::Run() {
    InitFont();
    InitAudio();
    SetTargetFPS(60);
    LoadLevel(0);
    m_splashTimer = GetTime() + 2.0f;
    EnableCursor();

    while (!WindowShouldClose() && !m_shouldExit) {
        float dt = GetFrameTime();
        if (dt > 0.05f) dt = 0.05f;
        m_timer += dt;
        Update(dt);
        Draw();
    }

    DestroyFont();
    DestroyAudio();
    CloseWindow();
}

void Game::Update(float dt) {
    if (m_splashTimer > GetTime()) {
        if (IsKeyPressed(KEY_ENTER) || IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
            m_splashTimer = GetTime();
        }
    }

    if (IsKeyPressed(KEY_ESCAPE)) {
        if (m_state == State::PLAYING || m_state == State::LEVEL_INTRO ||
            m_state == State::LEVEL_COMPLETE) {
            Restart();
        } else if (m_state == State::SETTINGS) {
            m_state = State::MENU_MAIN;
        }
    }

    switch (m_state) {
        case State::MENU_MAIN: {
            float angleY = sinf(m_timer * 0.15f) * 0.5f;
            float angleX = sinf(m_timer * 0.1f) * 0.15f;
            float dist = 12.0f;
            m_menuCamera.position.x = sinf(angleY) * cosf(angleX) * dist;
            m_menuCamera.position.y = sinf(angleX) * dist + 1.0f;
            m_menuCamera.position.z = cosf(angleY) * cosf(angleX) * dist;
            m_menuCamera.target = { 0, 0, 0 };

            Ray mouseRay = GetScreenToWorldRay(GetMousePosition(), m_menuCamera);
            Vector3 rayDir = Vector3Normalize(mouseRay.direction);
            Vector3 repPoint = Vector3Add(mouseRay.position, Vector3Scale(rayDir, 10.0f));

            for (auto& p : m_menuParticles) {
                p.position.x += p.velocity.x * dt;
                p.position.y += p.velocity.y * dt;
                p.position.z += p.velocity.z * dt;
                Vector3 toRep = Vector3Subtract(p.position, repPoint);
                float repDist = Vector3Length(toRep);
                if (repDist < 5.0f && repDist > 0.01f) {
                    Vector3 repForce = Vector3Scale(Vector3Normalize(toRep), dt * 1.5f / (repDist + 0.1f));
                    p.position = Vector3Add(p.position, repForce);
                }
                if (p.position.x > 15) { p.position.x = -15; p.velocity.x = (float)GetRandomValue(-20, 20) * 0.01f; }
                if (p.position.x < -15) { p.position.x = 15; p.velocity.x = (float)GetRandomValue(-20, 20) * 0.01f; }
                if (p.position.y > 8) { p.position.y = -5; p.velocity.y = (float)GetRandomValue(-10, 10) * 0.01f; }
                if (p.position.y < -5) { p.position.y = 8; p.velocity.y = (float)GetRandomValue(-10, 10) * 0.01f; }
                if (p.position.z > 15) { p.position.z = -15; p.velocity.z = (float)GetRandomValue(-20, 20) * 0.01f; }
                if (p.position.z < -15) { p.position.z = 15; p.velocity.z = (float)GetRandomValue(-20, 20) * 0.01f; }
            }

            if (IsKeyPressed(KEY_UP) || IsKeyPressed(KEY_W)) m_menuSelection = (m_menuSelection - 1 + 3) % 3;
            if (IsKeyPressed(KEY_DOWN) || IsKeyPressed(KEY_S)) m_menuSelection = (m_menuSelection + 1) % 3;

            Vector2 mp = GetMousePosition();
            int startY = m_screenHeight / 2;
            int itemFs = 36;
            const char* itemLabels[] = { "Начать игру", "Настройки", "Выход" };
            for (int i = 0; i < 3; ++i) {
                int iw = MeasureTextGame(itemLabels[i], itemFs);
                Rectangle r = { (m_screenWidth - iw) / 2.0f - 20, (float)(startY + i * 56 - 6), (float)iw + 40, (float)itemFs + 12 };
                if (CheckCollisionPointRec(mp, r)) {
                    m_menuSelection = i;
                }
            }
            if (IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
                if (m_menuSelection == 0) {
                    LoadLevel(0);
                    m_state = State::LEVEL_INTRO;
                    m_introTimer = 1.5f;
                } else if (m_menuSelection == 1) {
                    m_settingsCursor = 0;
                    m_state = State::SETTINGS;
                } else if (m_menuSelection == 2) {
                    m_shouldExit = true;
                }
            }
            if (IsKeyPressed(KEY_ENTER)) {
                if (m_menuSelection == 0) {
                    LoadLevel(0);
                    m_state = State::LEVEL_INTRO;
                    m_introTimer = 1.5f;
                } else if (m_menuSelection == 1) {
                    m_settingsCursor = 0;
                    m_state = State::SETTINGS;
                } else if (m_menuSelection == 2) {
                    m_shouldExit = true;
                }
            }
            break;
        }

        case State::SETTINGS: {
            int prev = m_settingsCursor;
            if (IsKeyPressed(KEY_UP) || IsKeyPressed(KEY_W)) m_settingsCursor = (m_settingsCursor - 1 + 2) % 2;
            if (IsKeyPressed(KEY_DOWN) || IsKeyPressed(KEY_S)) m_settingsCursor = (m_settingsCursor + 1) % 2;

            if (m_settingsCursor == 0) {
                if (IsKeyPressed(KEY_RIGHT)) m_volume = fminf(m_volume + 0.1f, 1.0f);
                if (IsKeyPressed(KEY_LEFT)) m_volume = fmaxf(m_volume - 0.1f, 0.0f);
                if (m_audioLoaded) {
                    SetSoundVolume(m_orbSound, m_volume);
                    SetSoundVolume(m_hitSound, m_volume);
                    SetSoundVolume(m_levelSound, m_volume);
                }
            } else {
                if (IsKeyPressed(KEY_RIGHT)) m_sensitivity = fminf(m_sensitivity + 0.0005f, 0.01f);
                if (IsKeyPressed(KEY_LEFT)) m_sensitivity = fmaxf(m_sensitivity - 0.0005f, 0.0005f);
                m_player.SetSensitivity(m_sensitivity);
            }
            break;
        }

        case State::LEVEL_INTRO:
            m_introTimer -= dt;
            if (m_introTimer <= 0.0f || IsKeyPressed(KEY_ENTER)) {
                DisableCursor();
                SetMousePosition(m_screenWidth / 2, m_screenHeight / 2);
                m_state = State::PLAYING;
            }
            break;

        case State::PLAYING:
            UpdatePlaying(dt);
            break;

        case State::LEVEL_COMPLETE:
            m_completeTimer -= dt;
            if (m_completeTimer <= 0.0f || IsKeyPressed(KEY_ENTER)) {
                if (m_currentLevel + 1 < m_totalLevels) {
                    LoadLevel(m_currentLevel + 1);
                    m_state = State::LEVEL_INTRO;
                    m_introTimer = 1.5f;
                } else {
                    m_state = State::WIN;
                }
            }
            break;

        case State::WIN:
            if (IsKeyPressed(KEY_ENTER)) Restart();
            break;

        case State::GAME_OVER:
            if (IsKeyPressed(KEY_ENTER)) Restart();
            break;
    }
}

void Game::UpdatePlaying(float dt) {
    m_levelTimer += dt;

    if (m_invincibleTimer > 0.0f) {
        m_invincibleTimer -= dt;
    }

    m_player.Update(dt, m_maze, m_screenWidth, m_screenHeight);

    for (auto& orb : m_orbs) {
        orb.animTime += dt;
        if (orb.collected) continue;
        Vector3 orbPos = orb.position;
        orbPos.y += sinf(orb.animTime * 2.0f) * 0.3f;
        float dist = Vector3Distance(m_player.GetPosition(), orbPos);
        if (dist < 1.2f) {
            orb.collected = true;
            ++m_orbsCollected;
            if (m_audioLoaded) {
                SetSoundVolume(m_orbSound, m_volume);
                PlaySound(m_orbSound);
            }
        }
    }

    m_exitUnlocked = (m_orbsCollected >= m_totalOrbs);

    Vector3 exitPos = m_maze.GetExitPos();
    exitPos.y = m_player.GetPosition().y;
    if (m_exitUnlocked && Vector3Distance(m_player.GetPosition(), exitPos) < 1.5f) {
        EnableCursor();
        m_state = State::LEVEL_COMPLETE;
        m_completeTimer = 2.0f;
        if (m_audioLoaded) {
            SetSoundVolume(m_levelSound, m_volume);
            PlaySound(m_levelSound);
        }
        return;
    }

    Vector3 ppos = m_player.GetPosition();
    for (auto& e : m_enemies) {
        UpdateEnemy(e, dt, ppos, m_maze);
        if (!e.active) continue;
        float dx = ppos.x - e.position.x;
        float dz = ppos.z - e.position.z;
        float dist = sqrtf(dx * dx + dz * dz);
        if (dist < e.radius + 0.25f) {
            HitByEnemy();
            break;
        }
    }
}

void Game::Draw() {
    BeginDrawing();
    ClearBackground(BG_COLOR);

    switch (m_state) {
        case State::MENU_MAIN:
            DrawMenuMain();
            break;
        case State::SETTINGS:
            DrawSettings();
            break;
        case State::LEVEL_INTRO:
            DrawLevelIntro();
            break;
        case State::PLAYING:
            DrawPlaying();
            break;
        case State::LEVEL_COMPLETE:
            DrawPlaying();
            DrawLevelComplete();
            break;
        case State::WIN:
            DrawWin();
            break;
        case State::GAME_OVER:
            DrawPlaying();
            DrawGameOver();
            break;
    }

    if (m_splashTimer > GetTime()) {
        DrawSplash();
    }

    EndDrawing();
}

void Game::DrawMenuMain() {
    BeginMode3D(m_menuCamera);

    for (const auto& p : m_menuParticles) {
        float alpha = 0.5f + 0.4f * sinf(m_timer * 1.5f + p.phase);
        Color pc = p.color;
        pc.a = (unsigned char)(alpha * 255);
        DrawSphere(p.position, p.size, pc);
    }

    EndMode3D();

    DrawRectangle(0, 0, m_screenWidth, m_screenHeight, AlphaColor(BLACK, 0.3f));

    const char* title = "Gem Hunter 3D";
    int tw = MeasureTextGame(title, 72);
    DrawTextGame(title, (m_screenWidth - tw) / 2, m_screenHeight / 2 - 140, 72,
             (Color){100, 200, 255, 255});
    const char* subtitle = "Собери все 3D сферы и найди выход!";
    int sw = MeasureTextGame(subtitle, 28);
    DrawTextGame(subtitle, (m_screenWidth - sw) / 2, m_screenHeight / 2 - 60, 28,
             (Color){150, 150, 180, 255});

    const char* items[] = { "Начать игру", "Настройки", "Выход" };
    int startY = m_screenHeight / 2;
    int itemFs = 36;
    for (int i = 0; i < 3; ++i) {
        bool sel = (i == m_menuSelection);
        int iw = MeasureTextGame(items[i], itemFs);
        int ix = (m_screenWidth - iw) / 2;
        int iy = startY + i * 56;
        if (sel) {
            DrawRectangle(ix - 20, iy - 6, iw + 40, itemFs + 12, (Color){30, 40, 60, 255});
            DrawRectangleLines(ix - 20, iy - 6, iw + 40, itemFs + 12, (Color){60, 160, 220, 255});
        }
        Color c = sel ? (Color){100, 200, 255, 255} : (Color){150, 150, 180, 255};
        DrawTextGame(items[i], ix, iy, itemFs, c);
    }
}

void Game::DrawSplash() {
    DrawRectangle(0, 0, m_screenWidth, m_screenHeight, WHITE);
    float remaining = m_splashTimer - GetTime();
    float alpha = fminf(1.0f, remaining * 3.0f);
    Color c = {0, 0, 0, (unsigned char)(alpha * 255)};
    const char* text = "Keeeensy";
    int tw = MeasureTextGame(text, 80);
    DrawTextGame(text, (m_screenWidth - tw) / 2, m_screenHeight / 2 - 40, 80, c);
}

void Game::DrawSettings() {
    DrawRectangle(0, 0, m_screenWidth, m_screenHeight, AlphaColor(BLACK, 0.8f));

    const char* title = "Настройки";
    int tw = MeasureTextGame(title, 56);
    DrawTextGame(title, (m_screenWidth - tw) / 2, 40, 56, (Color){80, 200, 255, 255});

    int fs = 28;
    int startY = 140;
    int spacing = 100;

    for (int i = 0; i < 2; ++i) {
        bool sel = (i == m_settingsCursor);
        Color labelC = sel ? WHITE : (Color){180, 180, 200, 255};

        const char* label = (i == 0) ? "Громкость" : "Чувствительность мыши";
        int lw = MeasureTextGame(label, fs);
        DrawTextGame(label, (m_screenWidth - lw) / 2, startY + i * spacing, fs, labelC);

        float val = (i == 0) ? m_volume : (m_sensitivity / 0.01f);
        int barW = 300;
        int barH = 12;
        int barX = (m_screenWidth - barW) / 2;
        int barY = startY + i * spacing + 35;

        DrawRectangle(barX, barY, barW, barH, (Color){60, 60, 80, 255});

        int fill = (int)(val * barW);
        Color fillC = sel ? (Color){80, 200, 255, 255} : (Color){100, 100, 140, 255};
        DrawRectangle(barX, barY, fill, barH, fillC);

        char valStr[16];
        snprintf(valStr, sizeof(valStr), "%.0f%%", val * 100.0f);
        int vw = MeasureTextGame(valStr, 22);
        DrawTextGame(valStr, barX + barW + 12, barY - 1, 22, labelC);

        if (sel) {
            DrawRectangleLines(barX - 2, barY - 2, barW + 4, barH + 4,
                               AlphaColor((Color){80, 200, 255, 255}, 0.5f + 0.5f * sinf(m_timer * 3)));
        }
    }

    const char* hint = "< > для изменения, ESC для возврата";
    float pulse = sinf(m_timer * 2.0f) * 0.3f + 0.7f;
    int hw = MeasureTextGame(hint, 22);
    DrawTextGame(hint, (m_screenWidth - hw) / 2, startY + 2 * spacing + 30, 22,
             AlphaColor((Color){150, 150, 180, 255}, pulse));
}

void Game::DrawLevelIntro() {
    DrawPlaying();

    DrawRectangle(0, 0, m_screenWidth, m_screenHeight, AlphaColor(BLACK, 0.4f));

    char buf[64];
    snprintf(buf, sizeof(buf), "Уровень %d / %d", m_currentLevel + 1, m_totalLevels);
    int tw = MeasureTextGame(buf, 56);
    DrawTextGame(buf, (m_screenWidth - tw) / 2, m_screenHeight / 2 - 36, 56, WHITE);

    const char* prompt = "Приготовься...";
    int pw = MeasureTextGame(prompt, 28);
    DrawTextGame(prompt, (m_screenWidth - pw) / 2, m_screenHeight / 2 + 36, 28,
             (Color){200, 200, 220, 255});
}

void Game::DrawPlaying() {
    BeginMode3D(*m_player.GetCamera());

    m_maze.Draw3D();

    for (const auto& e : m_enemies) {
        DrawEnemy(e, m_timer);
    }

    for (const auto& orb : m_orbs) {
        if (orb.collected) continue;
        float bob = sinf(orb.animTime * 2.0f) * 0.3f;
        Vector3 pos = { orb.position.x, orb.position.y + bob, orb.position.z };
        Vector3 shadowPos = { orb.position.x, 0.05f, orb.position.z };
        DrawCylinder(shadowPos, 0.3f, 0.3f, 0.02f, 10, AlphaColor(BLACK, 0.3f));
        Color c = OrbColor(orb.animTime);
        DrawSphere(pos, 0.35f, c);
        DrawSphereWires(pos, 0.35f, 8, 8, AlphaColor(c, 0.4f));
    }

    if (m_exitUnlocked) {
        Vector3 ep = m_maze.GetExitPos();
        ep.y = 1.5f;
        float pulse = sinf(GetTime() * 3.0f) * 0.5f + 0.5f;
        DrawCylinder(ep, 0.8f, 0.1f, 4.0f, 8,
                     AlphaColor((Color){0, 255, 100, 255}, pulse * 0.6f));
        DrawCylinderWires(ep, 0.8f, 0.1f, 4.0f, 8,
                          AlphaColor((Color){0, 255, 100, 255}, pulse));
    }

    EndMode3D();

    DrawHUD();
    m_maze.DrawMinimap(m_screenWidth - 180, 15, 160, m_player.GetPosition());
}

void Game::DrawHUD() {
    char buf[128];

    int yy = 20;

    snprintf(buf, sizeof(buf), "Сферы: %d / %d", m_orbsCollected, m_totalOrbs);
    DrawTextGame(buf, 20, yy, 28, m_exitUnlocked ? GREEN : WHITE);
    yy += 36;

    snprintf(buf, sizeof(buf), "Жизни: ");
    DrawTextGame(buf, 20, yy, 28, WHITE);
    int lx = 20 + MeasureTextGame(buf, 28);
    for (int i = 0; i < m_lives; ++i) {
        DrawCircle(lx + i * 22, yy + 14, 8, RED);
    }
    yy += 36;

    snprintf(buf, sizeof(buf), "Уровень: %d / %d", m_currentLevel + 1, m_totalLevels);
    DrawTextGame(buf, 20, yy, 22, (Color){180, 180, 200, 255});
    yy += 30;

    int minutes = (int)(m_levelTimer / 60);
    int seconds = (int)(m_levelTimer) % 60;
    snprintf(buf, sizeof(buf), "Время: %02d:%02d", minutes, seconds);
    DrawTextGame(buf, 20, yy, 22, (Color){180, 180, 200, 255});
    yy += 30;

    if (!m_exitUnlocked) {
        const char* hint = "Собери все сферы чтобы открыть выход";
        int hw = MeasureTextGame(hint, 20);
        DrawTextGame(hint, (m_screenWidth - hw) / 2, m_screenHeight - 44, 20,
                 (Color){180, 150, 60, 255});
    } else {
        const char* hint = "Выход открыт! Найди зеленый маяк";
        int hw = MeasureTextGame(hint, 20);
        float pulse = sinf(GetTime() * 3.0f) * 0.3f + 0.7f;
        DrawTextGame(hint, (m_screenWidth - hw) / 2, m_screenHeight - 44, 20,
                 AlphaColor(GREEN, pulse));
    }
}

void Game::DrawLevelComplete() {
    DrawRectangle(0, 0, m_screenWidth, m_screenHeight, AlphaColor(BLACK, 0.4f));

    char buf[64];
    snprintf(buf, sizeof(buf), "Уровень %d пройден!", m_currentLevel + 1);
    int tw = MeasureTextGame(buf, 56);
    DrawTextGame(buf, (m_screenWidth - tw) / 2, m_screenHeight / 2 - 36, 56, GREEN);

    int minutes = (int)(m_levelTimer / 60);
    int seconds = (int)m_levelTimer % 60;
    snprintf(buf, sizeof(buf), "Время: %02d:%02d", minutes, seconds);
    int sw = MeasureTextGame(buf, 28);
    DrawTextGame(buf, (m_screenWidth - sw) / 2, m_screenHeight / 2 + 24, 28, WHITE);
}

void Game::DrawGameOver() {
    DrawRectangle(0, 0, m_screenWidth, m_screenHeight, AlphaColor(BLACK, 0.6f));

    const char* title = "ИГРА ОКОНЧЕНА";
    int tw = MeasureTextGame(title, 72);
    DrawTextGame(title, (m_screenWidth - tw) / 2, m_screenHeight / 2 - 56, 72, RED);

    const char* prompt = "Нажми ENTER для возврата в меню";
    float pulse = sinf(m_timer * 2.0f) * 0.3f + 0.7f;
    int pw = MeasureTextGame(prompt, 26);
    DrawTextGame(prompt, (m_screenWidth - pw) / 2, m_screenHeight / 2 + 24, 26,
             AlphaColor((Color){200, 200, 220, 255}, pulse));
}

void Game::DrawWin() {
    DrawRectangle(0, 0, m_screenWidth, m_screenHeight, AlphaColor(BLACK, 0.7f));

    const char* win = "ТЫ ПОБЕДИЛ!";
    int tw = MeasureTextGame(win, 72);
    DrawTextGame(win, (m_screenWidth - tw) / 2, m_screenHeight / 2 - 56, 72, GREEN);

    float seconds = m_timer;
    int minutes = (int)(seconds / 60);
    int secs = (int)seconds % 60;
    char buf[64];
    snprintf(buf, sizeof(buf), "Общее время: %02d:%02d", minutes, secs);
    int sw = MeasureTextGame(buf, 32);
    DrawTextGame(buf, (m_screenWidth - sw) / 2, m_screenHeight / 2 + 24, 32, WHITE);

    const char* prompt = "Нажми ENTER для возврата в меню";
    float pulse = sinf(m_timer * 2.0f) * 0.3f + 0.7f;
    int pw = MeasureTextGame(prompt, 26);
    DrawTextGame(prompt, (m_screenWidth - pw) / 2, m_screenHeight / 2 + 80, 26,
             AlphaColor((Color){200, 200, 220, 255}, pulse));
}
