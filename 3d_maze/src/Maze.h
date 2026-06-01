#pragma once
#include "raylib.h"
#include <utility>
#include <vector>

struct WallQuad {
    int col;
    int row;
    int width;
    int height;
};

class Maze {
public:
    Maze();

    void Generate(int levelIndex);
    void Draw3D() const;
    void DrawMinimap(int screenX, int screenY, int size, Vector3 playerPos) const;

    bool IsSolid(int col, int row) const;
    bool IsWalkable(int col, int row) const;
    bool CheckCollision(Vector3 pos, float radius) const;

    Vector3 GetSpawnPos() const { return m_spawnPos; }
    Vector3 GetExitPos() const { return m_exitPos; }
    int GetSpawnCol() const { return m_spawnCol; }
    int GetSpawnRow() const { return m_spawnRow; }
    int GetExitCol() const { return m_exitCol; }
    int GetExitRow() const { return m_exitRow; }
    int GetCols() const { return m_cols; }
    int GetRows() const { return m_rows; }
    float GetCellSize() const { return m_cellSize; }
    void SetExitCell(int col, int row);

    std::vector<std::vector<bool>> ComputeReachable() const;
    static bool ValidateAllLevels();

private:
    struct CellInfo {
        bool wall = true;
        bool exit = false;
    };

    void GenerateBraidedMaze(int innerCols, int innerRows, unsigned int seed, float braidChance);
    void PlaceExitByBfs();
    void BuildWallMesh();

    std::vector<std::vector<CellInfo>> m_cells;
    std::vector<WallQuad> m_wallQuads;
    Vector3 m_spawnPos{};
    Vector3 m_exitPos{};
    int m_spawnCol = 1;
    int m_spawnRow = 1;
    int m_exitCol = 0;
    int m_exitRow = 0;
    int m_cols = 0;
    int m_rows = 0;
    float m_cellSize = 3.0f;
    float m_wallHeight = 3.0f;
};
