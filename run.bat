@echo off
setlocal

REM Launch backend (directly run PowerShell script to avoid double windows)
start "NeuralES Backend" powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0backend\run.ps1"

REM Launch web (directly run PowerShell script to avoid double windows)
start "NeuralES Web" powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0neurales-web\run.ps1"

endlocal
