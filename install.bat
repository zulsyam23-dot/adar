@echo off
echo Installing Adar...
echo.

set "EXE_DIR=%~dp0dist-exe"

if not exist "%EXE_DIR%\adar.exe" (
    echo ERROR: adar.exe not found in %EXE_DIR%
    echo Run 'python scripts\build_exe.py' first.
    exit /b 1
)

:: Add to PATH for current user
setx PATH "%PATH%;%EXE_DIR%" /M 2>nul

echo.
echo Adar installed!
echo.
echo Try: adar build examples\src\button.adar -o dist\
echo       adarpc --help
echo.
pause
