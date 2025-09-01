#!/usr/bin/env python3
"""
Simple test script for GUI functionality.
"""

import sys
import os
import traceback

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    print("Testing GUI imports...")
    from app.gui.main_app import MainApplication
    print("✓ MainApplication import successful")
    
    print("Creating MainApplication instance...")
    app = MainApplication(api_base_url="http://localhost:8000")
    print("✓ MainApplication created successfully")
    
    print("Testing application methods...")
    print(f"Current state: {app.get_current_state()}")
    print(f"Login visible: {app.is_login_window_visible()}")
    
    print("Starting GUI (will run for 10 seconds)...")
    
    # Set a timer to quit after 10 seconds for testing
    if app.login_window and app.login_window.window:
        app.login_window.window.after(10000, app.quit)
        app.run()
    
    print("GUI test completed successfully!")
    
except Exception as e:
    print(f"Error during GUI test: {e}")
    print("Traceback:")
    traceback.print_exc()