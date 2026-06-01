@echo off
chcp 65001 >nul
title Minecraft - Vanilla 26.1.2
cd /d "%~dp0\..\.."
PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0\..\launch_fabric.ps1" -Profile vanilla
if errorlevel 1 pause