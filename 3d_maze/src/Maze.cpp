#include "Maze.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <queue>
#include <utility>
#include "raymath.h"

static const Color WALL_COLOR = {70, 70, 90, 255};
static const Color WALL_TOP_COLOR = {90, 90, 110, 255};
static const Color FLOOR_COLOR = {25, 25, 35, 255};
static const Color EXIT_COLOR = {0, 200, 100, 255};

static int CountOpenNeighbors(const std::vector<std::vector<bool>>& grid, int cols, int rows, int c, int r) {
    int count = 0;
    const int dirs[4][2] = {{0, -1}, {1, 0}, {0, 1}, {-1, 0}};
    for (auto& d : dirs) {
        int nc = c + d[0], nr = r + d[1];
        if (nc > 0 && nc < cols - 1 && nr > 0 && nr < rows - 1 && !grid[nr][nc]) {
            ++count;
        }
    }
    return count;
}

Maze::Maze() {}

void Maze::Generate(int levelIndex) {
    const int innerCols = 7 + levelIndex * 2;
    const int innerRows = 5 + levelIndex * 2;
    const unsigned int seed = 10007u + static_cast<unsigned int>(levelIndex) * 7919u;
    const float braidChance = 0.12f + static_cast<float>(levelIndex) * 0.025f;

    GenerateBraidedMaze(innerCols, innerRows, seed, braidChance);
    PlaceExitByBfs();
    BuildWallMesh();
}

void Maze::GenerateBraidedMaze(int innerCols, int innerRows, unsigned int seed, float braidChance) {
    m_cols = innerCols + 2;
    m_rows = innerRows + 2;

    std::vector<std::vector<bool>> grid(m_rows, std::vector<bool>(m_cols, true));

    auto carve = [&](int c, int r) {
        grid[r][c] = false;
    };

    std::vector<std::pair<int, int>> stack;
    carve(1, 1);
    stack.emplace_back(1, 1);

    const int stepDirs[4][2] = {{0, -2}, {2, 0}, {0, 2}, {-2, 0}};

    while (!stack.empty()) {
        auto [cx, cy] = stack.back();
        std::vector<int> order = {0, 1, 2, 3};
        for (int i = 3; i > 0; --i) {
            int j = static_cast<int>((seed + cx * 17 + cy * 31 + i * 13) % (i + 1));
            std::swap(order[i], order[j]);
        }

        bool moved = false;
        for (int idx : order) {
            int nx = cx + stepDirs[idx][0];
            int ny = cy + stepDirs[idx][1];
            if (nx <= 0 || ny <= 0 || nx >= m_cols - 1 || ny >= m_rows - 1) continue;
            if (!grid[ny][nx]) continue;

            carve(nx, ny);
            carve(cx + stepDirs[idx][0] / 2, cy + stepDirs[idx][1] / 2);
            stack.emplace_back(nx, ny);
            moved = true;
            break;
        }
        if (!moved) stack.pop_back();
    }

    for (int r = 1; r < m_rows - 1; ++r) {
        for (int c = 1; c < m_cols - 1; ++c) {
            if (!grid[r][c]) continue;
            bool horizontal = c + 1 < m_cols - 1 && !grid[r][c + 1];
            bool vertical = r + 1 < m_rows - 1 && !grid[r + 1][c];
            if (!horizontal && !vertical) continue;

            float roll = static_cast<float>((seed + c * 97 + r * 53) % 1000) / 1000.0f;
            if (roll > braidChance) continue;

            if (horizontal && vertical) {
                if (((seed + c + r) % 2) == 0) horizontal = false;
                else vertical = false;
            }

            if (horizontal) {
                int left = c - 1, right = c + 1;
                if (left > 0 && right < m_cols - 1 && !grid[r][left] && !grid[r][right]) {
                    grid[r][c] = false;
                }
            } else if (vertical) {
                int up = r - 1, down = r + 1;
                if (up > 0 && down < m_rows - 1 && !grid[up][c] && !grid[down][c]) {
                    grid[r][c] = false;
                }
            }
        }
    }

    for (int r = 1; r < m_rows - 1; ++r) {
        for (int c = 1; c < m_cols - 1; ++c) {
            if (grid[r][c]) continue;
            if (CountOpenNeighbors(grid, m_cols, m_rows, c, r) != 1) continue;

            const int dirs[4][2] = {{0, -1}, {1, 0}, {0, 1}, {-1, 0}};
            for (auto& d : dirs) {
                int wc = c + d[0], wr = r + d[1];
                if (wc <= 0 || wr <= 0 || wc >= m_cols - 1 || wr >= m_rows - 1) continue;
                if (!grid[wr][wc]) continue;

                int beyondC = c + d[0] * 2;
                int beyondR = r + d[1] * 2;
                if (beyondC <= 0 || beyondR <= 0 || beyondC >= m_cols - 1 || beyondR >= m_rows - 1) continue;
                if (grid[beyondR][beyondC]) continue;

                float roll = static_cast<float>((seed + c * 113 + r * 71 + wc + wr) % 1000) / 1000.0f;
                if (roll < braidChance * 1.5f) {
                    grid[wr][wc] = false;
                    break;
                }
            }
        }
    }

    m_cells.assign(m_rows, std::vector<CellInfo>(m_cols));
    for (int r = 0; r < m_rows; ++r) {
        for (int c = 0; c < m_cols; ++c) {
            m_cells[r][c].wall = grid[r][c];
            m_cells[r][c].exit = false;
        }
    }

    m_spawnCol = 1;
    m_spawnRow = 1;
    m_spawnPos = {
        (m_spawnCol + 0.5f) * m_cellSize,
        0.0f,
        (m_spawnRow + 0.5f) * m_cellSize
    };
}

void Maze::PlaceExitByBfs() {
    auto reachable = ComputeReachable();
    int bestDist = -1;
    int bestC = m_spawnCol;
    int bestR = m_spawnRow;

    std::queue<std::tuple<int, int, int>> q;
    q.emplace(m_spawnCol, m_spawnRow, 0);

    std::vector<std::vector<bool>> visited(m_rows, std::vector<bool>(m_cols, false));
    visited[m_spawnRow][m_spawnCol] = true;

    const int dirs[4][2] = {{0, -1}, {1, 0}, {0, 1}, {-1, 0}};

    while (!q.empty()) {
        auto [c, r, dist] = q.front();
        q.pop();

        if (dist > bestDist && !(c == m_spawnCol && r == m_spawnRow)) {
            bestDist = dist;
            bestC = c;
            bestR = r;
        }

        for (auto& d : dirs) {
            int nc = c + d[0], nr = r + d[1];
            if (nc < 0 || nr < 0 || nc >= m_cols || nr >= m_rows) continue;
            if (visited[nr][nc] || !reachable[nr][nc]) continue;
            visited[nr][nc] = true;
            q.emplace(nc, nr, dist + 1);
        }
    }

    for (int r = 0; r < m_rows; ++r) {
        for (int c = 0; c < m_cols; ++c) {
            m_cells[r][c].exit = false;
        }
    }

    m_exitCol = bestC;
    m_exitRow = bestR;
    m_cells[bestR][bestC].exit = true;
    m_exitPos = {
        (bestC + 0.5f) * m_cellSize,
        0.0f,
        (bestR + 0.5f) * m_cellSize
    };
}

void Maze::BuildWallMesh() {
    m_wallQuads.clear();
    std::vector<std::vector<bool>> used(m_rows, std::vector<bool>(m_cols, false));

    for (int r = 0; r < m_rows; ++r) {
        for (int c = 0; c < m_cols; ++c) {
            if (used[r][c] || !m_cells[r][c].wall) continue;

            int w = 1;
            while (c + w < m_cols && m_cells[r][c + w].wall && !used[r][c + w]) {
                ++w;
            }

            int h = 1;
            for (;;) {
                if (r + h >= m_rows) break;
                bool ok = true;
                for (int dc = 0; dc < w; ++dc) {
                    if (!m_cells[r + h][c + dc].wall || used[r + h][c + dc]) {
                        ok = false;
                        break;
                    }
                }
                if (!ok) break;
                ++h;
            }

            for (int dr = 0; dr < h; ++dr) {
                for (int dc = 0; dc < w; ++dc) {
                    used[r + dr][c + dc] = true;
                }
            }

            m_wallQuads.push_back({c, r, w, h});
        }
    }
}

void Maze::SetExitCell(int col, int row) {
    for (int r = 0; r < m_rows; ++r) {
        for (int c = 0; c < m_cols; ++c) {
            m_cells[r][c].exit = false;
        }
    }
    if (row >= 0 && row < m_rows && col >= 0 && col < m_cols && IsWalkable(col, row)) {
        m_cells[row][col].exit = true;
        m_exitCol = col;
        m_exitRow = row;
        m_exitPos = {
            (col + 0.5f) * m_cellSize,
            0.0f,
            (row + 0.5f) * m_cellSize
        };
    }
}

bool Maze::IsWalkable(int col, int row) const {
    if (row < 0 || row >= m_rows || col < 0 || col >= m_cols) return false;
    return !m_cells[row][col].wall;
}

bool Maze::IsSolid(int col, int row) const {
    return !IsWalkable(col, row);
}

std::vector<std::vector<bool>> Maze::ComputeReachable() const {
    std::vector<std::vector<bool>> reachable(m_rows, std::vector<bool>(m_cols, false));
    if (!IsWalkable(m_spawnCol, m_spawnRow)) return reachable;

    std::queue<std::pair<int, int>> q;
    q.emplace(m_spawnCol, m_spawnRow);
    reachable[m_spawnRow][m_spawnCol] = true;

    const int dirs[4][2] = {{0, -1}, {1, 0}, {0, 1}, {-1, 0}};
    while (!q.empty()) {
        auto [c, r] = q.front();
        q.pop();
        for (auto& d : dirs) {
            int nc = c + d[0], nr = r + d[1];
            if (nc < 0 || nr < 0 || nc >= m_cols || nr >= m_rows) continue;
            if (reachable[nr][nc] || !IsWalkable(nc, nr)) continue;
            reachable[nr][nc] = true;
            q.emplace(nc, nr);
        }
    }
    return reachable;
}

bool Maze::ValidateAllLevels() {
    for (int i = 0; i < 10; ++i) {
        Maze maze;
        maze.Generate(i);

        if (!maze.IsWalkable(maze.GetSpawnCol(), maze.GetSpawnRow())) return false;
        if (!maze.IsWalkable(maze.GetExitCol(), maze.GetExitRow())) return false;

        auto reachable = maze.ComputeReachable();
        if (!reachable[maze.GetExitRow()][maze.GetExitCol()]) return false;

        int openCells = 0;
        int junctions = 0;
        const int dirs[4][2] = {{0, -1}, {1, 0}, {0, 1}, {-1, 0}};
        for (int r = 1; r < maze.GetRows() - 1; ++r) {
            for (int c = 1; c < maze.GetCols() - 1; ++c) {
                if (!reachable[r][c]) continue;
                ++openCells;
                int neighbors = 0;
                for (auto& d : dirs) {
                    int nc = c + d[0], nr = r + d[1];
                    if (reachable[nr][nc]) ++neighbors;
                }
                if (neighbors >= 3) ++junctions;
            }
        }
        if (openCells < 4) return false;
        if (junctions < 1 && i > 0) return false;
    }
    return true;
}

bool Maze::CheckCollision(Vector3 pos, float radius) const {
    for (const auto& quad : m_wallQuads) {
        float minX = quad.col * m_cellSize;
        float minZ = quad.row * m_cellSize;
        float maxX = (quad.col + quad.width) * m_cellSize;
        float maxZ = (quad.row + quad.height) * m_cellSize;

        BoundingBox box = {
            { minX, 0.0f, minZ },
            { maxX, m_wallHeight, maxZ }
        };
        BoundingBox entityBox = {
            { pos.x - radius, 0.0f, pos.z - radius },
            { pos.x + radius, m_wallHeight, pos.z + radius }
        };
        if (CheckCollisionBoxes(entityBox, box)) return true;
    }
    return false;
}

void Maze::Draw3D() const {
    DrawPlane(
        { m_cols * m_cellSize * 0.5f, 0.0f, m_rows * m_cellSize * 0.5f },
        { m_cols * m_cellSize, m_rows * m_cellSize },
        FLOOR_COLOR
    );

    for (const auto& quad : m_wallQuads) {
        float cx = (quad.col + quad.width * 0.5f) * m_cellSize;
        float cz = (quad.row + quad.height * 0.5f) * m_cellSize;
        Vector3 center = { cx, m_wallHeight * 0.5f, cz };
        Vector3 size = {
            quad.width * m_cellSize,
            m_wallHeight,
            quad.height * m_cellSize
        };
        DrawCubeV(center, size, WALL_COLOR);

        Vector3 topCenter = { center.x, center.y + size.y * 0.5f, center.z };
        DrawCubeV(topCenter, { size.x, 0.1f, size.z }, WALL_TOP_COLOR);
    }

    Vector3 exitCenter = { m_exitPos.x, m_wallHeight * 0.5f + 1.0f, m_exitPos.z };
    float pulse = sinf(GetTime() * 2.0f) * 0.3f + 0.7f;
    DrawCubeV(exitCenter, { m_cellSize * 0.5f, m_wallHeight + 0.5f, m_cellSize * 0.5f },
              ColorAlpha(EXIT_COLOR, pulse * 0.4f));
    DrawCubeV(exitCenter, { m_cellSize * 0.3f, m_wallHeight, m_cellSize * 0.3f },
              ColorAlpha(EXIT_COLOR, pulse * 0.6f));
    DrawCubeV(exitCenter, { m_cellSize * 0.1f, m_wallHeight + 1.0f, m_cellSize * 0.1f },
              ColorAlpha(EXIT_COLOR, pulse));
}

void Maze::DrawMinimap(int screenX, int screenY, int size, Vector3 playerPos) const {
    float cellPx = static_cast<float>(size) / fmaxf(static_cast<float>(m_cols), static_cast<float>(m_rows));

    for (const auto& quad : m_wallQuads) {
        float px = screenX + quad.col * cellPx;
        float py = screenY + quad.row * cellPx;
        DrawRectangle(
            static_cast<int>(px),
            static_cast<int>(py),
            static_cast<int>(ceilf(quad.width * cellPx)) + 1,
            static_cast<int>(ceilf(quad.height * cellPx)) + 1,
            Color{100, 100, 120, 200}
        );
    }

    int pc = static_cast<int>(screenX + (playerPos.x / m_cellSize) * cellPx);
    int pr = static_cast<int>(screenY + (playerPos.z / m_cellSize) * cellPx);
    DrawCircle(pc, pr, cellPx * 0.6f, GREEN);

    int ec = static_cast<int>(screenX + (m_exitPos.x / m_cellSize) * cellPx);
    int er = static_cast<int>(screenY + (m_exitPos.z / m_cellSize) * cellPx);
    DrawCircle(ec, er, cellPx * 0.4f, EXIT_COLOR);

    DrawRectangleLines(
        screenX - 1, screenY - 1,
        static_cast<int>(m_cols * cellPx) + 2,
        static_cast<int>(m_rows * cellPx) + 2,
        Color{200, 200, 220, 150}
    );
}
