@echo off
cd /d "C:\Users\Dylan\Desktop\Side\NeuralES\backend"

echo ========================================
echo Running Migration...
echo ========================================
python run_migration_v2.py
echo Migration exit code: %ERRORLEVEL%

echo.
echo ========================================
echo Running Seed Database...
echo ========================================
python seed_db.py --reset
echo Seed exit code: %ERRORLEVEL%

echo.
echo ========================================
echo Done!
echo ========================================
pause
