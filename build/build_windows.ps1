# PowerShell Build Script for Antidetect Browser
# Requires: Python 3.12+, PyInstaller, Inno Setup
# Usage: .\build\build_windows.ps1

param(
    [switch]$Clean = $false,
    [switch]$NoInstaller = $false,
    [switch]$Sign = $false,
    [string]$SignCert = "",
    [string]$SignPassword = ""
)

# Configuration
$AppName = "AntidetectBrowser"
$Version = "0.1.0"
$InnoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

# Error handling
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] " -NoNewline -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[✓] $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[✗] $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor Yellow
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Antidetect Browser - Windows Build  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

try {
    # Step 1: Check Python
    Write-Step "Checking Python installation..."
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found. Please install Python 3.12 or later."
    }
    Write-Success "Python found: $pythonVersion"

    # Step 2: Install dependencies
    Write-Step "Installing dependencies..."
    python -m pip install --upgrade pip --quiet
    python -m pip install -e ".[gui,package]" --quiet
    Write-Success "Dependencies installed"

    # Step 3: Generate icons
    Write-Step "Generating application icons..."
    if (-not (Test-Path "build\icons")) {
        New-Item -ItemType Directory -Path "build\icons" -Force | Out-Null
    }

    if (Test-Path "src\antidetect_playwright\resources\icon.svg") {
        python build\generate_icons.py
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Icons generated successfully"
        } else {
            Write-Warning-Custom "Icon generation failed, using default icon"
        }
    } else {
        Write-Warning-Custom "icon.svg not found, skipping icon generation"
    }

    # Step 4: Clean previous builds
    if ($Clean) {
        Write-Step "Cleaning previous builds..."
        if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
        if (Test-Path "build\AntidetectBrowser") { Remove-Item -Recurse -Force "build\AntidetectBrowser" }
        Write-Success "Cleaned previous builds"
    }

    # Step 5: Build with PyInstaller
    Write-Step "Building executable with PyInstaller..."
    python -m PyInstaller antidetect-browser.spec --clean --noconfirm
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed"
    }
    Write-Success "Executable built: dist\$AppName\"

    # Step 6: Code signing (optional)
    if ($Sign -and $SignCert) {
        Write-Step "Signing executable..."
        $exePath = "dist\$AppName\$AppName.exe"

        if (Test-Path $SignCert) {
            $signTool = "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe"
            $signToolPath = (Get-Item $signTool | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

            if ($signToolPath) {
                $signArgs = @(
                    "sign",
                    "/f", "`"$SignCert`"",
                    "/p", "`"$SignPassword`"",
                    "/tr", "http://timestamp.digicert.com",
                    "/td", "SHA256",
                    "/fd", "SHA256",
                    "`"$exePath`""
                )

                & $signToolPath $signArgs
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "Executable signed successfully"
                } else {
                    Write-Warning-Custom "Code signing failed"
                }
            } else {
                Write-Warning-Custom "SignTool not found. Install Windows SDK."
            }
        } else {
            Write-Warning-Custom "Certificate not found: $SignCert"
        }
    }

    # Step 7: Create installer
    if (-not $NoInstaller) {
        Write-Step "Creating installer with Inno Setup..."

        if (Test-Path $InnoSetupPath) {
            & $InnoSetupPath "build\installer.iss"
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Installer created: dist\$AppName-Setup-$Version.exe"

                # Sign installer if requested
                if ($Sign -and $SignCert) {
                    Write-Step "Signing installer..."
                    $installerPath = "dist\$AppName-Setup-$Version.exe"
                    $signToolPath = (Get-Item "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe" |
                                    Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

                    if ($signToolPath) {
                        & $signToolPath sign /f "$SignCert" /p "$SignPassword" `
                            /tr "http://timestamp.digicert.com" /td SHA256 /fd SHA256 "$installerPath"

                        if ($LASTEXITCODE -eq 0) {
                            Write-Success "Installer signed successfully"
                        }
                    }
                }
            } else {
                Write-Warning-Custom "Installer creation failed"
            }
        } else {
            Write-Warning-Custom "Inno Setup not found at: $InnoSetupPath"
            Write-Host "Please install from: https://jrsoftware.org/isinfo.php" -ForegroundColor Yellow
        }
    }

    # Summary
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "         Build Complete!               " -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "`nOutput files:" -ForegroundColor Cyan
    Write-Host "  Executable: dist\$AppName\$AppName.exe" -ForegroundColor White

    if (Test-Path "dist\$AppName-Setup-$Version.exe") {
        Write-Host "  Installer:  dist\$AppName-Setup-$Version.exe" -ForegroundColor White
    }

    Write-Host ""

} catch {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "           Build Failed!               " -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
