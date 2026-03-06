@echo off
echo ========================================
echo   AI Media OS - Starting All Services
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/3] Starting Backend (FastAPI)...
cd backend
if not exist "app\core" (
    echo [ERROR] Backend core modules missing. Run setup first.
    pause
    exit /b 1
)
start "AI Media OS - Backend" cmd /k "python run.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Frontend (Next.js)...
cd ..
start "AI Media OS - Frontend" cmd /k "npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   All Services Started!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
echo Press any key to open browser...
pause >nul

start http://localhost:3000

echo.
echo Services are running in separate windows.
echo Close those windows to stop the services.
echo.
pause
