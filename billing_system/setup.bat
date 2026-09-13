@echo off
REM Wi-Fi Billing System - Windows Setup Script

echo.
echo ================================
echo Wi-Fi Billing System Setup
echo ================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python is installed
echo.

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo [OK] .env file created
    echo Please update .env with your database credentials
) else (
    echo [OK] .env file already exists
)

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next steps:
echo 1. Update .env with your MySQL credentials
echo 2. Create the database:
echo    - Open MySQL command line or workbench
echo    - Run: source billing_system/models.sql
echo 3. Start the Flask backend:
echo    python app.py
echo 4. In another terminal, start Streamlit dashboard:
echo    streamlit run dashboard.py
echo.
echo Access the application at: http://localhost:5000
echo Access the dashboard at: http://localhost:8501
echo.
pause
