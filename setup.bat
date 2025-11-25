@echo off
REM Quick setup script for Windows

echo ====================================
echo Lemiex Record App - Quick Setup
echo ====================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Python detected
echo.

REM Create virtual environment
if not exist "venv" (
    echo [2/5] Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo [2/5] Virtual environment already exists
)
echo.

REM Activate virtual environment and install dependencies
echo [3/5] Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.

REM Create .env file if not exists
if not exist ".env" (
    echo [4/5] Creating .env file...
    copy .env.example .env
    echo Please edit .env file with your B2 credentials
) else (
    echo [4/5] .env file already exists
)
echo.

REM Create directories
echo [5/5] Creating directories...
if not exist "logs" mkdir logs
if not exist "temp_videos" mkdir temp_videos
echo.

echo ====================================
echo Setup completed successfully!
echo ====================================
echo.
echo Next steps:
echo 1. Edit .env file with your Backblaze B2 credentials
echo 2. Edit config/config.yaml if needed
echo 3. Run the application with: run.bat
echo.
pause
