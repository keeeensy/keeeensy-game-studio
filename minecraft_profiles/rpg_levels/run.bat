@echo off
chcp 65001 >nul
title Minecraft - RPG Levels Mod
cd /d "%~dp0\..\.."
PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0\..\launch_fabric.ps1" -Profile rpg_levels
if errorlevel 1 pause