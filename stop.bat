@echo off
echo ========================================
echo   AI Media OS - Stopping All Services
echo ========================================
echo.

echo Stopping Backend (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a >nul 2>&1

echo Stopping Frontend (port 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /F /PID %%a >nul 2>&1

echo.
echo All services stopped.
echo.
pause
