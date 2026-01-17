@echo off
title Validator System Launcher
echo ===================================================
echo   Real-Time File Monitoring System - Launcher
echo ===================================================

echo [1/4] Starting API Server & Dashboard...
start "Validator API" cmd /k "uvicorn src.validator.api:app --reload"

echo Waiting 5 seconds for API to initialize...
timeout /t 5 >nul

echo [2/4] Generating Large Test Datasets (75 Columns)...
python src/validator/generate_test_data.py

echo [3/4] Starting File Watcher...
start "File Watcher" cmd /k "python watcher.py"

echo [4/4] Opening Dashboard...
start http://localhost:8000/dashboard

echo.
echo ===================================================
echo   System Running!
echo   - Drop files in 'input/' to validate
echo   - Check 'processed/' or 'rejected/' for results
echo ===================================================
pause
