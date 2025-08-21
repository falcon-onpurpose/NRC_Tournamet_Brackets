# NRC Tournament Program Launcher

## Overview
The NRC Tournament Program Launcher is a simple program that starts both the backend and frontend servers automatically and opens your browser to the application.

## Quick Start

### Option 1: Using the Shell Script (Recommended)
```bash
./start.sh
```

### Option 2: Using Python Directly
```bash
python3 launcher.py
```

## What the Launcher Does

1. **Checks Dependencies**: Verifies that all required files and directories exist
2. **Starts Backend**: Activates the virtual environment and starts the FastAPI server on port 8000
3. **Starts Frontend**: Starts the Next.js development server on port 3000
4. **Waits for Servers**: Ensures both servers are responding before proceeding
5. **Opens Browser**: Automatically opens your default browser to the frontend
6. **Monitors Servers**: Keeps both servers running and handles graceful shutdown

## Features

- ✅ **Automatic Server Management**: Starts both backend and frontend
- ✅ **Dependency Checking**: Verifies all required components are installed
- ✅ **Browser Integration**: Opens the application in your default browser
- ✅ **Graceful Shutdown**: Properly stops both servers when you press Ctrl+C
- ✅ **Cross-Platform**: Works on Windows, macOS, and Linux
- ✅ **Error Handling**: Provides clear error messages if something goes wrong

## URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Stopping the Program

Press **Ctrl+C** in the terminal where the launcher is running. This will:
- Stop the backend server
- Stop the frontend server
- Close the launcher

## Troubleshooting

### "Backend virtual environment not found"
Run these commands in the backend directory:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### "Frontend package.json not found"
Run these commands in the frontend directory:
```bash
cd frontend
npm install
```

### "Python 3 is not installed"
Install Python 3 from https://python.org

### "npm is not installed"
Install Node.js from https://nodejs.org

## Manual Server Management

If you prefer to run servers manually:

### Backend
```bash
cd backend
source venv/bin/activate
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

## Creating a Desktop Shortcut

### macOS
1. Right-click on `start.sh`
2. Select "Make Alias"
3. Move the alias to your Desktop
4. Double-click to run

### Windows
1. Right-click on `start.sh`
2. Select "Create shortcut"
3. Move the shortcut to your Desktop
4. Double-click to run

### Linux
1. Right-click on your Desktop
2. Select "Create Launcher"
3. Set the command to: `/path/to/NRC Tournament Program/start.sh`
4. Set the name to: "NRC Tournament Program"
