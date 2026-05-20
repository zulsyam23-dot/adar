@echo off
title Adar Installer
echo ====================================
echo      Adar v0.1.0 — Installer
echo ====================================
echo.

set "EXE_DIR=%~dp0dist-exe"
set "ADAR_EXE=%EXE_DIR%\adar.exe"
set "ADARPC_EXE=%EXE_DIR%\adarpc.exe"
set "REPO=https://github.com/zulsyam23-dot/adar/releases/latest/download"

:: Check if already installed
where adar.exe >nul 2>nul
if %errorlevel% equ 0 (
    echo [✓] Adar sudah terinstal di PATH.
    echo     Jalankan: adar --help
    echo.
    choice /c QN /n /m "Tekan Q untuk keluar, N untuk install ulang: "
    if errorlevel 2 exit /b
)

:: Check if adar.exe exists locally
if not exist "%ADAR_EXE%" (
    echo [~] adar.exe tidak ditemukan di folder dist-exe\
    echo [~] Mendownload dari GitHub Releases...
    echo.
    where curl >nul 2>nul
    if %errorlevel% equ 0 (
        curl -L -o "%ADAR_EXE%" "%REPO%/adar.exe" --progress-bar
        if %errorlevel% neq 0 (
            echo [X] Gagal mendownload adar.exe.
            echo     Download manual: %REPO%/adar.exe
            pause
            exit /b 1
        )
        curl -L -o "%ADARPC_EXE%" "%REPO%/adarpc.exe" --progress-bar
    ) else (
        echo [X] curl tidak ditemukan. Download manual:
        echo     %REPO%/adar.exe
        echo     %REPO%/adarpc.exe
        pause
        exit /b 1
    )
)

echo [~] Menambahkan Adar ke PATH pengguna...
setx PATH "%PATH%;%EXE_DIR%" >nul
if %errorlevel% equ 0 (
    echo [✓] Adar berhasil diinstal!
) else (
    echo [!] Gagal menambah ke PATH. Jalankan sebagai Administrator.
)

echo.
echo ====================================
echo   Cara pakai:
echo     adar build style.adar -o dist\
echo     adar check style.adar
echo     adarpc init project
echo     adarpc build
echo     adarpc serve
echo ====================================
echo.
pause
