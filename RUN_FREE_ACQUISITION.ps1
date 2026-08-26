$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path $python)) { throw 'Python virtual environment not found. Create .venv first.' }
& $python scripts/global/data_acquisition_worker.py --config config/data_acquisition_local.json
