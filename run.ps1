# Run db.py using the venv interpreter regardless of PATH
$scriptPath = Join-Path $PSScriptRoot "db.py"
$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "Virtual environment not found: $pythonExe"
    Write-Host "Create it with: python -m venv .venv"
    exit 1
}

& $pythonExe $scriptPath
