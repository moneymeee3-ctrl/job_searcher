# EMBEDHUNT AI — run the API locally (reload mode).
# Usage:  ./scripts/run.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$py   = Join-Path $root ".venv/Scripts/python.exe"

Push-Location (Join-Path $root "backend")
try {
    & $py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}
finally {
    Pop-Location
}
