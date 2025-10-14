#!/bin/bash
# TodoApp - Unix/Mac Startup Script
# =====================================

echo "🚀 Starting TodoApp..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python is not installed"
        echo "Please install Python from https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "❌ Backend directory not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo "❌ Frontend directory not found"
    echo "Please run this script from the project root directory"  
    exit 1
fi

echo "✅ Python found, starting application..."
echo

# Make script executable if needed
chmod +x "$0"

# Run the Python startup script
$PYTHON_CMD run.py
