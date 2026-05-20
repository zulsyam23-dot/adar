#Requires -Version 5.1
<#
.SYNOPSIS
    Adar — One-click installer for Windows
.DESCRIPTION
    Downloads and installs adar.exe and adarpc.exe,
    then adds them to the system PATH.
.EXAMPLE
    .\install.ps1
#>

$ErrorActionPreference = "Stop"
$Repo = "https://github.com/zulsyam23-dot/adar/releases/latest/download"
$InstallDir = "$env:LOCALAPPDATA\Adar"
$AdarExe = "$InstallDir\adar.exe"
$AdarpcExe = "$InstallDir\adarpc.exe"

function Write-Step {
    param($Icon, $Text)
    Write-Host "$Icon $Text"
}

function Download-File {
    param($Url, $Path, $Name)
    try {
        $wc = New-Object System.Net.WebClient
        Write-Progress -Activity "Downloading $Name..." -Status "0%" -PercentComplete 0
        $wc.DownloadFile($Url, $Path)
        Write-Progress -Activity "Downloading $Name..." -Completed
        return $true
    } catch {
        return $false
    }
}

# ─── Start ─────────────────────────────────────────────
Clear-Host
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "        Adar v0.1.0 — Windows Installer     " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Create install directory
Write-Step "~" "Membuat folder $InstallDir..."
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
Write-Step "[OK]" "Folder siap" -ForegroundColor Green

# 2. Download exe files
Write-Step "~" "Mendownload adar.exe dari GitHub Releases..."
$ok = Download-File "$Repo/adar.exe" $AdarExe "adar.exe"
if (-not $ok) {
    Write-Step "[X]" "Gagal mendownload adar.exe" -ForegroundColor Red
    Write-Step "!" "Download manual: $Repo/adar.exe" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Step "[OK]" "adar.exe selesai" -ForegroundColor Green

Write-Step "~" "Mendownload adarpc.exe..."
$ok = Download-File "$Repo/adarpc.exe" $AdarpcExe "adarpc.exe"
if (-not $ok) {
    Write-Step "[X]" "Gagal mendownload adarpc.exe" -ForegroundColor Red
    Write-Step "!" "Download manual: $Repo/adarpc.exe" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Step "[OK]" "adarpc.exe selesai" -ForegroundColor Green

# 3. Add to PATH
Write-Step "~" "Menambahkan ke PATH pengguna..."
$oldPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($oldPath -notlike "*$InstallDir*") {
    $newPath = "$oldPath;$InstallDir"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Step "[OK]" "PATH berhasil ditambahkan" -ForegroundColor Green
} else {
    Write-Step "[OK]" "Adar sudah ada di PATH" -ForegroundColor Green
}

# 4. Verify
Write-Step "~" "Memverifikasi instalasi..."
$env:Path = [Environment]::GetEnvironmentVariable("Path", "User") + ";$env:Path"
try {
    $ver = & $AdarExe --help 2>&1 | Select-Object -First 1
    Write-Step "[OK]" "Instalasi berhasil!" -ForegroundColor Green
} catch {
    Write-Step "[!]" "Verifikasi gagal. Coba buka terminal baru." -ForegroundColor Yellow
}

# 5. Done
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Cara pakai:" -ForegroundColor White
Write-Host "    adar build style.adar -o dist\" -ForegroundColor Gray
Write-Host "    adar check style.adar" -ForegroundColor Gray
Write-Host "    adarpc init project" -ForegroundColor Gray
Write-Host "    adarpc build" -ForegroundColor Gray
Write-Host "    adarpc serve" -ForegroundColor Gray
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
pause
