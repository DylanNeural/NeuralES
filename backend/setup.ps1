# Installation et démarrage du backend NeuralES (PowerShell)

Write-Host "`n" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "      NeuralES Backend - Setup" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "`n"

$backendDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $backendDir

# Vérifier Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[✗] Python n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

# Créer venv si nécessaire
if (-not (Test-Path "venv")) {
    Write-Host "[1/3] Création du virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[✗] Erreur lors de la création du venv" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[1/3] Virtual environment trouvé" -ForegroundColor Green
}

# Activer venv
Write-Host "[2/3] Activation du virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Installer les dépendances
Write-Host "[3/3] Installation des dépendances..." -ForegroundColor Cyan
pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[✗] Erreur lors de l'installation des dépendances" -ForegroundColor Red
    exit 1
}

Write-Host "`n" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "      Setup terminé!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "`n"
Write-Host "Prochaines étapes:" -ForegroundColor Yellow
Write-Host "  1. Créer un fichier .env (copier depuis .env.example)" -ForegroundColor White
Write-Host "  2. Configurer la base de données PostgreSQL" -ForegroundColor White
Write-Host "  3. Lancer: python -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "`n"

# Proposer de lancer le serveur
$response = Read-Host "Voulez-vous lancer le serveur maintenant ? (O/N)"
if ($response -eq "O" -or $response -eq "o") {
    Write-Host "`nDémarrage du serveur..." -ForegroundColor Cyan
    Write-Host "Accédez à http://localhost:8000/docs pour la documentation API`n" -ForegroundColor Green
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} else {
    Write-Host "Pour lancer le serveur: python -m uvicorn app.main:app --reload`n" -ForegroundColor Green
}
