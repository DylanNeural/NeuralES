@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ==========================================
echo      NeuralES Mobile - Startup
echo ==========================================
echo.

REM Verification de Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Node.js introuvable. Installez Node.js depuis https://nodejs.org
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('node -v') do set NODE_VERSION=%%v
echo Node.js  : %NODE_VERSION%

REM Installation des dependances si node_modules absent
if not exist "node_modules\" (
    echo.
    echo node_modules absent, installation en cours...
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        echo ERREUR: npm install a echoue.
        pause
        exit /b 1
    )
    echo Dependances installees.
)

REM Affichage config
if exist ".env" (
    for /f "tokens=2 delims==" %%a in ('findstr "EXPO_PUBLIC_API_URL" .env') do set API_URL=%%a
)
echo API URL  : %API_URL%
echo Expo Go  : scannez le QR code avec l'app Expo Go
echo.
echo ==========================================
echo       Lancement de l'app mobile
echo ==========================================
echo.

npx expo start --clear
