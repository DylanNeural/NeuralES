#!/usr/bin/env pwsh
# Démarrer le serveur NeuralES WebApp

Set-Location -Path $PSScriptRoot

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "      NeuralES WebApp - Startup" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Vérifier Node.js
Write-Host "[1/3] Verification de Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Node.js n'est pas installe" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour quitter"
    Exit 1
}
Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
Write-Host ""

# Créer .env si nécessaire et détecter port disponible
Write-Host "[2/3] Configuration de l'environnement..." -ForegroundColor Yellow
$port = 5173
if (-not (Test-Path ".env")) {
    $netstat = netstat -ano | Select-String ":$port " -ErrorAction SilentlyContinue
    while ($netstat) {
        $port++
        if ($port -ge 59999) {
            Write-Host "ERREUR: Aucun port disponible" -ForegroundColor Red
            Exit 1
        }
        $netstat = netstat -ano | Select-String ":$port " -ErrorAction SilentlyContinue
    }
    
    @(
        "# Frontend Configuration",
        "VITE_API_BASE_URL=http://localhost:8000",
        "VITE_APP_NAME=NeuralES",
        "VITE_PORT=$port"
    ) | Set-Content ".env" -Encoding UTF8
    Write-Host ".env cree avec port $port" -ForegroundColor Green
} else {
    Write-Host ".env existe deja" -ForegroundColor Green
}

# Installer les dépendances si nécessaire
Write-Host "[3/3] Verification des dependances..." -ForegroundColor Yellow
if (-not (Test-Path "node_modules")) {
    Write-Host "Installation des dependances (npm install)..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: npm install a echoue" -ForegroundColor Red
        Read-Host "Appuyez sur Entree pour quitter"
        Exit 1
    }
    Write-Host "Dependances installees" -ForegroundColor Green
} else {
    Write-Host "Dependances deja installees" -ForegroundColor Green
}
Write-Host ""

# Afficher info
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "WEB URL   : http://localhost:$port" -ForegroundColor Cyan
Write-Host "API URL   : http://localhost:8000" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Demarrage du serveur Vite..." -ForegroundColor Yellow
Write-Host ""

# Démarrer le serveur
try {
    npm run dev
} finally {
    Write-Host "" 
    Write-Host "Nettoyage des caches Node..." -ForegroundColor Yellow

    # Nettoyer les caches de build
    $cacheDirs = @("dist", "dist-ssr", ".vite", "node_modules/.cache", "node_modules/.vite")
    foreach ($dirName in $cacheDirs) {
        $fullPath = Join-Path $PSScriptRoot $dirName
        if (Test-Path $fullPath) {
            Remove-Item -Recurse -Force $fullPath -ErrorAction SilentlyContinue
            Write-Host "Supprime : $dirName" -ForegroundColor DarkGray
        }
    }
    
    Write-Host "Nettoyage termine." -ForegroundColor Green
}
