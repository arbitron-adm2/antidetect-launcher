@echo off
REM Quick build script - builds without installer
REM For full installer, use build_windows.bat

echo Building Antidetect Browser (Quick Build)...
echo.

python -m PyInstaller antidetect-browser.spec --clean --noconfirm

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build complete!
echo Executable: dist\AntidetectBrowser\AntidetectBrowser.exe
echo.
pause
