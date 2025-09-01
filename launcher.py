#!/usr/bin/env python3
"""
Complete Service Launcher for FastAPI User Management System.

This script launches both the FastAPI backend service and the GUI application
together, handling the full startup sequence and providing a unified entry point.

Usage:
    python launcher.py [options]

Options:
    --host HOST         Backend host (default: 127.0.0.1)
    --port PORT         Backend port (default: 8000)
    --gui-delay SECONDS Delay before starting GUI (default: 3)
    --no-gui           Start only the backend service
    --help             Show this help message

Examples:
    python launcher.py                          # Start both backend and GUI
    python launcher.py --port 8080             # Use custom port
    python launcher.py --no-gui                # Backend only
    python launcher.py --gui-delay 5           # Wait 5 seconds before GUI
"""

import sys
import os
import argparse
import time
import threading
import subprocess
import signal
import atexit
import requests
from typing import Optional, List
import tkinter as tk
from tkinter import messagebox

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

class ServiceLauncher:
    """Main service launcher class that manages both backend and GUI processes."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8000, 
                 gui_delay: int = 3, start_gui: bool = True):
        """
        Initialize the service launcher.
        
        Args:
            host: Backend server host
            port: Backend server port
            gui_delay: Delay in seconds before starting GUI
            start_gui: Whether to start the GUI application
        """
        self.host = host
        self.port = port
        self.gui_delay = gui_delay
        self.should_start_gui = start_gui
        self.api_url = f"http://{host}:{port}"
        
        # Process management
        self.backend_process = None
        self.gui_thread = None
        self.gui_app = None
        self.shutdown_requested = False
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        print(f"\nReceived signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up all processes and resources."""
        print("Cleaning up resources...")
        
        # Stop GUI application
        if self.gui_app and hasattr(self.gui_app, 'quit'):
            try:
                self.gui_app.quit()
            except Exception as e:
                print(f"Error stopping GUI: {e}")
        
        # Stop backend process
        if self.backend_process:
            try:
                print("Stopping backend service...")
                self.backend_process.terminate()
                # Wait for graceful shutdown
                try:
                    self.backend_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print("Force killing backend process...")
                    self.backend_process.kill()
                    self.backend_process.wait()
                print("Backend service stopped.")
            except Exception as e:
                print(f"Error stopping backend: {e}")
    
    def check_dependencies(self) -> bool:
        """
        Check if all required dependencies are available.
        
        Returns:
            True if all dependencies are available, False otherwise
        """
        missing_modules = []
        
        # Check for required modules
        required_modules = [
            'fastapi',
            'uvicorn',
            'sqlalchemy',
            'passlib',
            'requests',
            'tkinter'
        ]
        
        for module in required_modules:
            try:
                if module == 'tkinter':
                    import tkinter
                else:
                    __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            print("Error: Missing required modules:")
            for module in missing_modules:
                print(f"  - {module}")
            print("\nPlease install missing modules:")
            print("pip install -r requirements.txt")
            return False
        
        return True
    
    def start_backend(self) -> bool:
        """
        Start the FastAPI backend service.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            print(f"Starting backend service on {self.host}:{self.port}...")
            
            # Start uvicorn server as subprocess
            cmd = [
                sys.executable, "-m", "uvicorn",
                "app.main:app",
                "--host", self.host,
                "--port", str(self.port),
                "--reload"
            ]
            
            self.backend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print("Backend process started, waiting for service to be ready...")
            return self.wait_for_backend()
            
        except Exception as e:
            print(f"Failed to start backend service: {e}")
            return False
    
    def wait_for_backend(self, timeout: int = 30) -> bool:
        """
        Wait for backend service to be ready.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if service is ready, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.shutdown_requested:
                return False
                
            try:
                response = requests.get(f"{self.api_url}/health", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("result") == "ok":
                        print("✓ Backend service is ready!")
                        return True
            except requests.exceptions.RequestException:
                pass
            
            # Check if backend process is still running
            if self.backend_process and self.backend_process.poll() is not None:
                try:
                    if self.backend_process.stderr:
                        stderr_output = self.backend_process.stderr.read()
                        if stderr_output:
                            print(f"Backend process error: {stderr_output}")
                except Exception as e:
                    print(f"Error reading backend process stderr: {e}")
                return False
            
            print(".", end="", flush=True)
            time.sleep(1)
        
        print(f"\nTimeout waiting for backend service after {timeout} seconds")
        return False
    
    def start_gui(self):
        """Start the GUI application in a separate thread."""
        try:
            if self.gui_delay > 0:
                print(f"Waiting {self.gui_delay} seconds before starting GUI...")
                time.sleep(self.gui_delay)
            
            if self.shutdown_requested:
                return
            
            print("Starting GUI application...")
            
            # Import GUI modules
            from app.gui.main_app import MainApplication
            
            # Create and run GUI application
            self.gui_app = MainApplication(api_base_url=self.api_url)
            
            print("✓ GUI application started!")
            print("\nИнструкции по использованию:")
            print("1. Введите email и пароль для входа")
            print("2. Для администраторских функций используйте admin@example.com")
            print("3. Используйте кнопки интерфейса для навигации")
            print("4. Для остановки сервиса закройте все окна или нажмите Ctrl+C")
            
            # Run the GUI application (this blocks until GUI is closed)
            self.gui_app.run()
            
        except Exception as e:
            print(f"Failed to start GUI application: {e}")
            self.show_error("GUI Error", f"Failed to start GUI application: {e}")
    
    def show_error(self, title: str, message: str):
        """Show error dialog."""
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(title, message)
            root.destroy()
        except Exception:
            print(f"Error: {title} - {message}")
    
    def run(self) -> bool:
        """
        Run the complete service stack.
        
        Returns:
            True if successful, False otherwise
        """
        print("FastAPI User Management Service Launcher")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        try:
            # Start backend service
            if not self.start_backend():
                print("Failed to start backend service")
                return False
            
            # Start GUI if requested
            if self.should_start_gui and not self.shutdown_requested:
                self.gui_thread = threading.Thread(target=self.start_gui, daemon=True)
                self.gui_thread.start()
                
                # Wait for GUI thread to complete or until interrupted
                try:
                    self.gui_thread.join()
                except KeyboardInterrupt:
                    print("\nShutdown requested by user")
            else:
                print("Backend service running. Press Ctrl+C to stop.")
                try:
                    # Keep the main thread alive
                    while not self.shutdown_requested:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nShutdown requested by user")
            
            return True
            
        except Exception as e:
            print(f"Error during service execution: {e}")
            return False
        
        finally:
            self.cleanup()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Complete Service Launcher for FastAPI User Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Start both backend and GUI
  %(prog)s --port 8080             # Use custom port
  %(prog)s --no-gui                # Backend only
  %(prog)s --gui-delay 5           # Wait 5 seconds before GUI
  %(prog)s --host 0.0.0.0 --port 8000  # Custom host and port
        """
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Backend host address (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Backend port number (default: 8000)'
    )
    
    parser.add_argument(
        '--gui-delay',
        type=int,
        default=3,
        help='Delay in seconds before starting GUI (default: 3)'
    )
    
    parser.add_argument(
        '--no-gui',
        action='store_true',
        help='Start only the backend service without GUI'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='FastAPI User Management Service Launcher v1.0.0'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Create and run service launcher
        launcher = ServiceLauncher(
            host=args.host,
            port=args.port,
            gui_delay=args.gui_delay,
            start_gui=not args.no_gui
        )
        
        success = launcher.run()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nService launcher interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()