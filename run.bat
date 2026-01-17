@echo off
echo ===================================================
echo   Real-Time File Monitoring System - Launcher
echo ===================================================

echo [1/3] Starting API Server & Dashboard...
start "Validator API" cmd /k "uvicorn src.validator.api:app --reload"

echo Waiting for server to initialize...
timeout /t 5 /nobreak >nul

echo [2/3] Opening Dashboard...
start http://localhost:8000/dashboard

echo [3/3] Running Financial Stress Test Simulation...
start "Simulation" cmd /k "python stress_test.py"

echo.
echo ===================================================
echo   System Running!
echo   - Check the Dashboard API window for backend logs
echo   - Check the Simulation window for test progress
echo   - Watch the Dashboard in your browser
echo ===================================================
pause
