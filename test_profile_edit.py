#!/usr/bin/env python3
"""
Test profile editing functionality.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.gui.components.api_client import APIClient
from app.gui.components.auth_manager import AuthenticationManager
from app.gui.components.session_manager import UserSessionManager

def test_profile_editing():
    """Test profile editing functionality."""
    print("Testing Profile Editing Functionality")
    print("=" * 40)
    
    # Create components
    api_client = APIClient("http://localhost:8000")
    auth_manager = AuthenticationManager(api_client)
    session_manager = UserSessionManager(api_client)
    
    # Test authentication
    print("1. Testing authentication...")
    success, error = auth_manager.login("test@example.com", "testpass123")
    if success:
        print("✓ Authentication successful")
        current_user = auth_manager.get_current_user()
        print(f"Current user: {current_user}")
    else:
        print(f"❌ Authentication failed: {error}")
        return
    
    # Test profile update
    print("\n2. Testing profile update...")
    new_data = {
        "name": "Test User Modified",
        "email": "test@example.com", 
        "phone": "89123456788"
    }
    
    success, error = session_manager.update_profile(new_data)
    if success:
        print("✓ Profile update successful")
        updated_user = auth_manager.get_current_user()
        print(f"Updated user: {updated_user}")
    else:
        print(f"❌ Profile update failed: {error}")
    
    # Test getting users
    print("\n3. Testing get users...")
    success, users, error = session_manager.get_users()
    if success:
        print(f"✓ Got {len(users)} users")
        for user in users:
            if user.get('email') == 'test@example.com':
                print(f"Test user in list: {user}")
    else:
        print(f"❌ Get users failed: {error}")

if __name__ == "__main__":
    test_profile_editing()