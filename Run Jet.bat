@echo off
title Fighter Jet Follower
echo.
echo  [JET] Fighter Jet Cursor Follower
echo  Starting...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found! Install from https://python.org
    pause
    exit /b 1
)

pythonw jet_follower.py 2>nul || python jet_follower.py
