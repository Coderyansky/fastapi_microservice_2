#!/usr/bin/env python3
"""
Main GUI Entry Point for FastAPI User Management Desktop Application.

This script provides the entry point for launching the desktop GUI application
that interfaces with the FastAPI user management microservice.

Usage:
    python main_gui.py [--api-url URL] [--help]

Examples:
    python main_gui.py
    python main_gui.py --api-url http://localhost:8000
    python main_gui.py --api-url http://192.168.1.100:8000
"""

import sys
import argparse
import tkinter as tk
from tkinter import messagebox
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.gui.main_app import MainApplication
except ImportError as e:
    print(f"Error importing GUI modules: {e}")
    print("Please ensure you're running this script from the project root directory.")
    sys.exit(1)


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="FastAPI User Management Desktop Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Connect to localhost:8000
  %(prog)s --api-url http://localhost:8000   # Specify API URL
  %(prog)s --api-url http://192.168.1.100:8000  # Remote API server
        """
    )
    
    parser.add_argument(
        '--api-url',
        default='http://localhost:8000',
        help='Base URL of the FastAPI service (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='FastAPI User Management GUI v1.0.0'
    )
    
    return parser.parse_args()


def validate_api_url(url: str) -> str:
    """
    Validate and normalize the API URL.
    
    Args:
        url: API URL to validate
        
    Returns:
        Normalized URL
        
    Raises:
        ValueError: If URL is invalid
    """
    if not url:
        raise ValueError("API URL cannot be empty")
    
    # Ensure URL starts with http:// or https://
    if not url.startswith(('http://', 'https://')):
        url = f'http://{url}'
    
    # Remove trailing slash
    url = url.rstrip('/')
    
    return url


def check_dependencies():
    """
    Check if all required dependencies are available.
    
    Returns:
        True if all dependencies are available, False otherwise
    """
    missing_modules = []
    
    # Check for required modules
    required_modules = [
        'tkinter',
        'requests',
        'json',
        'base64',
        'threading'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("Error: Missing required modules:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install missing modules and try again.")
        return False
    
    return True


def show_startup_error(title: str, message: str):
    """
    Show startup error dialog.
    
    Args:
        title: Error dialog title
        message: Error message to display
    """
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        # If GUI is not available, print to console
        print(f"Error: {title}")
        print(message)


def main():
    """Main application entry point."""
    print("FastAPI User Management Desktop Application")
    print("=" * 50)
    
    # Parse command line arguments
    try:
        args = parse_arguments()
    except SystemExit:
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Validate API URL
    try:
        api_url = validate_api_url(args.api_url)
        print(f"API URL: {api_url}")
    except ValueError as e:
        show_startup_error("Invalid API URL", str(e))
        return
    
    # Create and run the application
    try:
        print("Starting GUI application...")
        
        # Create main application
        app = MainApplication(api_base_url=api_url)
        
        print("GUI application started successfully!")
        print("\nИнструкции:")
        print("1. Введите email и пароль для входа")
        print("2. Для администраторских функций используйте admin@example.com")
        print("3. Используйте кнопки интерфейса для навигации")
        print("\nДля выхода закройте все окна или нажмите Ctrl+C")
        
        # Run the application
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        
    except ImportError as e:
        error_msg = f"Failed to import required modules: {e}\n\n"
        error_msg += "Please ensure you're running this script from the project root directory "
        error_msg += "and all dependencies are installed."
        show_startup_error("Import Error", error_msg)
        
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}\n\n"
        error_msg += "Please check your Python environment and try again."
        show_startup_error("Application Error", error_msg)
        print(f"Error details: {e}")
        
    finally:
        print("\nApplication terminated.")


if __name__ == "__main__":
    main()