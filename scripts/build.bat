@echo off
REM Build standalone executable for Windows

setlocal enabledelayedexpansion

cd /d "%~dp0.."

echo === Antidetect Browser Build Script ===
echo.

REM Check if venv exists
if not exist ".venv" (
    echo ERROR: Virtual environment not found.
    echo Run setup.bat first.
    pause
    exit /b 1
)

REM Activate venv
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install package dependencies
echo Installing package dependencies...
pip install -e ".[gui,package]"

REM Generate icons
echo.
echo Generating application icons...
python scripts\generate_icons.py

REM Build with PyInstaller
echo.
echo Building executable with PyInstaller...
pyinstaller antidetect-browser.spec --clean --noconfirm

REM Check result
if exist "dist\AntidetectBrowser\AntidetectBrowser.exe" (
    echo.
    echo === Build successful! ===
    echo.
    echo Executable location:
    echo   dist\AntidetectBrowser\AntidetectBrowser.exe
    echo.
    echo To run:
    echo   dist\AntidetectBrowser\AntidetectBrowser.exe
    echo.
    echo To create distributable archive:
    echo   Right-click dist\AntidetectBrowser folder and "Send to > Compressed folder"
    echo   Or use: tar -a -cf AntidetectBrowser-Windows.zip dist\AntidetectBrowser
) else (
    echo.
    echo ERROR: Build failed. Check output above.
    pause
    exit /b 1
)

echo.
pause
