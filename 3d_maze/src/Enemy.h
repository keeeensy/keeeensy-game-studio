#pragma once
#include "raylib.h"
#include <vector>

class Maze;

struct Enemy {
    Vector3 position;
    float speed;
    float radius;
    bool active;
    float animTime;
};

void UpdateEnemy(Enemy& e, float dt, const Vector3& playerPos, const Maze& maze);
void DrawEnemy(const Enemy& e, float time);
void SpawnEnemies(
    std::vector<Enemy>& enemies,
    const Maze& maze,
    int levelIndex,
    const std::vector<std::vector<bool>>& reachableCells
);
