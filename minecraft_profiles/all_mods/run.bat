@echo off
chcp 65001 >nul
title Minecraft - All Mods (RPG Levels + Death Marker)
cd /d "%~dp0\..\.."
PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0\..\launch_fabric.ps1" -Profile all_mods
if errorlevel 1 pause