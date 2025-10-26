@echo off
REM LangTeam Setup Script for Windows
REM Automates installation and configuration

echo.
echo ================================================================
echo   LangTeam - Automated Setup
echo ================================================================
echo.

REM Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo [OK] Python found
echo.

REM Check Ollama
echo [2/6] Checking Ollama installation...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama is not installed or not in PATH
    echo Please install from https://ollama.ai/download
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
) else (
    ollama --version
    echo [OK] Ollama found
)
echo.

REM Create virtual environment
echo [3/6] Creating virtual environment...
if exist venv (
    echo [SKIP] Virtual environment already exists
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)
echo.

REM Activate and install dependencies
echo [4/6] Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Setup .env file
echo [5/6] Setting up environment configuration...
if exist .env (
    echo [SKIP] .env file already exists
) else (
    copy .env.example .env >nul
    echo [OK] Created .env from .env.example
)
echo.

REM Create sandbox directory
echo [6/6] Creating sandbox directory...
if exist sandbox (
    echo [SKIP] Sandbox directory already exists
) else (
    mkdir sandbox
    echo [OK] Sandbox directory created
)
echo.

REM Check/pull Ollama model
echo ================================================================
echo   Optional: Ollama Model Setup
echo ================================================================
echo.
ollama list >nul 2>&1
if not errorlevel 1 (
    echo Current Ollama models:
    ollama list
    echo.
    set /p pull_model="Pull codellama:latest model now? (y/n): "
    if /i "%pull_model%"=="y" (
        echo Pulling codellama:latest... (this may take a few minutes)
        ollama pull codellama:latest
        echo [OK] Model pulled
    ) else (
        echo [SKIP] Model pull skipped
    )
) else (
    echo [SKIP] Ollama not available, skipping model setup
)
echo.

REM Run tests
echo ================================================================
echo   Optional: Run Tests
echo ================================================================
echo.
set /p run_tests="Run boot tests to verify installation? (y/n): "
if /i "%run_tests%"=="y" (
    echo Running tests...
    python tests\test_boot.py
    echo.
)

REM Success message
echo.
echo ================================================================
echo   Setup Complete!
echo ================================================================
echo.
echo Next steps:
echo   1. Make sure Ollama is running: ollama serve
echo   2. Activate virtual environment: venv\Scripts\activate
echo   3. Run the team: python -m src.run_team "Your project goal"
echo.
echo Example:
echo   python -m src.run_team "Build a REST API for a blog"
echo.
echo Configuration:
echo   - Edit .env to change settings (model, limits, etc.)
echo   - Default: Ollama with codellama:latest
echo   - Memory: Enabled (learns from each session)
echo.
echo Enjoy building with your AI agile team! 🚀
echo.

pause
