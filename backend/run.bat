@echo off
REM Démarrer le serveur NeuralES Backend avec PostgreSQL dans le PATH

setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Ajouter PostgreSQL bin au PATH
set PATH=C:\Program Files\PostgreSQL\18\bin;%PATH%

REM Activer venv
call .\venv\Scripts\activate.bat

REM Afficher info
echo.
echo ==========================================
echo      NeuralES Backend - Startup
echo ==========================================
echo.
echo BASE DE DONNEES : %DATABASE_URL%
echo API URL   : http://localhost:8000
echo DOCS      : http://localhost:8000/docs
echo.

REM Démarrer le serveur
echo Demarrage du serveur Uvicorn (PowerShell)...
echo.
echo Une fenetre PowerShell va s'ouvrir. Arrete le serveur avec Ctrl+C dans cette fenetre.
echo Le nettoyage des caches sera fait automatiquement apres l'arret.
echo.
start "NeuralES Backend" /wait powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1"

pause
