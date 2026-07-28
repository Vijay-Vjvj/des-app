@echo off
title AI Interview Preparation
cd /d "%~dp0"
echo Starting AI Interview Preparation...
call venv\Scripts\activate.bat
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with an error. Press any key to close...
    pause > nul
)
