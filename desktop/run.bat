@echo off
REM Démarrer l'application NeuralES Desktop

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Afficher info
echo.
echo ==========================================
echo      NeuralES Desktop - Startup
echo ==========================================
echo.

REM Démarrer le serveur
echo Demarrage de l'application (PowerShell)...
echo.
echo Une fenetre PowerShell va s'ouvrir. Ferme l'application pour revenir ici.
echo Le nettoyage des caches sera fait automatiquement apres l'arret.
echo.
start "NeuralES Desktop" /wait powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1"

pause
