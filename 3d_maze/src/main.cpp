#include "raylib.h"
#include "Game.h"
#include "Maze.h"
#include <cstdio>
#include <string>

int main(int argc, char** argv) {
    for (int i = 1; i < argc; ++i) {
        if (std::string(argv[i]) == "--validate") {
            if (Maze::ValidateAllLevels()) {
                std::printf("Maze validation: OK (10 levels)\n");
                return 0;
            }
            std::printf("Maze validation: FAILED\n");
            return 1;
        }
    }

    const int screenWidth = 1280;
    const int screenHeight = 720;

    InitWindow(screenWidth, screenHeight, "Gem Hunter 3D");
    SetExitKey(KEY_NULL);
    SetTargetFPS(60);

    Game game(screenWidth, screenHeight);
    game.Run();

    return 0;
}
