@echo off
REM Démarrer le serveur NeuralES WebApp

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Afficher info
echo.
echo ==========================================
echo      NeuralES WebApp - Startup
echo ==========================================
echo.
echo WEB URL   : http://localhost:5173
echo API URL   : http://localhost:8000
echo.

REM Démarrer le serveur
echo Demarrage du serveur Vite (PowerShell)...
echo.
echo Une fenetre PowerShell va s'ouvrir. Arrete le serveur avec Ctrl+C dans cette fenetre.
echo Le nettoyage des caches sera fait automatiquement apres l'arret.
echo.
start "NeuralES WebApp" /wait powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1"

pause
