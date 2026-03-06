Write-Host "======================================="
Write-Host "HiveMind Integration Test Runner"
Write-Host "======================================="

$ErrorActionPreference = "Stop"

Write-Host "Moving to backend directory..."
cd backend

# -----------------------------
# Locate Python 3.11
# -----------------------------
Write-Host "Searching for Python 3.11..."

$python311 = py -3.11 -c "import sys; print(sys.executable)" 2>$null

if (!$python311) {
    Write-Host "ERROR: Python 3.11 not found."
    Write-Host "Install Python 3.11.9 from:"
    Write-Host "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    exit 1
}

Write-Host "Python 3.11 found at:"
Write-Host $python311

# -----------------------------
# Create virtual environment
# -----------------------------
Write-Host "Creating virtual environment with Python 3.11..."

if (!(Test-Path "venv")) {
    & $python311 -m venv venv
}

# -----------------------------
# Activate environment
# -----------------------------
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# -----------------------------
# Confirm correct Python version
# -----------------------------
Write-Host "Verifying Python version..."
python --version

# -----------------------------
# Upgrade pip
# -----------------------------
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# -----------------------------
# Install dependencies
# -----------------------------
Write-Host "Installing project dependencies..."
pip install -r requirements.txt

# -----------------------------
# Install test tools
# -----------------------------
Write-Host "Installing testing tools..."
pip install pytest pytest-asyncio pytest-cov httpx aiosqlite redis pytest-xdist

# -----------------------------
# Set PYTHONPATH
# -----------------------------
Write-Host "Setting PYTHONPATH..."
$env:PYTHONPATH = (Get-Location)

# -----------------------------
# Run tests
# -----------------------------
Write-Host "Running all tests..."
pytest -v

Write-Host "Running coverage tests..."
pytest --cov=app --cov-report=html

Write-Host "Running integration tests..."
pytest -m integration -v

Write-Host "Running cross-module tests..."
pytest tests/test_cross_module_learning.py -v

Write-Host "Running vector tests..."
pytest -m vector -v

Write-Host "Running parallel tests..."
pytest -n auto

Write-Host "======================================="
Write-Host "All tests completed successfully"
Write-Host "Coverage report available at:"
Write-Host "backend/htmlcov/index.html"
Write-Host "======================================="