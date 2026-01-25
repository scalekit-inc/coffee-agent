@echo off
echo 🚀 Setting up Coffee Agent development environment...

REM Check if Python 3 is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is not installed. Please install Python 3.11+ first.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 🐍 Python version: %PYTHON_VERSION%

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing dependencies...
pip install -r requirements.txt

echo.
echo ✅ Setup complete! To start development:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Run the app: python run.py
echo 3. Open browser: http://localhost:8000
echo.
echo 🔑 Don't forget to create a .env file with your OPENAI_API_KEY!
echo.
echo To deactivate the virtual environment later, run: deactivate
pause
