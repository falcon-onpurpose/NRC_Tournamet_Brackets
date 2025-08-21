#!/usr/bin/env python3
"""
NRC Tournament Program Launcher
Starts both backend and frontend servers and opens the browser
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from pathlib import Path

class TournamentLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.backend_process = None
        self.frontend_process = None
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        
    def check_dependencies(self):
        """Check if required directories and files exist"""
        if not self.backend_dir.exists():
            print("❌ Backend directory not found!")
            return False
        if not self.frontend_dir.exists():
            print("❌ Frontend directory not found!")
            return False
        if not (self.backend_dir / "venv").exists():
            print("❌ Backend virtual environment not found!")
            print("Please run: cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
            return False
        if not (self.frontend_dir / "package.json").exists():
            print("❌ Frontend package.json not found!")
            print("Please run: cd frontend && npm install")
            return False
        return True
    
    def start_backend(self):
        """Start the backend server"""
        print("🚀 Starting backend server...")
        os.chdir(self.backend_dir)
        
        # Activate virtual environment and start server
        if os.name == 'nt':  # Windows
            activate_cmd = str(self.backend_dir / "venv" / "Scripts" / "activate.bat")
            cmd = f'cmd /c "{activate_cmd} && python -m uvicorn main:app --host 127.0.0.1 --port 8000"'
        else:  # Unix/Linux/macOS
            activate_cmd = str(self.backend_dir / "venv" / "bin" / "activate")
            cmd = f'bash -c "source {activate_cmd} && python -m uvicorn main:app --host 127.0.0.1 --port 8000"'
        
        self.backend_process = subprocess.Popen(
            cmd, 
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for backend to start
        time.sleep(3)
        if self.backend_process.poll() is None:
            print("✅ Backend server started successfully")
        else:
            print("❌ Backend server failed to start")
            return False
        return True
    
    def start_frontend(self):
        """Start the frontend server"""
        print("🚀 Starting frontend server...")
        os.chdir(self.frontend_dir)
        
        # Start Next.js development server
        self.frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for frontend to start
        time.sleep(5)
        if self.frontend_process.poll() is None:
            print("✅ Frontend server started successfully")
        else:
            print("❌ Frontend server failed to start")
            return False
        return True
    
    def wait_for_servers(self):
        """Wait for both servers to be ready"""
        print("⏳ Waiting for servers to be ready...")
        
        # Wait for backend
        backend_ready = False
        for i in range(30):  # Wait up to 30 seconds
            try:
                import requests
                response = requests.get(f"{self.backend_url}/health", timeout=1)
                if response.status_code == 200:
                    backend_ready = True
                    break
            except:
                pass
            time.sleep(1)
        
        if not backend_ready:
            print("❌ Backend server not responding")
            return False
        
        # Wait for frontend
        frontend_ready = False
        for i in range(30):  # Wait up to 30 seconds
            try:
                import requests
                response = requests.get(self.frontend_url, timeout=1)
                if response.status_code == 200:
                    frontend_ready = True
                    break
            except:
                pass
            time.sleep(1)
        
        if not frontend_ready:
            print("❌ Frontend server not responding")
            return False
        
        print("✅ Both servers are ready!")
        return True
    
    def open_browser(self):
        """Open the browser to the frontend"""
        print(f"🌐 Opening browser to {self.frontend_url}")
        webbrowser.open(self.frontend_url)
    
    def monitor_servers(self):
        """Monitor server processes and handle shutdown"""
        try:
            while True:
                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend server stopped unexpectedly")
                    break
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend server stopped unexpectedly")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down servers...")
            self.shutdown()
    
    def shutdown(self):
        """Shutdown both servers"""
        print("🛑 Stopping servers...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
            print("✅ Backend server stopped")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
            print("✅ Frontend server stopped")
        
        print("👋 NRC Tournament Program stopped")
    
    def run(self):
        """Main launcher function"""
        print("🎯 NRC Tournament Program Launcher")
        print("=" * 40)
        
        # Check dependencies
        if not self.check_dependencies():
            print("❌ Dependencies check failed. Please fix the issues above.")
            return
        
        try:
            # Start servers
            if not self.start_backend():
                return
            if not self.start_frontend():
                return
            
            # Wait for servers to be ready
            if not self.wait_for_servers():
                return
            
            # Open browser
            self.open_browser()
            
            print("\n🎉 NRC Tournament Program is running!")
            print(f"📱 Frontend: {self.frontend_url}")
            print(f"🔧 Backend API: {self.backend_url}")
            print("Press Ctrl+C to stop the servers")
            print("=" * 40)
            
            # Monitor servers
            self.monitor_servers()
            
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested by user")
            self.shutdown()
        except Exception as e:
            print(f"❌ Error: {e}")
            self.shutdown()

def main():
    launcher = TournamentLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
