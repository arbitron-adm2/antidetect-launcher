@echo off
REM Windows Build Script for Antidetect Browser
REM Requires: Python 3.12+, PyInstaller, Inno Setup

setlocal enabledelayedexpansion

echo ========================================
echo Antidetect Browser - Windows Build
echo ========================================
echo.

REM Configuration
set APP_NAME=AntidetectBrowser
set VERSION=0.1.0
set PYTHON=python
set INNO_SETUP="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

REM Colors (if supported)
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set BLUE=[94m
set NC=[0m

REM Step 1: Check Python installation
echo %BLUE%[1/6] Checking Python installation...%NC%
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo %RED%Error: Python not found. Please install Python 3.12 or later.%NC%
    exit /b 1
)
%PYTHON% --version
echo.

REM Step 2: Install/upgrade dependencies
echo %BLUE%[2/6] Installing dependencies...%NC%
%PYTHON% -m pip install --upgrade pip
if errorlevel 1 (
    echo %RED%Error: Failed to upgrade pip%NC%
    exit /b 1
)

%PYTHON% -m pip install -e ".[gui,package]"
if errorlevel 1 (
    echo %RED%Error: Failed to install dependencies%NC%
    exit /b 1
)
echo.

REM Step 3: Generate icons
echo %BLUE%[3/6] Generating application icons...%NC%
if not exist "build\icons" mkdir build\icons

if exist "src\antidetect_playwright\resources\icon.svg" (
    echo Generating icon.ico from SVG...
    %PYTHON% build\generate_icons.py
    if errorlevel 1 (
        echo %YELLOW%Warning: Icon generation failed, using default icon%NC%
    )
) else (
    echo %YELLOW%Warning: icon.svg not found, skipping icon generation%NC%
)
echo.

REM Step 4: Clean previous builds
echo %BLUE%[4/6] Cleaning previous builds...%NC%
if exist "dist" (
    echo Removing dist directory...
    rmdir /s /q dist
)
if exist "build\AntidetectBrowser" (
    echo Removing build directory...
    rmdir /s /q build\AntidetectBrowser
)
echo.

REM Step 5: Build with PyInstaller
echo %BLUE%[5/6] Building executable with PyInstaller...%NC%
%PYTHON% -m PyInstaller antidetect-browser.spec --clean --noconfirm
if errorlevel 1 (
    echo %RED%Error: PyInstaller build failed%NC%
    exit /b 1
)
echo %GREEN%Build successful: dist\AntidetectBrowser\%NC%
echo.

REM Step 6: Create installer
echo %BLUE%[6/6] Creating installer with Inno Setup...%NC%

if not exist %INNO_SETUP% (
    echo %YELLOW%Warning: Inno Setup not found at %INNO_SETUP%%NC%
    echo Please install Inno Setup 6 from https://jrsoftware.org/isinfo.php
    echo Or update the INNO_SETUP path in this script.
    echo.
    echo %GREEN%Build complete without installer%NC%
    echo Executable location: dist\AntidetectBrowser\%APP_NAME%.exe
    goto :end
)

%INNO_SETUP% build\installer.iss
if errorlevel 1 (
    echo %RED%Error: Installer creation failed%NC%
    echo %YELLOW%But executable is available at: dist\AntidetectBrowser\%APP_NAME%.exe%NC%
    exit /b 1
)

echo.
echo %GREEN%========================================%NC%
echo %GREEN%Build Complete!%NC%
echo %GREEN%========================================%NC%
echo.
echo Executable: dist\AntidetectBrowser\%APP_NAME%.exe
echo Installer:  dist\%APP_NAME%-Setup-%VERSION%.exe
echo.

:end
endlocal
pause
