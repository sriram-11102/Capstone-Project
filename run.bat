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

echo [LAUNCHER] Starting File Watcher (Monitor)...
start "File Watcher" cmd /k "python watcher.py"

echo [SUCCESS] System is live!
echo - API/Dashboard: http://localhost:8000/dashboard
echo - Input Folder : input/
echo.
pause
