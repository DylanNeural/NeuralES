# SSH Tunnel pour PostgreSQL via Plink (PuTTY)
# Connexion VPS OVH NeuralES
# Usage: .\run_with_plink.ps1

$SSHHost = "51.178.30.35"
$SSHUser = "debian"
$SSHPort = 22
$SSHPassword = "SaleNoir1"
$RemoteDB = "127.0.0.1:5432"
$LocalPort = 5432

Write-Host "========================================" -ForegroundColor Green
Write-Host "   SSH Tunnel - NeuralES PostgreSQL"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "SSH Server : $SSHHost (OVH VPS)"
Write-Host "SSH User   : $SSHUser"
Write-Host "Local Port : $LocalPort"
Write-Host "Remote DB  : $RemoteDB"
Write-Host ""
Write-Host "Database config:"
Write-Host "  User: neurales_user"
Write-Host "  Pass: jp8GJIrdC7L7S55N"
Write-Host "  DB  : neurales"
Write-Host ""

# Verification de plink
$plinkPath = "C:\Program Files\PuTTY\plink.exe"
if (-not (Test-Path $plinkPath)) {
    Write-Host "ERROR: plink.exe not found at $plinkPath" -ForegroundColor Red
    Write-Host "Install PuTTY or adjust the path" -ForegroundColor Red
    exit 1
}

Write-Host "Launching SSH tunnel in background..." -ForegroundColor Yellow

# Tunnel SSH en background avec plink
Start-Process -FilePath $plinkPath -ArgumentList "-batch -pw $SSHPassword -L $LocalPort`:$RemoteDB -N $SSHUser@$SSHHost -P $SSHPort" -WindowStyle Hidden

# Attendre un peu que le tunnel soit etabli
Start-Sleep -Seconds 2

Write-Host "SSH tunnel established in background`n" -ForegroundColor Green

# Lancer le backend
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "      Launching NeuralES Backend"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activer venv et lancer le serveur
Set-Location $PSScriptRoot
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
