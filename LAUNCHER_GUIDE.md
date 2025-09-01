# Service Launcher Guide

This document explains how to use the various launcher scripts to start the complete FastAPI User Management System.

## Overview

The project now includes multiple launcher options to start both the backend API service and GUI application together:

1. **`launcher.py`** - Main Python launcher (cross-platform)
2. **`start_service.bat`** - Windows batch file launcher
3. **`start_service.ps1`** - PowerShell launcher (Windows)

## Quick Start

### Option 1: Python Launcher (Recommended)
```bash
# Start both backend and GUI with default settings
python launcher.py

# Custom port
python launcher.py --port 8080

# Backend only (no GUI)
python launcher.py --no-gui

# Custom host and longer GUI delay
python launcher.py --host 0.0.0.0 --gui-delay 5
```

### Option 2: Windows Batch File
```cmd
# Double-click start_service.bat or run from command prompt
start_service.bat

# With custom arguments (passed to launcher.py)
start_service.bat --port 8080
```

### Option 3: PowerShell (Windows)
```powershell
# Start with default settings
.\start_service.ps1

# Custom configuration
.\start_service.ps1 -Port 8080 -Host "0.0.0.0"

# Backend only
.\start_service.ps1 -NoGui

# Show help
.\start_service.ps1 -Help
```

## Features

### Main Python Launcher (`launcher.py`)

**Features:**
- Automatically starts FastAPI backend with uvicorn
- Waits for backend to be ready before starting GUI
- Proper process management and cleanup
- Graceful shutdown handling (Ctrl+C)
- Health checks and error handling
- Cross-platform compatibility

**Command Line Options:**
- `--host HOST` - Backend host address (default: 127.0.0.1)
- `--port PORT` - Backend port number (default: 8000)
- `--gui-delay SECONDS` - Delay before starting GUI (default: 3)
- `--no-gui` - Start only backend service
- `--help` - Show help message

**What It Does:**
1. Validates all dependencies are installed
2. Starts FastAPI backend with uvicorn
3. Waits for backend health check to pass
4. Starts GUI application after specified delay
5. Monitors both processes
6. Handles graceful shutdown when GUI is closed

### Windows Batch Launcher (`start_service.bat`)

**Features:**
- Simple double-click execution
- Automatic virtual environment activation
- Dependency validation
- Error handling with user prompts

**Usage:**
- Double-click the file in Windows Explorer
- Or run from Command Prompt with optional arguments

### PowerShell Launcher (`start_service.ps1`)

**Features:**
- Native PowerShell interface
- Parameter validation
- Colored output for better readability
- Built-in help system
- Error handling with informative messages

**Parameters:**
- `-Host` - Backend host address
- `-Port` - Backend port number
- `-GuiDelay` - Delay before starting GUI
- `-NoGui` - Start only backend
- `-Help` - Show help

## Prerequisites

Before using any launcher, ensure:

1. **Python 3.11+** is installed
2. **Virtual environment** is created and configured:
   ```bash
   python -m venv venv
   ```

3. **Dependencies** are installed:
   ```bash
   # Windows
   venv\Scripts\activate.bat
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

## Usage Examples

### Development Mode
```bash
# Start with hot reload for development
python launcher.py --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
# Backend only for server deployment
python launcher.py --no-gui --host 0.0.0.0 --port 8000
```

### Testing Different Ports
```bash
# Test on different port
python launcher.py --port 8080
```

### Local Network Access
```bash
# Allow access from other machines on network
python launcher.py --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Common Issues

1. **"Python not found"**
   - Ensure Python is installed and in PATH
   - Use `python --version` to verify

2. **"Virtual environment not found"**
   - Create virtual environment: `python -m venv venv`
   - Activate and install dependencies

3. **"Missing modules"**
   - Activate virtual environment
   - Install requirements: `pip install -r requirements.txt`

4. **"Backend failed to start"**
   - Check if port is already in use
   - Try a different port: `--port 8080`
   - Check database permissions

5. **"GUI failed to start"**
   - Ensure tkinter is available
   - Check backend is running and accessible
   - Try increasing GUI delay: `--gui-delay 10`

### Port Already in Use
```bash
# Find process using port 8000 (Windows)
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <pid> /F

# Or use different port
python launcher.py --port 8080
```

### Backend Not Ready
If GUI can't connect to backend:
- Increase GUI delay: `--gui-delay 10`
- Check backend logs for errors
- Verify backend URL in GUI error messages

## System Requirements

- **Python**: 3.11 or higher
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **RAM**: 512MB minimum
- **Disk**: 100MB for dependencies

## Security Notes

- Default configuration uses HTTP (not HTTPS)
- Use only on trusted networks
- For production, configure proper HTTPS and authentication
- Backend binds to localhost by default for security

## Advanced Configuration

### Environment Variables
You can set these environment variables to override defaults:
```bash
export FASTAPI_HOST=0.0.0.0
export FASTAPI_PORT=8000
export GUI_DELAY=3
```

### Custom Database
The launcher uses the default SQLite database. To use a custom database, modify `app/database.py` before starting.

## Integration with Development Tools

### VS Code
Add to `.vscode/launch.json`:
```json
{
    "name": "Launch Full Service",
    "type": "python",
    "request": "launch",
    "program": "launcher.py",
    "args": ["--gui-delay", "5"],
    "console": "integratedTerminal"
}
```

### PyCharm
Create run configuration:
- Script path: `launcher.py`
- Parameters: `--gui-delay 5`
- Working directory: Project root

## Support

For issues with the launcher scripts:
1. Check this guide for common solutions
2. Verify all prerequisites are met
3. Check Python and dependency versions
4. Review error messages for specific issues

The launcher provides detailed error messages to help diagnose problems quickly.