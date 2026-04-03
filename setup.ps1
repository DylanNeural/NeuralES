# NeuralES Setup Script
# Installe tous les pré-requis et prépare l'environnement
# Usage: .\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   NeuralES - Project Setup"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# ====== ÉTAPE 1: Vérifier Python ======
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Python 3.10+ is required" -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Cyan
    exit 1
}
Write-Host "  ✓ Python: $pythonVersion" -ForegroundColor Green

# ====== ÉTAPE 2: Vérifier Node.js ======
Write-Host "[2/6] Checking Node.js installation..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Node.js 18+ is required" -ForegroundColor Red
    Write-Host "  Download from: https://nodejs.org/" -ForegroundColor Cyan
    exit 1
}
Write-Host "  ✓ Node.js: $nodeVersion" -ForegroundColor Green

# ====== ÉTAPE 3: Vérifier PuTTY (plink) ======
Write-Host "[3/6] Checking PuTTY (plink) installation..." -ForegroundColor Yellow
$plinkPath = "C:\Program Files\PuTTY\plink.exe"
if (-not (Test-Path $plinkPath)) {
    Write-Host "  ERROR: PuTTY is required for SSH tunneling" -ForegroundColor Red
    Write-Host "  Download from: https://www.chiark.greenend.org.uk/~sgtatham/putty/" -ForegroundColor Cyan
    exit 1
}
Write-Host "  ✓ PuTTY found" -ForegroundColor Green

# ====== ÉTAPE 4: Créer venv backend ======
Write-Host "[4/6] Setting up backend environment..." -ForegroundColor Yellow
$backendVenv = "backend\venv"
if (-not (Test-Path $backendVenv)) {
    Write-Host "  Creating Python virtual environment..." -ForegroundColor Gray
    python -m venv $backendVenv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Failed to create venv" -ForegroundColor Red
        exit 1
    }
}

# Installer dépendances backend
Write-Host "  Installing Python dependencies..." -ForegroundColor Gray
& "$backendVenv\Scripts\pip.exe" install -q -r "backend\requirements.txt" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Failed to install Python packages" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Backend environment ready" -ForegroundColor Green

# ====== ÉTAPE 5: Créer venv web ======
Write-Host "[5/6] Setting up web environment..." -ForegroundColor Yellow
Push-Location "neurales-web"
if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing npm dependencies..." -ForegroundColor Gray
    npm install --silent 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: Failed to install npm packages" -ForegroundColor Red
        exit 1
    }
}
Write-Host "  ✓ Web environment ready" -ForegroundColor Green
Pop-Location

# ====== ÉTAPE 6: Créer .env files ======
Write-Host "[6/6] Configuring environment variables..." -ForegroundColor Yellow

# Backend .env
if (-not (Test-Path "backend\.env")) {
    Write-Host "  Creating backend\.env..." -ForegroundColor Gray
    Copy-Item "backend\.env.example" "backend\.env" -Force
    Write-Host "  ⚠  Please update backend\.env with your credentials" -ForegroundColor Yellow
}

# Web .env
if (-not (Test-Path "neurales-web\.env")) {
    Write-Host "  Creating neurales-web\.env..." -ForegroundColor Gray
    @"
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
"@ | Out-File "neurales-web\.env" -Encoding UTF8
}

Write-Host "  ✓ Environment files ready" -ForegroundColor Green

# ====== Résumé ======
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Setup Complete!"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Edit backend\.env if needed" -ForegroundColor Gray
Write-Host "  2. Run: .\run.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "Backend will run on: http://localhost:8000" -ForegroundColor Gray
Write-Host "Web will run on:     http://localhost:5173" -ForegroundColor Gray
Write-Host ""
