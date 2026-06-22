# EMBEDHUNT AI — one-shot local dev setup.
# Usage:  ./scripts/setup.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $root ".venv"
$py   = Join-Path $venv "Scripts/python.exe"

Write-Host "EMBEDHUNT AI — dev setup" -ForegroundColor Cyan

if (-not (Test-Path $py)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venv
}

Write-Host "Installing dependencies..." -ForegroundColor Yellow
& $py -m pip install --upgrade pip setuptools wheel
& $py -m pip install -r (Join-Path $root "backend/requirements/test.txt")

$envFile = Join-Path $root "backend/.env"
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $root "backend/.env.example") $envFile
    Write-Host "Created backend/.env from template — edit it with your secrets." -ForegroundColor Green
}

Write-Host "Setup complete. Start the API with: ./scripts/run.ps1" -ForegroundColor Green
