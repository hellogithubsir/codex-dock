$ErrorActionPreference = "Stop"

$SourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SourceDir

Write-Host "Installing the codex-dock shell command into your PowerShell profile."

if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 -c "from scripts.main import install; install()"
    exit $LASTEXITCODE
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    python -c "from scripts.main import install; install()"
    exit $LASTEXITCODE
}

Write-Error "Python 3.10+ was not found in PATH."
