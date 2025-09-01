@echo off
REM Complete Service Launcher for FastAPI User Management System (Windows)
REM This batch file starts both the FastAPI backend and GUI application

echo FastAPI User Management Service Launcher
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found
    echo Please create virtual environment first:
    echo   python -m venv venv
    echo   venv\Scripts\activate.bat
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting complete service stack...
python launcher.py %*

echo Service stopped.
pause