# Installation complète et démarrage du frontend NeuralES (Vue.js + Vite)

Write-Host "`n" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "      NeuralES WebApp - Setup Complet" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "`n"

# ETAPE 0: Vérifier et installer Node.js si nécessaire
Write-Host "[ETAPE 0/3] VERIFICATION DE NODE.JS" -ForegroundColor Red

$nodeExists = $null -ne (Get-Command node -ErrorAction SilentlyContinue)

if ($nodeExists) {
    try {
        $nodeVersion = node --version 2>&1
        $npmVersion = npm --version 2>&1
        Write-Host "      Node.js version: $nodeVersion" -ForegroundColor Green
        Write-Host "      npm version: $npmVersion" -ForegroundColor Green
        Write-Host "      ✓ Node.js trouvé" -ForegroundColor Green
    } catch {
        $nodeExists = $false
    }
}

if (-not $nodeExists) {
    Write-Host "      ⚠ Node.js n'est pas installé, installation en cours..." -ForegroundColor Yellow
    
    # Vérifier si winget est disponible
    $wingetExists = $null -ne (Get-Command winget -ErrorAction SilentlyContinue)
    
    if ($wingetExists) {
        Write-Host "      Utilisation de winget pour installer Node.js..." -ForegroundColor Cyan
        try {
            winget install --id OpenJS.NodeJS --accept-source-agreements --accept-package-agreements --silent
            Write-Host "      ✓ Node.js installé avec succès" -ForegroundColor Green
            
            # Rafraîchir le PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            
            Write-Host "      Vérification..." -ForegroundColor Cyan
            $nodeVersion = node --version 2>&1
            $npmVersion = npm --version 2>&1
            Write-Host "      Node.js version: $nodeVersion" -ForegroundColor Green
            Write-Host "      npm version: $npmVersion" -ForegroundColor Green
        } catch {
            Write-Host "      [ERROR] Erreur lors de l'installation via winget" -ForegroundColor Red
            Write-Host "      Relance ce script en tant qu'administrateur" -ForegroundColor Yellow
            Read-Host "Appuyez sur Entrée pour quitter"
            exit 1
        }
    } else {
        # Fallback: Télécharger et installer manuellement
        Write-Host "      winget non trouvé, téléchargement et installation de Node.js..." -ForegroundColor Cyan
        
        try {
            $tempDir = [System.IO.Path]::GetTempPath()
            $installerPath = Join-Path $tempDir "nodejs-installer.msi"
            $nodeUrl = "https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi"
            
            Write-Host "      Téléchargement de Node.js..." -ForegroundColor Cyan
            Invoke-WebRequest -Uri $nodeUrl -OutFile $installerPath -UseBasicParsing
            
            Write-Host "      Installation en cours..." -ForegroundColor Cyan
            Start-Process -FilePath $installerPath -ArgumentList "/quiet" -Wait
            
            # Nettoyer
            Remove-Item $installerPath -Force
            
            # Rafraîchir le PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            
            Write-Host "      ✓ Node.js installé avec succès" -ForegroundColor Green
            Write-Host "      Vérification..." -ForegroundColor Cyan
            $nodeVersion = node --version 2>&1
            $npmVersion = npm --version 2>&1
            Write-Host "      Node.js version: $nodeVersion" -ForegroundColor Green
            Write-Host "      npm version: $npmVersion" -ForegroundColor Green
        } catch {
            Write-Host "      [ERROR] Erreur lors de l'installation de Node.js" -ForegroundColor Red
            Write-Host "      Installe manuellement depuis: https://nodejs.org/" -ForegroundColor Yellow
            Read-Host "Appuyez sur Entrée pour quitter"
            exit 1
        }
    }
}

Write-Host "`n"

# ETAPE 1: Créer le fichier .env s'il n'existe pas
if (-not (Test-Path ".env")) {
    Write-Host "[ETAPE 1/3] CREATION DU FICHIER .env" -ForegroundColor Red
    
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env" -Force
        Write-Host "      ✓ Copie de .env.example vers .env" -ForegroundColor Green
    } else {
        Write-Host "      Création d'un fichier .env minimal..." -ForegroundColor Yellow
        @"
# Frontend Configuration
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=NeuralES
"@ | Set-Content ".env"
    }
    
    Write-Host "      ✓ Fichier .env créé" -ForegroundColor Green
    Write-Host "      Config: VITE_API_URL=http://localhost:8000" -ForegroundColor Cyan
    Write-Host "`n"
} else {
    Write-Host "[ETAPE 1/3] FICHIER .env DEJA PRESENT" -ForegroundColor Red
    Write-Host "      Configuration trouvée ✓" -ForegroundColor Green
}

Write-Host "`n"

# ETAPE 2: Installer les dépendances
Write-Host "[ETAPE 2/3] INSTALLATION DES DEPENDANCES" -ForegroundColor Red
Write-Host "      Fichier: package.json" -ForegroundColor Cyan
Write-Host "      Gestionnaire: npm" -ForegroundColor Cyan
Write-Host "      Installation en cours..." -ForegroundColor Cyan
Write-Host "`n"

npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Erreur lors de l'installation des dépendances" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Write-Host "`n"
Write-Host "      ✓ Toutes les dépendances installées" -ForegroundColor Green

Write-Host "`n"
Write-Host "==========================================" -ForegroundColor Green
Write-Host "      Setup terminé avec succès!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "`n"
Write-Host "[ETAPE 3/3] DEMARRAGE DU SERVEUR DE DEVELOPPEMENT" -ForegroundColor Red
Write-Host "`n"
Write-Host "Serveur disponible sur: http://localhost:5173" -ForegroundColor Cyan
Write-Host "`n"
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
Write-Host "`n"

npm run dev