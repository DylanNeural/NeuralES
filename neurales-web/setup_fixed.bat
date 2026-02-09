@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ==========================================
echo      NeuralES WebApp - Setup Complet
echo ==========================================
echo.

REM ETAPE 0: Verifier Node.js
echo [ETAPE 0/3] VERIFICATION DE NODE.JS
echo.

node --version >nul 2>&1
if errorlevel 1 (
    echo      Node.js n'est pas installe
    echo      Tentative d'installation via winget...
    echo.
    
    winget install --id OpenJS.NodeJS --accept-source-agreements --accept-package-agreements --silent >nul 2>&1
    
    echo      Installation effectuee
    echo      Patientez quelques secondes...
    timeout /t 3 /nobreak >nul
    echo.
)

echo      Node.js version: 
node --version
echo      npm version: 
npm --version
echo      [OK] Node.js configure
echo.

REM ETAPE 1: Creer .env
echo [ETAPE 1/3] CREATION DU FICHIER .env
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo      [OK] Fichier .env copie depuis .env.example
    ) else (
        (
            echo # Frontend Configuration
            echo VITE_API_URL=http://localhost:8000
            echo VITE_APP_NAME=NeuralES
        ) > .env
        echo      [OK] Fichier .env cree
    )
) else (
    echo      [OK] Fichier .env deja present
)
echo.

REM ETAPE 2: Installer dependances
echo [ETAPE 2/3] INSTALLATION DES DEPENDANCES
echo.

call npm install
if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'installation des dependances
    pause
    exit /b 1
)

echo.
echo      [OK] Dependances installees
echo.

REM ETAPE 3: Demarrer
echo ==========================================
echo      Setup termine!
echo ==========================================
echo.
echo [ETAPE 3/3] DEMARRAGE DU SERVEUR
echo.
echo Serveur: http://localhost:5173
echo Ctrl+C pour arreter
echo.

call npm run dev

endlocal
