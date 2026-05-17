@echo off
:: ============================================================
:: JobBot Windows Setup Script
:: Run once: setup.bat
:: ============================================================
echo.
echo  ========================================
echo   JobBot — Setup
echo  ========================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+ from python.org
    pause
    exit /b 1
)
echo [OK] Python found.

:: 2. Create virtual environment
if not exist "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)

:: 3. Activate and install dependencies
echo [INFO] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
echo [OK] Dependencies installed.

:: 4. Install Playwright browsers
echo [INFO] Installing Playwright browser...
playwright install chromium
echo [OK] Chromium installed.

:: 5. Create .env if missing
if not exist ".env" (
    copy .env.example .env
    echo [IMPORTANT] .env file created — please add your OPENAI_API_KEY and Gmail credentials!
) else (
    echo [OK] .env file already exists.
)

:: 6. Create data dirs
if not exist "data\cvs\" mkdir data\cvs
if not exist "data\certificates\" mkdir data\certificates
if not exist "logs\" mkdir logs
echo [OK] Directories created.

echo.
echo  ========================================
echo   Setup complete!
echo  ========================================
echo.
echo  Next steps:
echo    1. Open .env and enter your API keys
echo    2. Copy your CV to: data\cvs\my_cv.pdf
echo    3. Edit config\profile.py with your personal data
echo    4. Start JobBot: python run.py
echo.
pause