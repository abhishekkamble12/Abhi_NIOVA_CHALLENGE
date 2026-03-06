@echo off
echo ========================================
echo   AI Media OS - First Time Setup
echo ========================================
echo.

echo [1/2] Setting up Backend...
cd backend
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
echo Installing dependencies...
pip install -q fastapi uvicorn sqlalchemy aiosqlite pydantic-settings python-dotenv
echo Backend setup complete!

echo.
echo [2/2] Setting up Frontend...
cd ..
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)
echo Frontend setup complete!

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Run start.bat to launch the application
echo.
pause
