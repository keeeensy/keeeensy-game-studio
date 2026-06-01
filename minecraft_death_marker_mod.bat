@echo off
chcp 65001 >nul
title Minecraft - Death Marker Mod
cd /d "%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0minecraft_profiles\launch_fabric.ps1" -Profile death_marker
if errorlevel 1 pause
