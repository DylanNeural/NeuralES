$pg = 'C:\Program Files\PostgreSQL\18\bin'
if (Test-Path $pg) {
    $env:Path = $pg + ';' + $env:Path
    Write-Host "Added $pg to PATH for this session"
} else {
    Write-Host "PostgreSQL bin not found: $pg"
    exit 1
}

Set-Location -Path $PSScriptRoot

if (-Not (Test-Path '.\\venv\\Scripts\\Activate.ps1')) {
    Write-Host 'venv missing -> creating venv'
    python -m venv venv
}

Write-Host 'Activating venv'
& .\\venv\\Scripts\\Activate.ps1

Write-Host 'Upgrading pip/setuptools/wheel'
python -m pip install --upgrade pip setuptools wheel

Write-Host 'Attempting to install psycopg2-binary (binary wheel preferred)'
python -m pip install --only-binary :all: psycopg2-binary
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Binary wheel install failed, trying source wheel (fallback)'
    python -m pip install psycopg2-binary
}

Write-Host 'Installing remaining dependencies from requirements.txt'
python -m pip install -r requirements.txt
