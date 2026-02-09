@echo off
REM Script pour créer et configurer le fichier .env

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo      Configuration du fichier .env
echo ==========================================
echo.

if exist ".env" (
    echo [!] Le fichier .env existe déjà
    echo Voulez-vous le recréer? (O/N)
    set /p choice=
    if /i not "!choice!"=="O" (
        echo Annulation
        pause
        exit /b 0
    )
)

echo.
echo Copie de .env.example vers .env...
copy ".env.example" ".env"

if errorlevel 1 (
    powershell Write-Host "[ERROR] Erreur lors de la copie" -ForegroundColor Red
    pause
    exit /b 1
)

echo.
powershell Write-Host "Fichier .env créé avec succès!" -ForegroundColor Green
echo.
echo Prochaine étape - Configure tes paramètres dans .env:
echo   1. Ouvre le fichier .env dans VS Code
echo   2. Modifier les valeurs:
echo      - DATABASE_URL = postgresql+psycopg2://user:password@localhost:5432/neurales
echo      - Remplace "user" et "password" par tes identifiants PostgreSQL
echo.
echo IMPORTANT:
echo   Avant de lancer le backend, assure-toi que:
echo   1. PostgreSQL est installé
echo   2. La base de données "neurales" est créée
echo   3. Le fichier .env est correctement configuré
echo.
echo.
echo code .env
timeout /t 3
code .env
pause
