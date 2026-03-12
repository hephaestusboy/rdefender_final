@echo off
REM R-Defender Clean Build Script (Fixed mscerts issue)
REM Run this on Windows to rebuild everything

echo.
echo ================================
echo R-DEFENDER CLEAN BUILD
echo ================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

REM Clean old builds
echo Cleaning old builds...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q RDefender-Setup.exe 2>nul

echo.
echo Building executable...
pyinstaller build_config.spec --clean

if errorlevel 1 (
    echo ERROR: PyInstaller failed
    pause
    exit /b 1
)

echo.
echo Building installer...
makensis installer.nsi

if errorlevel 1 (
    echo ERROR: NSIS failed
    pause
    exit /b 1
)

echo.
echo ================================
echo SUCCESS!
echo ================================
echo.
echo Created: RDefender-Setup.exe
echo Size: %~z0
echo.
echo Next steps:
echo 1. Uninstall old version (Add/Remove Programs)
echo 2. Run: RDefender-Setup.exe
echo 3. Test the application
echo.
pause
