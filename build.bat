@echo off
REM Build script for Lemiex Record App
REM Creates Windows executable with PyInstaller

echo ====================================
echo Lemiex Record App - Build Script
echo ====================================
echo.

REM Ensure virtual environment is available
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo WARNING: venv not found - using global Python
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found - installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Detect version from config
set VERSION=
for /f "delims=" %%A in ('python -c "import yaml;print(yaml.safe_load(open(r'config/config.yaml', encoding='utf-8'))['app']['version'])"') do set VERSION=%%A
if "%VERSION%"=="" set VERSION=1.0.1
echo Target version: %VERSION%

echo [1/5] Cleaning previous build...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo Build folders cleaned
echo.

echo [2/5] Running PyInstaller...
pyinstaller --clean Lemiex-record-app.spec
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo Build completed successfully
echo.

echo [3/5] Creating distribution folder...
set DIST_FOLDER=LemiexRecordApp_v%VERSION%

if exist "%DIST_FOLDER%" rmdir /s /q "%DIST_FOLDER%"
mkdir "%DIST_FOLDER%"
mkdir "%DIST_FOLDER%\logs"
mkdir "%DIST_FOLDER%\temp_videos"
mkdir "%DIST_FOLDER%\metadata"
mkdir "%DIST_FOLDER%\config"

echo [4/5] Copying files to distribution folder...
copy "dist\LemiexRecordApp.exe" "%DIST_FOLDER%\" >nul
copy ".env.example" "%DIST_FOLDER%\" >nul
copy "README.md" "%DIST_FOLDER%\" >nul
copy "USER_MANUAL.md" "%DIST_FOLDER%\" >nul
copy "INSTALL.md" "%DIST_FOLDER%\INSTALL_PORTABLE.md" >nul
copy "requirements.txt" "%DIST_FOLDER%\" >nul
xcopy "config" "%DIST_FOLDER%\config" /E /I /Y >nul
echo.

echo [5/5] Creating ZIP archive...
powershell Compress-Archive -Path "%DIST_FOLDER%" -DestinationPath "%DIST_FOLDER%.zip" -Force
if errorlevel 1 (
    echo WARNING: Failed to create ZIP archive
    echo You can manually zip the folder: %DIST_FOLDER%
) else (
    echo ZIP archive created: %DIST_FOLDER%.zip
)
echo.

echo ====================================
echo Build completed successfully!
echo ====================================
echo.
echo Executable location: dist\LemiexRecordApp.exe
echo Distribution folder: %DIST_FOLDER%\
echo ZIP archive: %DIST_FOLDER%.zip
echo.
echo File size:
dir /s "dist\LemiexRecordApp.exe" | find "LemiexRecordApp.exe"
echo.
echo Next steps:
echo 1. Test the executable: %DIST_FOLDER%\LemiexRecordApp.exe
echo 2. Configure .env file with B2 credentials
echo 3. Commit/tag version %VERSION% and upload %DIST_FOLDER%.zip to GitHub Releases
echo.
pause
