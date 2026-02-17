#!/usr/bin/env pwsh

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      NeuralES WebApp - Setup Complet" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ETAPE 0: Verify Node.js
Write-Host "[ETAPE 0/3] VERIFICATION DE NODE.JS" -ForegroundColor Yellow
Write-Host ""

$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Node.js not installed" -ForegroundColor Red
    Exit 1
}

Write-Host "Node.js version: $nodeVersion"
npm --version | ForEach-Object { Write-Host "npm version: $_" }
Write-Host ""

# ETAPE 1: Create .env and find port
Write-Host "[ETAPE 1/3] CREATION DU FICHIER .env" -ForegroundColor Yellow
Write-Host ""

$port = 5173
$netstat = netstat -ano | Select-String ":$port " -ErrorAction SilentlyContinue
while ($netstat) {
    $port++
    if ($port -ge 59999) {
        Write-Host "ERROR: No available port found" -ForegroundColor Red
        Exit 1
    }
    $netstat = netstat -ano | Select-String ":$port " -ErrorAction SilentlyContinue
}

Write-Host "Using port: $port"

if (Test-Path ".env") {
    Write-Host ".env already exists"
} else {
    @(
        "# Frontend Configuration",
        "VITE_API_URL=http://localhost:8000",
        "VITE_APP_NAME=NeuralES",
        "VITE_PORT=$port"
    ) | Set-Content ".env" -Encoding UTF8
    Write-Host ".env created"
}
Write-Host ""

# ETAPE 2: Install dependencies
Write-Host "[ETAPE 2/3] INSTALLATION DES DEPENDANCES" -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..."
    & npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: npm install failed" -ForegroundColor Red
        Exit 1
    }
} else {
    Write-Host "node_modules already exists, skipping npm install"
}
Write-Host ""

# ETAPE 3: Start server
Write-Host "==========================================" -ForegroundColor Green
Write-Host "     Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "[ETAPE 3/3] STARTING SERVER" -ForegroundColor Yellow
Write-Host ""
Write-Host "Server: http://localhost:$port" -ForegroundColor Green
Write-Host ""

Write-Host "Starting development server..." -ForegroundColor Cyan
& npm run dev
