@echo off
REM TodoApp - Windows Startup Script
REM ======================================

echo 🚀 Starting TodoApp...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "backend" (
    echo ❌ Backend directory not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ Frontend directory not found  
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo ✅ Python found, starting application...
echo.

REM Run the Python startup script
python run.py

pause
