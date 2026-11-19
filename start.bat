@echo off
title AgroAI Launcher
cd /d "C:\agrofield"

echo ============================================================
echo            Starting AgroAI (Frontend + Backend)
echo ============================================================
echo.

if not exist "C:\agrofield\backend\.venv\Scripts\uvicorn.exe" (
    echo [ERROR] Virtual environment not found at C:\agrofield\backend\.venv\Scripts\uvicorn.exe
    pause
    exit /b 1
)

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000...
start "AgroAI Backend (FastAPI)" cmd /k "cd /d C:\agrofield && C:\agrofield\backend\.venv\Scripts\uvicorn.exe backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting Frontend Server on http://localhost:8080...
start "AgroAI Frontend Server" cmd /k "cd /d C:\agrofield && powershell -ExecutionPolicy Bypass -File C:\agrofield\serve.ps1 -Port 8080"

echo.
echo Waiting for services to initialize...
timeout /t 3 /nobreak >nul

echo.
echo Opening AgroAI in your default browser...
start http://localhost:8080/

echo.
echo ============================================================
echo Services Started Successfully!
echo   - Frontend: http://localhost:8080/
echo   - Backend:  http://127.0.0.1:8000
echo   - API Docs: http://127.0.0.1:8000/docs
echo.
echo To shut down the services, simply close the respective terminal windows.
echo ============================================================
echo.
pause
