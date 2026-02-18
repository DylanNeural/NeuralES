@echo off
setlocal

REM Vérifier que le setup a été fait
if not exist "backend\venv\Scripts\python.exe" (
    echo.
    echo ==========================================
    echo   NeuralES Setup Required
    echo ==========================================
    echo.
    echo First launch detected. Running setup...
    echo.
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
    if errorlevel 1 (
        echo Setup failed. Please check the errors above.
        pause
        exit /b 1
    )
    echo.
    echo Setup complete! Starting NeuralES...
    echo.
)

REM Launch backend
start "NeuralES Backend" powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0backend\run_with_plink.ps1"

REM Launch web
start "NeuralES Web" powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0neurales-web\run.ps1"

endlocal
