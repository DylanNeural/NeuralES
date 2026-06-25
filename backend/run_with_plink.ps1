# SSH Tunnel pour PostgreSQL via Plink (PuTTY)
# Connexion VPS OVH NeuralES
# Usage: .\run_with_plink.ps1

$SSHHost = "51.178.30.35"
$SSHUser = "debian"
$SSHPort = 22
$SSHPassword = "Azerty45"
$RemoteDB = "127.0.0.1:5432"
$LocalPort = 5433

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

# Tunnel SSH en background avec plink — PassThru pour pouvoir le fermer proprement
$plinkProcess = Start-Process -FilePath $plinkPath `
    -ArgumentList "-batch -pw $SSHPassword -hostkey `"SHA256:YRUcnGwEaESpnHnmouUadaesNrcfwN2SW1NZp/aXYUE`" -L ${LocalPort}:$RemoteDB -N $SSHUser@$SSHHost -P $SSHPort" `
    -WindowStyle Hidden -PassThru

Start-Sleep -Seconds 2

if ($plinkProcess.HasExited) {
    Write-Host "ERREUR: Impossible d'etablir le tunnel SSH!" -ForegroundColor Red
    Write-Host "Verifiez vos cles SSH et la connectivite vers $SSHHost." -ForegroundColor Yellow
    exit 1
}

Write-Host "SSH tunnel etabli (PID: $($plinkProcess.Id))`n" -ForegroundColor Green

# Lancer le backend
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "      Launching NeuralES Backend"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

# Création du venv si absent
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "Venv absent, creation en cours..." -ForegroundColor Yellow
    python -m venv venv
    if (-not $?) { Write-Host "ERREUR: python introuvable. Installez Python 3.11+." -ForegroundColor Red; exit 1 }
    Write-Host "Installation des dependances..." -ForegroundColor Yellow
    .\venv\Scripts\pip.exe install -r requirements.txt --quiet
    Write-Host "Venv pret.`n" -ForegroundColor Green
}

# Activation du venv
$env:VIRTUAL_ENV = "$PSScriptRoot\venv"
$env:PATH = "$PSScriptRoot\venv\Scripts;$env:PATH"

try {
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} finally {
    if ($plinkProcess -and !$plinkProcess.HasExited) {
        Write-Host "Fermeture du tunnel SSH (PID: $($plinkProcess.Id))..." -ForegroundColor Yellow
        Stop-Process -Id $plinkProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "Tunnel SSH ferme." -ForegroundColor Green
    }
}
