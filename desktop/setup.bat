@echo off
REM Installation complète et démarrage de l'application desktop NeuralES

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ==========================================
echo    NeuralES Desktop - Setup Complet
echo ==========================================
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
echo      Fichier: app\requirements.txt
echo      Installation en cours...
echo.
pip install -r app\requirements.txt
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
echo Démarrage de l'application NeuralES Desktop...
echo.

python app\main.py

