"""
Authentication Manager for handling user authentication state.

This module manages user authentication, credentials, and login state
for the GUI application.
"""

from datetime import datetime, timedelta
from typing import Optional, Callable, Tuple
from .api_client import APIClient


class AuthenticationManager:
    """
    Manages user authentication state and session lifecycle.
    
    This class handles login, logout, session validation, and credential management
    while ensuring security by not persisting sensitive data.
    """
    
    def __init__(self, api_client: APIClient):
        """
        Initialize the authentication manager.
        
        Args:
            api_client: API client instance for authentication requests
        """
        self.api_client = api_client
        self._is_authenticated = False
        self._login_time = None
        self._session_timeout = timedelta(hours=8)  # 8 hour session timeout
        self._authentication_callbacks = []
    
    def add_authentication_callback(self, callback: Callable[[bool], None]) -> None:
        """
        Add a callback to be called when authentication state changes.
        
        Args:
            callback: Function to call with authentication state (True/False)
        """
        self._authentication_callbacks.append(callback)
    
    def remove_authentication_callback(self, callback: Callable[[bool], None]) -> None:
        """
        Remove an authentication callback.
        
        Args:
            callback: Callback function to remove
        """
        if callback in self._authentication_callbacks:
            self._authentication_callbacks.remove(callback)
    
    def _notify_authentication_change(self, is_authenticated: bool) -> None:
        """
        Notify all registered callbacks about authentication state change.
        
        Args:
            is_authenticated: New authentication state
        """
        for callback in self._authentication_callbacks:
            try:
                callback(is_authenticated)
            except Exception as e:
                print(f"Error in authentication callback: {e}")
    
    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Attempt to authenticate user with email and password.
        
        Args:
            email: User email address
            password: User password
            
        Returns:
            Tuple of (success, error_message)
        """
        # Validate inputs
        if not email or not email.strip():
            return False, "Email is required"
        
        if not password:
            return False, "Password is required"
        
        # Attempt authentication through API client
        success, error = self.api_client.authenticate(email.strip(), password)
        
        if success:
            self._is_authenticated = True
            self._login_time = datetime.now()
            self._notify_authentication_change(True)
            return True, ""
        else:
            self._is_authenticated = False
            self._login_time = None
            self._notify_authentication_change(False)
            return False, error
    
    def logout(self) -> None:
        """
        Logout the current user and clear session data.
        """
        # Clear API client authentication
        self.api_client.logout()
        
        # Clear local authentication state
        self._is_authenticated = False
        self._login_time = None
        
        # Notify authentication change
        self._notify_authentication_change(False)
    
    def is_authenticated(self) -> bool:
        """
        Check if user is currently authenticated and session is valid.
        
        Returns:
            True if authenticated and session is valid, False otherwise
        """
        if not self._is_authenticated or not self._login_time:
            return False
        
        # Check session timeout
        if datetime.now() - self._login_time > self._session_timeout:
            # Session has expired
            self.logout()
            return False
        
        # Check if API client still has authentication
        return self.api_client.is_authenticated()
    
    def is_admin(self) -> bool:
        """
        Check if current user has admin privileges.
        
        Returns:
            True if current user is admin, False otherwise
        """
        if not self.is_authenticated():
            return False
        
        return self.api_client.is_admin()
    
    def get_current_user(self) -> Optional[dict]:
        """
        Get current authenticated user information.
        
        Returns:
            User data dictionary if authenticated, None otherwise
        """
        if not self.is_authenticated():
            return None
        
        return self.api_client.get_current_user()
    
    def get_session_info(self) -> dict:
        """
        Get current session information.
        
        Returns:
            Dictionary with session details
        """
        if not self.is_authenticated():
            return {
                'authenticated': False,
                'login_time': None,
                'time_remaining': None,
                'user': None
            }
        
        time_remaining = self._session_timeout - (datetime.now() - self._login_time)
        
        return {
            'authenticated': True,
            'login_time': self._login_time,
            'time_remaining': time_remaining,
            'user': self.get_current_user()
        }
    
    def refresh_session(self) -> None:
        """
        Refresh the current session timestamp.
        This can be called on user activity to extend the session.
        """
        if self._is_authenticated:
            self._login_time = datetime.now()
    
    def check_session_validity(self) -> bool:
        """
        Check if the current session is still valid without side effects.
        
        Returns:
            True if session is valid, False if expired or not authenticated
        """
        if not self._is_authenticated or not self._login_time:
            return False
        
        return datetime.now() - self._login_time <= self._session_timeout
    
    def get_time_until_expiry(self) -> Optional[timedelta]:
        """
        Get time remaining until session expires.
        
        Returns:
            Timedelta until expiry, or None if not authenticated
        """
        if not self._is_authenticated or not self._login_time:
            return None
        
        elapsed = datetime.now() - self._login_time
        remaining = self._session_timeout - elapsed
        
        return remaining if remaining.total_seconds() > 0 else timedelta(0)