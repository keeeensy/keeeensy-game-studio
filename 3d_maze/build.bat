@echo off
cd /d "%~dp0"
set CMAKE_PATH=C:\Users\keeeensy\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages\cmake\data\bin
set PATH=%CMAKE_PATH%;%PATH%
if not exist build mkdir build
cd build
cmake .. -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release
if %errorlevel% neq 0 (
    echo CMake configuration failed.
    pause
    exit /b 1
)
make -j%NUMBER_OF_PROCESSORS%
if %errorlevel% neq 0 (
    echo Build failed.
    pause
    exit /b 1
)
copy /y maze_run_3d.exe ..\maze_run_3d.exe
echo.
echo Build OK - maze_run_3d.exe
pause
