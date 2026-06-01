cmake_minimum_required(VERSION 3.16)
project(maze_run_3d)

include(FetchContent)
FetchContent_Declare(raylib
    GIT_REPOSITORY https://github.com/raysan5/raylib.git
    GIT_TAG 5.5
)
FetchContent_MakeAvailable(raylib)

add_executable(maze_run_3d
    src/main.cpp
    src/Game.cpp
    src/Game.h
    src/Player.cpp
    src/Player.h
    src/Maze.cpp
    src/Maze.h
    src/Enemy.cpp
    src/Enemy.h
)
target_include_directories(maze_run_3d PRIVATE src)
target_link_libraries(maze_run_3d raylib)
target_link_options(maze_run_3d PRIVATE -static-libgcc -static-libstdc++ -static -mwindows)
