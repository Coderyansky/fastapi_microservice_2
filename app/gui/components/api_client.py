"""
API Client for communicating with the FastAPI user management service.

This module provides a centralized client for all HTTP communication
with the FastAPI microservice, including authentication and error handling.
"""

import base64
import json
import requests
from typing import Dict, List, Optional, Tuple, Any
from requests.exceptions import RequestException, Timeout, ConnectionError


class APIClientError(Exception):
    """Base exception for API client errors."""
    pass


class AuthenticationError(APIClientError):
    """Exception raised for authentication errors."""
    pass


class APIClient:
    """
    Client for communicating with the FastAPI user management service.
    
    This class handles HTTP Basic Authentication, request/response processing,
    and error handling for all API interactions.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the FastAPI service
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.auth_header = None
        self.current_user = None
        self.timeout = 30  # seconds
    
    def _create_auth_header(self, email: str, password: str) -> str:
        """
        Create HTTP Basic Authentication header.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Base64 encoded authentication string
        """
        credentials = f"{email}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        require_auth: bool = True
    ) -> Tuple[bool, Any, str]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request data (for POST/PUT requests)
            require_auth: Whether authentication is required
            
        Returns:
            Tuple of (success, response_data, error_message)
        """
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        # Add authentication header if required and available
        if require_auth and self.auth_header:
            headers['Authorization'] = self.auth_header
        
        try:
            # Prepare request data
            json_data = json.dumps(data) if data else None
            
            # Make the request
            response = self.session.request(
                method=method,
                url=url,
                data=json_data,
                headers=headers,
                timeout=self.timeout
            )
            
            # Handle response
            if response.status_code == 200 or response.status_code == 201:
                try:
                    return True, response.json(), ""
                except json.JSONDecodeError:
                    return True, {"message": "Success"}, ""
            
            elif response.status_code == 401:
                return False, None, "Неверный логин или пароль"
            
            elif response.status_code == 403:
                return False, None, "Недостаточно прав"
            
            elif response.status_code == 404:
                return False, None, "Пользователь не найден"
            
            elif response.status_code == 409:
                return False, None, "Email уже используется"
            
            elif response.status_code == 422:
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and 'detail' in error_data:
                        if isinstance(error_data['detail'], list):
                            # Validation error format
                            errors = [item.get('msg', str(item)) for item in error_data['detail']]
                            return False, None, "; ".join(errors)
                        else:
                            return False, None, str(error_data['detail'])
                    return False, None, "Ошибка валидации данных"
                except json.JSONDecodeError:
                    return False, None, "Ошибка валидации данных"
            
            elif response.status_code >= 500:
                return False, None, "Ошибка сервера"
            
            else:
                return False, None, f"Неожиданная ошибка: {response.status_code}"
        
        except Timeout:
            return False, None, "Превышено время ожидания"
        
        except ConnectionError:
            return False, None, "Не удается подключиться к серверу"
        
        except RequestException as e:
            return False, None, f"Ошибка сети: {str(e)}"
        
        except Exception as e:
            return False, None, f"Неожиданная ошибка: {str(e)}"
    
    def authenticate(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate user and store credentials.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, error_message)
        """
        # Create auth header
        auth_header = self._create_auth_header(email, password)
        
        # Temporarily set auth header for the request
        old_auth = self.auth_header
        self.auth_header = auth_header
        
        # Try to get users list to validate authentication
        success, data, error = self._make_request('GET', '/users')
        
        if success:
            # Authentication successful, find current user
            users_list = None
            
            # Handle wrapped response format
            if isinstance(data, dict) and 'users' in data:
                users_list = data['users']
            elif isinstance(data, list):
                users_list = data
            
            if isinstance(users_list, list):
                for user in users_list:
                    if user.get('email') == email:
                        self.current_user = user
                        break
                else:
                    # User not found in list, but auth worked - create basic user info
                    self.current_user = {'email': email, 'name': email.split('@')[0]}
            
            return True, ""
        else:
            # Authentication failed, restore old auth header
            self.auth_header = old_auth
            self.current_user = None
            return False, error
    
    def logout(self) -> None:
        """Clear authentication data."""
        self.auth_header = None
        self.current_user = None
    
    def get_users(self) -> Tuple[bool, Optional[List[Dict]], str]:
        """
        Get list of all users.
        
        Returns:
            Tuple of (success, users_list, error_message)
        """
        success, data, error = self._make_request('GET', '/users')
        
        if success:
            # Check if response is wrapped in StandardResponse format
            if isinstance(data, dict) and 'users' in data:
                users_list = data['users']
                if isinstance(users_list, list):
                    return True, users_list, ""
                else:
                    return False, None, "Invalid response format: users is not a list"
            elif isinstance(data, list):
                # Direct list response
                return True, data, ""
            else:
                return False, None, "Unexpected response format"
        else:
            return False, None, error
    
    def update_profile(self, profile_data: Dict) -> Tuple[bool, str]:
        """
        Update user profile.
        
        Args:
            profile_data: Dictionary with profile data (name, email, phone)
            
        Returns:
            Tuple of (success, error_message)
        """
        success, data, error = self._make_request('PUT', '/api/user/profile', profile_data)
        
        if success:
            # Update current user data from response
            if self.current_user and isinstance(data, dict):
                if 'user' in data and isinstance(data['user'], dict):
                    # Update with user data from response
                    self.current_user.update(data['user'])
                else:
                    # Fallback: update with request data
                    self.current_user.update(profile_data)
            return True, ""
        else:
            return False, error
    
    def change_password(self, new_password: str, repeat_password: str) -> Tuple[bool, str]:
        """
        Change user password.
        
        Args:
            new_password: New password
            repeat_password: Repeated password for confirmation
            
        Returns:
            Tuple of (success, error_message)
        """
        password_data = {
            'new_password': new_password,
            'new_password_repeat': repeat_password
        }
        
        success, data, error = self._make_request('PUT', '/api/user/password', password_data)
        
        if success:
            return True, ""
        else:
            return False, error
    
    def admin_delete_user(self, user_id: int) -> Tuple[bool, str]:
        """
        Delete a user (admin only).
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            Tuple of (success, error_message)
        """
        success, data, error = self._make_request('DELETE', f'/users/{user_id}')
        
        if success:
            return True, ""
        else:
            return False, error
    
    def admin_change_user_password(self, user_id: int, new_password: str) -> Tuple[bool, str]:
        """
        Change another user's password (admin only).
        
        Args:
            user_id: ID of the user whose password to change
            new_password: New password for the user
            
        Returns:
            Tuple of (success, error_message)
        """
        password_data = {'new_password': new_password}
        
        success, data, error = self._make_request(
            'POST', 
            f'/users/{user_id}/change-password', 
            password_data
        )
        
        if success:
            return True, ""
        else:
            return False, error
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self.auth_header is not None and self.current_user is not None
    
    def is_admin(self) -> bool:
        """Check if current user is admin."""
        if not self.current_user:
            return False
        return self.current_user.get('email') == 'admin@example.com'
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current user data."""
        return self.current_user.copy() if self.current_user else None