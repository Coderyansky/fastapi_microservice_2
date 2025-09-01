#!/usr/bin/env python3
"""
Comprehensive endpoint tester for FastAPI User Management Microservice
Tests all 7 required endpoints with various scenarios including error cases.
"""

import requests
import json
import base64
import sys
from typing import Dict, Any
import time

class EndpointTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.test_user_data = {
            "name": "Test User",
            "email": "test@example.com", 
            "password": "TestPassword123",
            "phone": "+7 900 100-20-30"
        }
        self.created_user_id = None
        self.auth_headers = {}
        self.test_results = []
        
    def create_auth_header(self, email: str, password: str) -> Dict[str, str]:
        """Create HTTP Basic Auth header"""
        credentials = base64.b64encode(f"{email}:{password}".encode()).decode()
        return {"Authorization": f"Basic {credentials}"}
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def test_server_health(self) -> bool:
        """Test if server is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Server Health Check", True, f"Server running: {data.get('message', 'OK')}")
                return True
            else:
                self.log_test("Server Health Check", False, f"Status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Server Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_create_user(self) -> bool:
        """Test POST /users - Create new user"""
        try:
            response = requests.post(
                f"{self.base_url}/users",
                json=self.test_user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                data = response.json()
                if data.get("result") == "ok" and "user" in data:
                    self.created_user_id = data["user"]["id"]
                    self.auth_headers = self.create_auth_header(
                        self.test_user_data["email"], 
                        self.test_user_data["password"]
                    )
                    self.log_test("Create User", True, f"User created with ID: {self.created_user_id}")
                    return True
                else:
                    self.log_test("Create User", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("Create User", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Create User", False, f"Request error: {str(e)}")
            return False
    
    def test_create_duplicate_user(self) -> bool:
        """Test POST /users - Try to create user with existing email"""
        try:
            response = requests.post(
                f"{self.base_url}/users",
                json=self.test_user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 409:
                data = response.json()
                if "Email уже используется" in data.get("message", ""):
                    self.log_test("Create Duplicate User", True, "Correctly rejected duplicate email")
                    return True
                else:
                    self.log_test("Create Duplicate User", False, f"Wrong error message: {data}")
                    return False
            else:
                self.log_test("Create Duplicate User", False, f"Expected 409, got {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Create Duplicate User", False, f"Request error: {str(e)}")
            return False
    
    def test_get_users(self) -> bool:
        """Test GET /users - Get all users (with auth)"""
        try:
            response = requests.get(f"{self.base_url}/users", headers=self.auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("result") == "ok" and "users" in data and len(data["users"]) > 0:
                    self.log_test("Get All Users", True, f"Retrieved {len(data['users'])} users")
                    return True
                else:
                    self.log_test("Get All Users", False, f"Invalid response: {data}")
                    return False
            else:
                self.log_test("Get All Users", False, f"Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get All Users", False, f"Request error: {str(e)}")
            return False
    
    def test_get_users_no_auth(self) -> bool:
        """Test GET /users - Try without authentication"""
        try:
            response = requests.get(f"{self.base_url}/users")
            
            if response.status_code == 401:
                self.log_test("Get Users No Auth", True, "Correctly rejected unauthenticated request")
                return True
            else:
                self.log_test("Get Users No Auth", False, f"Expected 401, got {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get Users No Auth", False, f"Request error: {str(e)}")
            return False
    
    def test_get_user_by_id(self) -> bool:
        """Test GET /users/{user_id} - Get specific user"""
        if not self.created_user_id:
            self.log_test("Get User By ID", False, "No user ID available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/users/{self.created_user_id}", 
                headers=self.auth_headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("result") == "ok" and "user" in data:
                    user = data["user"]
                    if user["id"] == self.created_user_id and user["email"] == self.test_user_data["email"]:
                        self.log_test("Get User By ID", True, f"Retrieved user: {user['name']}")
                        return True
                    else:
                        self.log_test("Get User By ID", False, f"User data mismatch: {user}")
                        return False
                else:
                    self.log_test("Get User By ID", False, f"Invalid response: {data}")
                    return False
            else:
                self.log_test("Get User By ID", False, f"Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get User By ID", False, f"Request error: {str(e)}")
            return False
    
    def test_update_profile(self) -> bool:
        """Test PUT /api/user/profile - Update own profile"""
        update_data = {
            "name": "Updated Test User",
            "phone": "+7 900 200-30-40"
        }
        
        try:
            response = requests.put(
                f"{self.base_url}/api/user/profile",
                json=update_data,
                headers={**self.auth_headers, "Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("result") == "ok" and "user" in data:
                    user = data["user"]
                    if user["name"] == update_data["name"] and user["phone"] == update_data["phone"]:
                        self.log_test("Update Profile", True, f"Profile updated: {user['name']}")
                        return True
                    else:
                        self.log_test("Update Profile", False, f"Update not applied: {user}")
                        return False
                else:
                    self.log_test("Update Profile", False, f"Invalid response: {data}")
                    return False
            else:
                self.log_test("Update Profile", False, f"Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Update Profile", False, f"Request error: {str(e)}")
            return False
    
    def test_change_password(self) -> bool:
        """Test PUT /api/user/password - Change own password"""
        new_password = "NewTestPassword456"
        password_data = {
            "new_password": new_password,
            "new_password_repeat": new_password
        }
        
        try:
            response = requests.put(
                f"{self.base_url}/api/user/password",
                json=password_data,
                headers={**self.auth_headers, "Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("result") == "ok" and "успешно изменён" in data.get("message", ""):
                    # Update auth headers for new password
                    self.auth_headers = self.create_auth_header(
                        self.test_user_data["email"], 
                        new_password
                    )
                    self.log_test("Change Password", True, "Password changed successfully")
                    return True
                else:
                    self.log_test("Change Password", False, f"Invalid response: {data}")
                    return False
            else:
                self.log_test("Change Password", False, f"Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Change Password", False, f"Request error: {str(e)}")
            return False
    
    def test_change_password_mismatch(self) -> bool:
        """Test PUT /api/user/password - Password mismatch error"""
        password_data = {
            "new_password": "Password123",
            "new_password_repeat": "DifferentPassword456"
        }
        
        try:
            response = requests.put(
                f"{self.base_url}/api/user/password",
                json=password_data,
                headers={**self.auth_headers, "Content-Type": "application/json"}
            )
            
            if response.status_code == 422:
                self.log_test("Password Mismatch", True, "Correctly rejected mismatched passwords")
                return True
            else:
                self.log_test("Password Mismatch", False, f"Expected 422, got {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Password Mismatch", False, f"Request error: {str(e)}")
            return False
    
    def test_admin_change_password(self) -> bool:
        """Test POST /users/{user_id}/change-password - Admin password change"""
        if not self.created_user_id:
            self.log_test("Admin Change Password", False, "No user ID available")
            return False
            
        admin_password_data = {
            "new_password": "AdminChangedPassword789"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/users/{self.created_user_id}/change-password",
                json=admin_password_data,
                headers={**self.auth_headers, "Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("result") == "ok" and "успешно изменён" in data.get("message", ""):
                    # Update auth headers for new password
                    self.auth_headers = self.create_auth_header(
                        self.test_user_data["email"], 
                        admin_password_data["new_password"]
                    )
                    self.log_test("Admin Change Password", True, "Admin password change successful")
                    return True
                else:
                    self.log_test("Admin Change Password", False, f"Invalid response: {data}")
                    return False
            else:
                self.log_test("Admin Change Password", False, f"Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Admin Change Password", False, f"Request error: {str(e)}")
            return False
    
    def test_delete_user(self) -> bool:
        """Test DELETE /users/{user_id} - Delete own user"""
        if not self.created_user_id:
            self.log_test("Delete User", False, "No user ID available")
            return False
            
        try:
            response = requests.delete(
                f"{self.base_url}/users/{self.created_user_id}",
                headers=self.auth_headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("result") == "ok" and "успешно удален" in data.get("message", ""):
                    self.log_test("Delete User", True, "User deleted successfully")
                    return True
                else:
                    self.log_test("Delete User", False, f"Invalid response: {data}")
                    return False
            else:
                self.log_test("Delete User", False, f"Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Delete User", False, f"Request error: {str(e)}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all endpoint tests"""
        print("🚀 Starting FastAPI User Management Microservice Tests")
        print("=" * 60)
        
        # Test server health first
        if not self.test_server_health():
            print("\n❌ Server is not accessible. Please start the server first.")
            print("Run: python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
            return False
        
        print("\n📝 Testing User Management Endpoints...")
        print("-" * 40)
        
        # Core functionality tests
        tests = [
            self.test_create_user,
            self.test_create_duplicate_user,
            self.test_get_users_no_auth,
            self.test_get_users,
            self.test_get_user_by_id,
            self.test_update_profile,
            self.test_change_password_mismatch,
            self.test_change_password,
            self.test_admin_change_password,
            self.test_delete_user
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                self.log_test(test.__name__, False, f"Exception: {str(e)}")
            time.sleep(0.5)  # Small delay between tests
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! The microservice is working correctly.")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. Please check the implementation.")
            return False


def main():
    """Main function to run tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test FastAPI User Management Microservice")
    parser.add_argument("--url", default="http://127.0.0.1:8000", 
                       help="Base URL of the microservice (default: http://127.0.0.1:8000)")
    
    args = parser.parse_args()
    
    tester = EndpointTester(args.url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()