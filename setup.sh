#!/bin/bash
# LangTeam Setup Script for macOS/Linux
# Automates installation and configuration

set -e  # Exit on error

echo ""
echo "================================================================"
echo "  LangTeam - Automated Setup"
echo "================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "[1/6] Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    python3 --version
    echo -e "${GREEN}[OK]${NC} Python found"
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    python --version
    echo -e "${GREEN}[OK]${NC} Python found"
else
    echo -e "${RED}[ERROR]${NC} Python is not installed or not in PATH"
    echo "Please install Python 3.11+ from https://www.python.org/downloads/"
    exit 1
fi
echo ""

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info[1])')

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]; }; then
    echo -e "${YELLOW}[WARNING]${NC} Python $PYTHON_VERSION detected. Python 3.11+ recommended."
fi

# Check Ollama
echo "[2/6] Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    ollama --version
    echo -e "${GREEN}[OK]${NC} Ollama found"
else
    echo -e "${YELLOW}[WARNING]${NC} Ollama is not installed or not in PATH"
    echo "Please install from https://ollama.ai/download"
    echo ""
    read -p "Continue anyway? (y/n): " continue
    if [ "$continue" != "y" ] && [ "$continue" != "Y" ]; then
        exit 1
    fi
fi
echo ""

# Create virtual environment
echo "[3/6] Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}[SKIP]${NC} Virtual environment already exists"
else
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}[OK]${NC} Virtual environment created"
fi
echo ""

# Activate and install dependencies
echo "[4/6] Installing dependencies..."
source venv/bin/activate
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[OK]${NC} Dependencies installed"
else
    echo -e "${RED}[ERROR]${NC} Failed to install dependencies"
    exit 1
fi
echo ""

# Setup .env file
echo "[5/6] Setting up environment configuration..."
if [ -f ".env" ]; then
    echo -e "${YELLOW}[SKIP]${NC} .env file already exists"
else
    cp .env.example .env
    echo -e "${GREEN}[OK]${NC} Created .env from .env.example"
fi
echo ""

# Create sandbox directory
echo "[6/6] Creating sandbox directory..."
if [ -d "sandbox" ]; then
    echo -e "${YELLOW}[SKIP]${NC} Sandbox directory already exists"
else
    mkdir -p sandbox
    echo -e "${GREEN}[OK]${NC} Sandbox directory created"
fi
echo ""

# Check/pull Ollama model
echo "================================================================"
echo "  Optional: Ollama Model Setup"
echo "================================================================"
echo ""
if command -v ollama &> /dev/null; then
    echo "Current Ollama models:"
    ollama list
    echo ""
    read -p "Pull codellama:latest model now? (y/n): " pull_model
    if [ "$pull_model" = "y" ] || [ "$pull_model" = "Y" ]; then
        echo "Pulling codellama:latest... (this may take a few minutes)"
        ollama pull codellama:latest
        echo -e "${GREEN}[OK]${NC} Model pulled"
    else
        echo -e "${YELLOW}[SKIP]${NC} Model pull skipped"
    fi
else
    echo -e "${YELLOW}[SKIP]${NC} Ollama not available, skipping model setup"
fi
echo ""

# Run tests
echo "================================================================"
echo "  Optional: Run Tests"
echo "================================================================"
echo ""
read -p "Run boot tests to verify installation? (y/n): " run_tests
if [ "$run_tests" = "y" ] || [ "$run_tests" = "Y" ]; then
    echo "Running tests..."
    python tests/test_boot.py
    echo ""
fi

# Success message
echo ""
echo "================================================================"
echo "  Setup Complete!"
echo "================================================================"
echo ""
echo "Next steps:"
echo "  1. Make sure Ollama is running: ollama serve"
echo "  2. Activate virtual environment: source venv/bin/activate"
echo "  3. Run the team: python -m src.run_team \"Your project goal\""
echo ""
echo "Example:"
echo "  python -m src.run_team \"Build a REST API for a blog\""
echo ""
echo "Configuration:"
echo "  - Edit .env to change settings (model, limits, etc.)"
echo "  - Default: Ollama with codellama:latest"
echo "  - Memory: Enabled (learns from each session)"
echo ""
echo "Enjoy building with your AI agile team! 🚀"
echo ""
