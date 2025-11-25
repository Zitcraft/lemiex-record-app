@echo off
REM Quick run script for Windows

echo Starting Lemiex Record App...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if venv is activated
if "%VIRTUAL_ENV%"=="" (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Run the application
python main.py

REM Deactivate on exit
deactivate
