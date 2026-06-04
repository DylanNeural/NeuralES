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

# Démarrer le tunnel SSH vers PostgreSQL
Write-Host "Ouverture du tunnel SSH vers PostgreSQL..." -ForegroundColor Yellow
$sshProcess = Start-Process -FilePath "ssh" -ArgumentList "-o StrictHostKeyChecking=no", "-o ConnectTimeout=10", "-L", "5433:127.0.0.1:5432", "debian@51.178.30.35", "-N" -PassThru -WindowStyle Hidden

# Attendre jusqu'à 15s que le port 5433 réponde vraiment
$tunnelOk = $false
for ($i = 1; $i -le 15; $i++) {
    Start-Sleep -Seconds 1
    if ($sshProcess.HasExited) {
        break
    }
    $test = (Test-NetConnection -ComputerName 127.0.0.1 -Port 5433 -WarningAction SilentlyContinue).TcpTestSucceeded
    if ($test) {
        $tunnelOk = $true
        break
    }
    Write-Host "  Attente tunnel SSH... ($i/15)" -ForegroundColor DarkGray
}

if ($tunnelOk) {
    Write-Host "Tunnel SSH etabli et operationnel (PID: $($sshProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "ERREUR: Tunnel SSH non operationnel apres 15s." -ForegroundColor Red
    Write-Host "  - Verifiez que le VPS est demarre (panel OVH)" -ForegroundColor Yellow
    Write-Host "  - Verifiez vos cles SSH" -ForegroundColor Yellow
    if ($sshProcess -and !$sshProcess.HasExited) {
        Stop-Process -Id $sshProcess.Id -Force -ErrorAction SilentlyContinue
    }
    exit 1
}
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
	# Fermer le tunnel SSH
	if ($sshProcess -and !$sshProcess.HasExited) {
		Write-Host "Fermeture du tunnel SSH..." -ForegroundColor Yellow
		Stop-Process -Id $sshProcess.Id -Force -ErrorAction SilentlyContinue
		Write-Host "Tunnel SSH ferme." -ForegroundColor Green
	}
	
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
