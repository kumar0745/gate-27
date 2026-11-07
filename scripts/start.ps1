$ErrorActionPreference = 'Stop'
$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

$Python = Get-Command py -ErrorAction SilentlyContinue
if (-not $Python) {
    throw 'Python 3.11 or newer is required. Install Python and try again.'
}
py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 or newer is required.' }

if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3 -m venv .venv
}

$VenvPython = Join-Path $RootDir '.venv\Scripts\python.exe'
& $VenvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }

if (-not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
    Write-Host 'Created .env from .env.example. Review its settings before production use.'
}

$HostAddress = if ($env:GATEPATH_HOST) { $env:GATEPATH_HOST } else { '127.0.0.1' }
$Port = if ($env:GATEPATH_PORT) { $env:GATEPATH_PORT } else { '8000' }
& $VenvPython -m uvicorn app.main:app --app-dir backend --host $HostAddress --port $Port
