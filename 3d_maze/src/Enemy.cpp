#include "Enemy.h"
#include "Maze.h"
#include <cmath>
#include "raymath.h"

void UpdateEnemy(Enemy& e, float dt, const Vector3& playerPos, const Maze& maze) {
    if (!e.active) return;
    e.animTime += dt;

    Vector3 dir = Vector3Subtract(playerPos, e.position);
    float dist = Vector3Length(dir);
    if (dist < 0.1f) return;

    dir = Vector3Scale(dir, 1.0f / dist);
    Vector3 move = Vector3Scale(dir, e.speed * dt);

    Vector3 testX = { e.position.x + move.x, e.position.y, e.position.z };
    if (!maze.CheckCollision(testX, e.radius)) {
        e.position.x = testX.x;
    }

    Vector3 testZ = { e.position.x, e.position.y, e.position.z + move.z };
    if (!maze.CheckCollision(testZ, e.radius)) {
        e.position.z = testZ.z;
    }
}

void DrawEnemy(const Enemy& e, float time) {
    if (!e.active) return;
    float bob = sinf(e.animTime * 3.0f) * 0.08f;
    Vector3 pos = { e.position.x, e.position.y + bob, e.position.z };

    Vector3 shadowPos = { e.position.x, 0.05f, e.position.z };
    DrawCylinder(shadowPos, e.radius * 0.8f, e.radius * 0.8f, 0.02f, 12,
                 ColorAlpha(BLACK, 0.35f));

    Color c = { 220, 30, 30, 255 };
    DrawSphere(pos, e.radius, c);
    DrawSphereWires(pos, e.radius, 12, 12, ColorAlpha(c, 0.15f));

    Color glow = ColorAlpha(c, 0.06f + 0.04f * sinf(time * 2.0f));
    DrawSphere(pos, e.radius * 1.8f, glow);
}

void SpawnEnemies(
    std::vector<Enemy>& enemies,
    const Maze& maze,
    int levelIndex,
    const std::vector<std::vector<bool>>& reachableCells
) {
    enemies.clear();
    int count = 2 + levelIndex * 2;
    if (count > 16) count = 16;

    int spawnCol = maze.GetSpawnCol();
    int spawnRow = maze.GetSpawnRow();
    int exitCol = maze.GetExitCol();
    int exitRow = maze.GetExitRow();
    float cell = maze.GetCellSize();

    std::vector<std::pair<int, int>> candidates;
    for (int r = 1; r < maze.GetRows() - 1; ++r) {
        for (int c = 1; c < maze.GetCols() - 1; ++c) {
            if (maze.IsSolid(c, r)) continue;
            if (r >= static_cast<int>(reachableCells.size()) ||
                c >= static_cast<int>(reachableCells[r].size()) ||
                !reachableCells[r][c]) {
                continue;
            }
            float dx = static_cast<float>(c - spawnCol) * cell;
            float dz = static_cast<float>(r - spawnRow) * cell;
            if (sqrtf(dx * dx + dz * dz) < cell * 3.0f) continue;
            dx = static_cast<float>(c - exitCol) * cell;
            dz = static_cast<float>(r - exitRow) * cell;
            if (sqrtf(dx * dx + dz * dz) < cell * 3.0f) continue;
            candidates.emplace_back(c, r);
        }
    }

    for (int i = 0; i < count && !candidates.empty(); ++i) {
        Enemy e{};
        e.radius = 0.4f;
        e.speed = 2.5f + static_cast<float>(levelIndex) * 0.35f;
        if (e.speed > 5.5f) e.speed = 5.5f;
        e.active = true;
        e.animTime = static_cast<float>(i * 17);
        e.position = { 0, 0, 0 };

        for (int attempt = 0; attempt < 100 && !candidates.empty(); ++attempt) {
            int idx = GetRandomValue(0, static_cast<int>(candidates.size()) - 1);
            auto [c, r] = candidates[idx];

            Vector3 pos = {
                (c + 0.5f) * cell,
                0.5f,
                (r + 0.5f) * cell
            };

            bool tooClose = false;
            for (const auto& exist : enemies) {
                if (Vector3Distance(pos, exist.position) < cell * 2.0f) {
                    tooClose = true;
                    break;
                }
            }
            if (tooClose) {
                candidates.erase(candidates.begin() + idx);
                continue;
            }

            e.position = pos;
            candidates.erase(candidates.begin() + idx);
            break;
        }

        if (e.position.x != 0.0f || e.position.z != 0.0f) {
            enemies.push_back(e);
        }
    }
}
