@echo off
REM R-Defender Build Script for Windows
REM This script builds the Windows installer

echo.
echo ================================
echo R-DEFENDER BUILD SYSTEM
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check PyInstaller
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Error: PyInstaller is not installed
    echo Install it with: pip install pyinstaller
    pause
    exit /b 1
)

REM Check NSIS
makensis /version >nul 2>&1
if errorlevel 1 (
    echo Error: NSIS is not installed
    echo Download from: https://nsis.sourceforge.io/Download
    pause
    exit /b 1
)

echo Building R-Defender installer...
python build.py

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Installer: RDefender-Setup.exe
echo.
pause
