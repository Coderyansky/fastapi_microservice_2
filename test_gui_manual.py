#!/usr/bin/env python3
"""
Manual GUI test with sample credentials.
"""

import sys
import os
import traceback
import requests
import json

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def create_test_user():
    """Create a test user for testing purposes."""
    try:
        # First, let's create a test user via the API
        user_data = {
            "name": "Test User", 
            "email": "test@example.com",
            "phone": "89123456788",
            "password": "testpass123"
        }
        
        response = requests.post("http://localhost:8000/users", json=user_data)
        if response.status_code in [200, 201]:
            print("✓ Test user created successfully")
            return True
        elif response.status_code == 409:
            print("✓ Test user already exists")
            return True
        else:
            print(f"Failed to create test user: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error creating test user: {e}")
        return False

def test_api_connection():
    """Test API connection."""
    try:
        response = requests.get("http://localhost:8000/users", 
                               auth=("admin@example.com", "admin123"))
        if response.status_code == 200:
            users = response.json()
            print(f"✓ API connection successful, found {len(users)} users")
            return True
        else:
            print(f"API connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"API connection error: {e}")
        return False

def main():
    try:
        print("FastAPI User Management GUI - Manual Test")
        print("=" * 50)
        
        # Test API connection
        if not test_api_connection():
            print("❌ API connection failed. Please ensure the FastAPI server is running.")
            return
        
        # Create test user
        create_test_user()
        
        print("\nStarting GUI application...")
        print("Login credentials for testing:")
        print("- Admin: admin@example.com / admin123")
        print("- Test User: test@example.com / testpass123")
        print("- Note: Close the GUI window to exit")
        print()
        
        from app.gui.main_app import MainApplication
        
        # Create and run application
        app = MainApplication(api_base_url="http://localhost:8000")
        app.run()
        
        print("✓ GUI application completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during GUI test: {e}")
        print("Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    main()