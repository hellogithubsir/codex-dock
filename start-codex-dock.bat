@echo off
setlocal
cd /d %~dp0

echo Starting codex-dock. Use --cli to open the terminal menu instead of the Web panel.

py -3 -c "import sys" >nul 2>nul
if %errorlevel%==0 (
py -3 -m scripts %*
  exit /b %errorlevel%
)

python -c "import sys" >nul 2>nul
if %errorlevel%==0 (
python -m scripts %*
  exit /b %errorlevel%
)

echo Python 3.10+ was not found in PATH.
exit /b 1
