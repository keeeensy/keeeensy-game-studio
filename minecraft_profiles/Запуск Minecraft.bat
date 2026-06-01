@echo off
chcp 65001 >nul
title Minecraft - All Mods
cd /d "%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch_fabric.ps1" -Profile all_mods
if errorlevel 1 pause
