@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

REM Launch PowerShell script directly
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_fixed.ps1"
exit /b %errorlevel%

REM If script reaches here, exit
exit /b 0

echo.
echo ==========================================
echo      NeuralES WebApp - Setup Complet
echo ==========================================
echo.
echo [ETAPE 0/3] VERIFICATION DE NODE.JS
echo.

node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed - please install Node.js first
    exit /b 1
)

echo Node.js version:
node --version
echo npm version:
npm --version
echo.
echo [ETAPE 1/3] CREATION DU FICHIER .env
echo.
REM Find available port
set "PORT=5173"
:find_port
netstat -ano | findstr ":%PORT%" >nul 2>&1
if %errorlevel%==0 (
    set /a PORT+=1
    if %PORT% GTR 59999 (
        echo ERROR: No available port found
        exit /b 1
    )
    goto find_port
)

echo Using port: %PORT%
echo.

REM Create .env if it doesn't exist
if not exist ".env" (
    (
        echo # Frontend Configuration
        echo VITE_API_URL=http://localhost:8000
        echo VITE_APP_NAME=NeuralES
        echo VITE_PORT=%PORT%
    ) > .env
    echo [OK] .env created
) else (
    echo [OK] .env already exists
    findstr /M "VITE_PORT" .env >nul 2>&1
    if errorlevel 1 (
        echo VITE_PORT=%PORT%>> .env
    )
)
echo.
echo [ETAPE 2/3] INSTALLATION DES DEPENDANCES
echo.

REM Install dependencies
if not exist "node_modules" (
    echo Installing node modules
    call npm install
    if errorlevel 1 (
        echo ERROR: npm install failed
        exit /b 1
    )
)
echo [OK] Dependencies installed
echo.


REM ETAPE 3: Start server
echo ==========================================
echo     Setup Complete!
echo ==========================================
echo.
echo [ETAPE 3/3] STARTING SERVER
echo.
echo Server: http://localhost:%PORT%
echo.

npm run dev

endlocal