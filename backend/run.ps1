#!/usr/bin/env pwsh
# Démarrer le serveur NeuralES Backend

Set-Location -Path $PSScriptRoot

# Ajouter PostgreSQL bin au PATH pour cette session
$env:Path = 'C:\Program Files\PostgreSQL\18\bin;' + $env:Path

# Activer venv
& ".\venv\Scripts\Activate.ps1"

# Afficher info
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "      NeuralES Backend - Startup" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "API URL   : http://localhost:8000" -ForegroundColor Cyan
Write-Host "DOCS      : http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "REDOC     : http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "Demarrage du serveur Uvicorn..." -ForegroundColor Yellow
Write-Host ""

# Démarrer le serveur
$repoRoot = Resolve-Path "$PSScriptRoot\.."
try {
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} finally {
	Write-Host "" 
	Write-Host "Nettoyage des caches Python..." -ForegroundColor Yellow

	$cacheDirs = @("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache")
	foreach ($dirName in $cacheDirs) {
		Get-ChildItem -Path $repoRoot -Recurse -Force -Directory -Filter $dirName -ErrorAction SilentlyContinue |
			Where-Object { $_.FullName -notmatch '\\venv\\|\\\.venv\\|\\node_modules\\' } |
			Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
	}

    Get-ChildItem -Path $repoRoot -Recurse -Force -File -Include "*.pyc", "*.pyo", "*.pyd" -ErrorAction SilentlyContinue |
		Where-Object { $_.FullName -notmatch '\\venv\\|\\\.venv\\|\\node_modules\\' } |
        Remove-Item -Force -ErrorAction SilentlyContinue

    Remove-Item -Path (Join-Path $repoRoot ".coverage") -Force -ErrorAction SilentlyContinue
    
    Write-Host "Nettoyage termine." -ForegroundColor Green
}
