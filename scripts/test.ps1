# EMBEDHUNT AI — run the test suite with coverage.
# Usage:  ./scripts/test.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$py   = Join-Path $root ".venv/Scripts/python.exe"

Push-Location (Join-Path $root "backend")
try {
    & $py -m pytest --cov=app --cov-report=term-missing -p no:cacheprovider
}
finally {
    Pop-Location
}
