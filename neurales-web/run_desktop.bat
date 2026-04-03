@echo off
REM Demarrer NeuralES en mode desktop (Tauri)

cd /d "%~dp0"

echo.
echo ==========================================
echo      NeuralES Desktop (Tauri) - Dev
echo ==========================================
echo.

echo Une fenetre PowerShell va s'ouvrir.
echo Pour arreter: Ctrl+C dans la fenetre PowerShell.
echo.
start "NeuralES Desktop" /wait powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_desktop.ps1"

pause
