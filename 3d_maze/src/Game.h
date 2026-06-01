#pragma once
#include "raylib.h"
#include "Player.h"
#include "Maze.h"
#include "Enemy.h"
#include <vector>

struct Orb {
    Vector3 position;
    bool collected;
    float animTime;
};

struct MenuParticle {
    Vector3 position;
    Vector3 velocity;
    float size;
    Color color;
    float phase;
};

class Game {
public:
    Game(int screenWidth, int screenHeight);
    ~Game();
    void Run();

private:
    enum class State { MENU_MAIN, SETTINGS, LEVEL_INTRO, PLAYING, LEVEL_COMPLETE, WIN, GAME_OVER };

    void Update(float dt);
    void Draw();

    void UpdatePlaying(float dt);
    void DrawSplash();
    void DrawMenuMain();
    void DrawSettings();
    void DrawLevelIntro();
    void DrawPlaying();
    void DrawLevelComplete();
    void DrawWin();
    void DrawGameOver();
    void DrawHUD();

    void LoadLevel(int index);
    void SpawnOrbs();
    void SpawnEnemiesForLevel();
    void HitByEnemy();
    void Restart();
    void ComputeReachableCells();

    void DrawTextGame(const char* text, int x, int y, int fontSize, Color color);
    int MeasureTextGame(const char* text, int fontSize);
    void InitFont();
    void DestroyFont();
    void InitAudio();
    void DestroyAudio();

    int m_screenWidth;
    int m_screenHeight;
    State m_state = State::MENU_MAIN;
    float m_splashTimer = 0.0f;
    int m_menuSelection = 0;
    int m_settingsCursor = 0;
    float m_volume = 0.7f;
    float m_sensitivity = 0.003f;

    Player m_player;
    Maze m_maze;

    std::vector<Orb> m_orbs;
    std::vector<std::vector<bool>> m_reachableCells;
    std::vector<Enemy> m_enemies;
    int m_lives = 3;
    float m_invincibleTimer = 0.0f;
    int m_currentLevel = 0;
    int m_totalLevels = 10;
    int m_orbsCollected = 0;
    int m_totalOrbs = 0;
    float m_timer = 0.0f;
    float m_levelTimer = 0.0f;
    float m_introTimer = 0.0f;
    float m_completeTimer = 0.0f;
    bool m_exitUnlocked = false;
    bool m_shouldExit = false;

    Font m_font = {};
    bool m_fontLoaded = false;
    Sound m_orbSound = {};
    Sound m_hitSound = {};
    Sound m_levelSound = {};
    bool m_audioLoaded = false;

    std::vector<MenuParticle> m_menuParticles;
    Camera3D m_menuCamera;
};
