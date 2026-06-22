# EMBEDHUNT AI — apply database migrations.
# Usage:  ./scripts/migrate.ps1            (upgrade to head)
#         ./scripts/migrate.ps1 revision   (autogenerate a new revision)
param(
    [ValidateSet("upgrade", "revision", "downgrade", "history")]
    [string]$Action = "upgrade",
    [string]$Message = "auto"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$py   = Join-Path $root ".venv/Scripts/python.exe"

Push-Location (Join-Path $root "backend")
try {
    switch ($Action) {
        "upgrade"   { & $py -m alembic upgrade head }
        "downgrade" { & $py -m alembic downgrade -1 }
        "history"   { & $py -m alembic history }
        "revision"  { & $py -m alembic revision --autogenerate -m $Message }
    }
}
finally {
    Pop-Location
}
