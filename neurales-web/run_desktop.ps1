#!/usr/bin/env pwsh
# Démarrer NeuralES en mode desktop (Tauri)

Set-Location -Path $PSScriptRoot

# Ensure Cargo is available for Tauri in shells opened before Rust install.
$cargoBin = Join-Path $env:USERPROFILE '.cargo\bin'
if (Test-Path $cargoBin) {
    $env:Path = "$cargoBin;$env:Path"
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "     NeuralES Desktop (Tauri) - Dev" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

if (-not (Test-Path "node_modules")) {
    Write-Host "Installation des dependances npm..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: npm install a echoue" -ForegroundColor Red
        Exit 1
    }
}

Write-Host "Lancement desktop..." -ForegroundColor Cyan
npm run desktop:dev
