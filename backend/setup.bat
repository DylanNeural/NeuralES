@echo off
REM Installation complète et démarrage du backend NeuralES

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ==========================================
echo      NeuralES Backend - Setup Complet
echo ==========================================
echo.

REM ETAPE 0: Créer le fichier .env s'il n'existe pas
if not exist ".env" (
    powershell Write-Host "[ETAPE 0/3] CREATION DU FICHIER .env" -ForegroundColor Red
    echo      Copie de .env.example vers .env...
    copy ".env.example" ".env" >nul
    if errorlevel 1 (
        powershell Write-Host "[ERROR] Erreur lors de la copie de .env.example" -ForegroundColor Red
        pause
        exit /b 1
    )
    echo      ✓ Fichier .env créé
    echo.
    echo      IMPORTANT: Configure tes identifiants PostgreSQL dans .env:
    echo      - DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/neurales
    echo      - Remplace "user" et "password" par tes identifiants
    echo.
    echo      Fichier ouvert dans VS Code pour édition...
    timeout /t 2 >nul
    code .env
    echo.
    echo      Verifie que PostgreSQL est installé et que la DB "neurales" existe!
    echo.
    pause
) else (
    powershell Write-Host "[ETAPE 0/3] FICHIER .env DEJA PRESENT" -ForegroundColor Red
    echo      Configuration trouvée ✓
)

echo.

REM Vérifier si venv existe
if not exist "venv\" (
    powershell Write-Host "[ETAPE 1/3] CREATION DU VIRTUAL ENVIRONMENT" -ForegroundColor Red
    echo      Localisation: %CD%\venv
    echo      Python version: 
    python --version
    echo      Création en cours...
    python -m venv venv
    if errorlevel 1 (
        powershell Write-Host "[ERROR] Python n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
        pause
        exit /b 1
    )
    echo      ✓ Virtual environment créé avec succès
) else (
    powershell Write-Host "[ETAPE 1/3] VIRTUAL ENVIRONMENT DEJA PRESENT" -ForegroundColor Red
    echo      Localisation: %CD%\venv
)

echo.

REM Activer venv
powershell Write-Host "[ETAPE 2/3] ACTIVATION DU VIRTUAL ENVIRONMENT" -ForegroundColor Red
echo      Activation depuis: %CD%\venv\Scripts\activate.bat
call venv\Scripts\activate.bat
if errorlevel 1 (
    powershell Write-Host "[ERROR] Erreur lors de l'activation du venv" -ForegroundColor Red
    pause
    exit /b 1
)
echo      ✓ Virtual environment activé

echo.

REM Installer les dépendances
powershell Write-Host "[ETAPE 3/3] INSTALLATION DES DEPENDANCES" -ForegroundColor Red
echo      Fichier: requirements.txt
echo      Installation en cours...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    powershell Write-Host "[ERROR] Erreur lors de l'installation des dépendances" -ForegroundColor Red
    pause
    exit /b 1
)
echo.
echo      ✓ Toutes les dépendances installées

echo.
echo ==========================================
echo      Setup terminé avec succès!
echo ==========================================
echo.
echo Démarrage du backend...
echo Serveur disponible sur: http://localhost:8000
echo Documentation: http://localhost:8000/docs
echo API Swagger: http://localhost:8000/docs
echo.
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.

python -m uvicorn app.main:app --reload
