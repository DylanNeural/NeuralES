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
echo Demarrage du serveur Uvicorn...
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
