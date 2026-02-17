#!/usr/bin/env pwsh
# Démarrer l'application NeuralES Desktop

Set-Location -Path $PSScriptRoot

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "      NeuralES Desktop - Startup" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Vérifier Python
Write-Host "[1/3] Verification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Python n'est pas installe ou pas dans le PATH" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour quitter"
    Exit 1
}
Write-Host ""

# Créer venv si nécessaire
Write-Host "[2/3] Configuration de l'environnement..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "Creation du virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: Impossible de creer le venv" -ForegroundColor Red
        Read-Host "Appuyez sur Entree pour quitter"
        Exit 1
    }
    Write-Host "Virtual environment cree" -ForegroundColor Green
} else {
    Write-Host "Virtual environment existe deja" -ForegroundColor Green
}

# Activer venv
& ".\venv\Scripts\Activate.ps1"

# Installer les dépendances si nécessaire
Write-Host "[3/3] Verification des dependances..." -ForegroundColor Yellow
$requirementsPath = Join-Path $PSScriptRoot "app\requirements.txt"
if (Test-Path $requirementsPath) {
    # Vérifier si les dépendances sont déjà installées (heuristique simple)
    $installedPackages = pip list --format=freeze 2>$null
    $requirementsContent = Get-Content $requirementsPath -Raw
    
    # Si pip list échoue ou est vide, installer
    if (-not $installedPackages -or $installedPackages.Count -lt 3) {
        Write-Host "Installation des dependances..." -ForegroundColor Cyan
        pip install -q -r $requirementsPath
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERREUR: Installation des dependances a echoue" -ForegroundColor Red
            Read-Host "Appuyez sur Entree pour quitter"
            Exit 1
        }
        Write-Host "Dependances installees" -ForegroundColor Green
    } else {
        Write-Host "Dependances deja installees" -ForegroundColor Green
    }
} else {
    Write-Host "Pas de requirements.txt trouve" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Demarrage de l'application..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Démarrer l'application
$repoRoot = Resolve-Path "$PSScriptRoot\.."
try {
    python app\main.py
} finally {
    Write-Host "" 
    Write-Host "Nettoyage des caches Python..." -ForegroundColor Yellow

    $cacheDirs = @("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache")
    foreach ($dirName in $cacheDirs) {
        Get-ChildItem -Path $PSScriptRoot -Recurse -Force -Directory -Filter $dirName -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch '\\venv\\|\\\.venv\\' } |
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    }

    Get-ChildItem -Path $PSScriptRoot -Recurse -Force -File -Include "*.pyc", "*.pyo", "*.pyd" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '\\venv\\|\\\.venv\\' } |
        Remove-Item -Force -ErrorAction SilentlyContinue
    
    Write-Host "Nettoyage termine." -ForegroundColor Green
}
