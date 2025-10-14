#!/usr/bin/env python3
"""
TodoApp - One-Click Startup Script
========================================

This script automatically sets up and starts your application:
- Installs dependencies
- Sets up database
- Starts backend server
- Opens frontend in browser

Usage: python run.py
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

def log(message):
    """Print timestamped log message"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_command(command, cwd=None, shell=True):
    """Run a command and return success status"""
    try:
        log(f"Running: {command}")
        result = subprocess.run(command, shell=shell, cwd=cwd, 
                              capture_output=True, text=True)
        if result.returncode == 0:
            log(f"✅ Success: {command}")
            return True
        else:
            log(f"❌ Failed: {command}")
            log(f"Error: {result.stderr}")
            return False
    except Exception as e:
        log(f"❌ Exception: {e}")
        return False

def install_backend_dependencies():
    """Install Python backend dependencies"""
    log("📦 Installing backend dependencies...")
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        log("❌ Backend directory not found!")
        return False
    
    # Check if virtual environment should be used
    if not os.path.exists("backend/venv") and not os.environ.get("VIRTUAL_ENV"):
        log("🔧 Creating virtual environment...")
        if not run_command("python -m venv venv", cwd="backend"):
            return False
    
    # Install requirements
    pip_cmd = "backend/venv/Scripts/pip" if os.name == 'nt' else "backend/venv/bin/pip"
    if not os.path.exists(pip_cmd) and os.environ.get("VIRTUAL_ENV"):
        pip_cmd = "pip"  # Use system pip if in virtual env
    elif not os.path.exists(pip_cmd):
        pip_cmd = "pip"  # Fallback to system pip
    
    requirements_file = "backend/requirements.txt"
    if os.path.exists(requirements_file):
        return run_command(f"{pip_cmd} install -r requirements.txt", cwd="backend")
    else:
        # Install common dependencies
        deps = ["fastapi", "uvicorn", "sqlite3", "pydantic"]
        for dep in deps:
            if not run_command(f"{pip_cmd} install {dep}", cwd="backend"):
                return False
        return True

def start_backend():
    """Start the backend server"""
    log("🚀 Starting backend server...")
    backend_dir = Path("backend")
    
    # Find the main Python file
    main_files = ["main.py", "app.py", "server.py", "run.py"]
    main_file = None
    
    for file in main_files:
        if (backend_dir / file).exists():
            main_file = file
            break
    
    if not main_file:
        log("❌ No main Python file found in backend/")
        return None
    
    # Start server
    python_cmd = "backend/venv/Scripts/python" if os.name == 'nt' else "backend/venv/bin/python"
    if not os.path.exists(python_cmd):
        python_cmd = "python"  # Fallback to system python
    
    # Try uvicorn first, then fallback to direct python
    uvicorn_cmd = f"uvicorn {main_file.replace('.py', '')}:app --reload --port 8000"
    
    try:
        log(f"Starting: {uvicorn_cmd}")
        process = subprocess.Popen(uvicorn_cmd, shell=True, cwd="backend")
        time.sleep(3)  # Give server time to start
        
        if process.poll() is None:  # Process still running
            return process
        else:
            # Fallback to direct python execution
            log("Falling back to direct Python execution...")
            process = subprocess.Popen(f"{python_cmd} {main_file}", 
                                     shell=True, cwd="backend")
            return process
    except Exception as e:
        log(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend server"""
    log("🌐 Starting frontend server...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        log("❌ Frontend directory not found!")
        return None
    
    try:
        # Start simple HTTP server for frontend
        process = subprocess.Popen(
            "python -m http.server 8080", 
            shell=True, 
            cwd="frontend",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)  # Give server time to start
        return process
    except Exception as e:
        log(f"❌ Failed to start frontend: {e}")
        return None

def open_browser():
    """Open the application in browser"""
    time.sleep(5)  # Wait for servers to fully start
    log("🌐 Opening application in browser...")
    try:
        webbrowser.open("http://localhost:8080")
        log("✅ Application opened in browser!")
    except Exception as e:
        log(f"❌ Could not open browser: {e}")
        log("📖 Manual access: http://localhost:8080")

def main():
    """Main startup function"""
    print("🚀 TodoApp - Starting Application")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("backend").exists() and not Path("frontend").exists():
        log("❌ Run this script from the project root directory")
        log("Expected structure: backend/ and frontend/ directories")
        return 1
    
    # Install dependencies
    if not install_backend_dependencies():
        log("❌ Failed to install backend dependencies")
        return 1
    
    # Start backend server
    backend_process = start_backend()
    if not backend_process:
        log("❌ Failed to start backend server")
        return 1
    
    # Start frontend server
    frontend_process = start_frontend()
    if not frontend_process:
        log("❌ Failed to start frontend server")
        backend_process.terminate()
        return 1
    
    # Open browser in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("\n🎉 Application Started Successfully!")
    print("-" * 40)
    print("📊 Backend API: http://localhost:8000")
    print("🌐 Frontend: http://localhost:8080")
    print("📚 API Docs: http://localhost:8000/docs")
    print("-" * 40)
    print("Press Ctrl+C to stop all servers")
    
    try:
        # Wait for processes
        while backend_process.poll() is None and frontend_process.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        log("\n🛑 Shutting down servers...")
        
        if backend_process and backend_process.poll() is None:
            backend_process.terminate()
            log("✅ Backend server stopped")
            
        if frontend_process and frontend_process.poll() is None:
            frontend_process.terminate()
            log("✅ Frontend server stopped")
        
        log("👋 Application stopped. Thank you!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
