@echo off
setlocal
cd /d "%~dp0"

python -m src.main
if errorlevel 1 (
    echo.
    echo Das Dashboard konnte nicht gestartet werden.
    echo Pruefen Sie, ob Python installiert und im PATH verfuegbar ist.
    pause
)
