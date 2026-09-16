@echo off
title RadiVision AI — Native Desktop Clinical Workstation Launcher
color 0B
cls

echo =====================================================================
echo           RADIVISION AI - NATIVE DESKTOP CLINICAL SUITE
echo =====================================================================
echo.
echo [*] Initializing local workstation environment...
cd /d "%~dp0"

echo [*] Starting local AI Deep Learning Engine (server.py)...
start /b "" python server.py > nul 2>&1
timeout /t 2 /nobreak > nul

echo [*] Launching RadiVision AI Native Desktop Application...
cd frontend
call npm run electron

echo.
echo [*] Desktop session ended. Shutting down local engine...
taskkill /f /im python.exe /fi "WINDOWTITLE eq RadiVision*" > nul 2>&1
echo [*] Application closed cleanly.
exit
