#!/bin/bash

echo "🚀 Setting up Coffee Agent development environment..."

# Check if Python 3.11+ is available
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ Python 3.10+ is not installed. Please install Python 3.10+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "🐍 Python version: $PYTHON_VERSION"

# Verify minimum version
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo "✅ Python version is compatible"
else
    echo "❌ Python 3.10+ is required for ScaleKit integration"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete! To start development:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the app: python run.py"
echo "3. Open browser: http://localhost:8000"
echo ""
echo "🔑 Don't forget to create a .env file with your OPENAI_API_KEY!"
echo ""
echo "To deactivate the virtual environment later, run: deactivate"
