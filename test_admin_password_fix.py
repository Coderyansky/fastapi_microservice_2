#!/usr/bin/env python3
"""
Test script for admin password change functionality.

This script tests the fixed admin password change endpoint to ensure
it properly validates admin privileges.
"""

import requests
import json
import base64
from typing import Dict, Any


def create_auth_header(email: str, password: str) -> str:
    """Create HTTP Basic Auth header."""
    credentials = f"{email}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"


def test_admin_password_change():
    """Test admin password change functionality."""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Admin Password Change Fix")
    print("=" * 50)
    
    # Test credentials
    admin_email = "admin@example.com"
    admin_password = "admin123"
    regular_email = "test@example.com"
    regular_password = "test123"
    
    # First, create a test user if not exists
    print("1. Creating test user...")
    test_user_data = {
        "name": "Test User",
        "email": regular_email,
        "password": regular_password,
        "phone": "+1234567890"
    }
    
    try:
        response = requests.post(f"{base_url}/users", json=test_user_data)
        if response.status_code == 201:
            print("✓ Test user created successfully")
            user_data = response.json()
            test_user_id = user_data.get("user", {}).get("id")
        elif response.status_code == 409:
            print("✓ Test user already exists")
            # Get user ID by fetching all users with admin credentials
            admin_headers = {"Authorization": create_auth_header(admin_email, admin_password)}
            users_response = requests.get(f"{base_url}/users", headers=admin_headers)
            if users_response.status_code == 200:
                users = users_response.json().get("users", [])
                test_user = next((u for u in users if u.get("email") == regular_email), None)
                test_user_id = test_user.get("id") if test_user else None
            else:
                print("✗ Failed to get test user ID")
                return
        else:
            print(f"✗ Failed to create test user: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"✗ Error creating test user: {e}")
        return
    
    if not test_user_id:
        print("✗ Could not get test user ID")
        return
    
    print(f"✓ Test user ID: {test_user_id}")
    
    # Test 1: Try changing password as regular user (should fail)
    print("\\n2. Testing password change as regular user (should fail)...")
    regular_headers = {"Authorization": create_auth_header(regular_email, regular_password)}
    password_change_data = {"new_password": "newpassword123"}
    
    try:
        response = requests.post(
            f"{base_url}/users/{test_user_id}/change-password",
            json=password_change_data,
            headers=regular_headers
        )
        
        if response.status_code == 403:
            print("✓ Regular user correctly denied access (403 Forbidden)")
        else:
            print(f"✗ Unexpected response: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Error testing regular user access: {e}")
    
    # Test 2: Try changing password as admin (should succeed)
    print("\\n3. Testing password change as admin (should succeed)...")
    admin_headers = {"Authorization": create_auth_header(admin_email, admin_password)}
    
    try:
        response = requests.post(
            f"{base_url}/users/{test_user_id}/change-password",
            json=password_change_data,
            headers=admin_headers
        )
        
        if response.status_code == 200:
            print("✓ Admin successfully changed user password")
            result = response.json()
            print(f"  Message: {result.get('message', 'N/A')}")
        else:
            print(f"✗ Admin password change failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Error testing admin access: {e}")
    
    # Test 3: Try changing password for non-existent user as admin
    print("\\n4. Testing password change for non-existent user...")
    try:
        response = requests.post(
            f"{base_url}/users/99999/change-password",
            json=password_change_data,
            headers=admin_headers
        )
        
        if response.status_code == 404:
            print("✓ Correctly returned 404 for non-existent user")
        else:
            print(f"✗ Unexpected response for non-existent user: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Error testing non-existent user: {e}")
    
    # Test 4: Try without authentication
    print("\\n5. Testing password change without authentication...")
    try:
        response = requests.post(
            f"{base_url}/users/{test_user_id}/change-password",
            json=password_change_data
        )
        
        if response.status_code == 401:
            print("✓ Correctly returned 401 for unauthenticated request")
        else:
            print(f"✗ Unexpected response for unauthenticated request: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Error testing unauthenticated request: {e}")
    
    print("\\n" + "=" * 50)
    print("Admin password change fix test completed!")


if __name__ == "__main__":
    test_admin_password_change()