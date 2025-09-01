"""
User Session Manager for managing current user session data.

This module handles user session data, caching, and session-related
operations for the GUI application.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Callable, Tuple
from .api_client import APIClient


class UserSessionManager:
    """
    Manages user session data and provides caching for user information.
    
    This class handles user data caching, session state management,
    and provides convenient access to user information throughout the application.
    """
    
    def __init__(self, api_client: APIClient):
        """
        Initialize the user session manager.
        
        Args:
            api_client: API client instance for data operations
        """
        self.api_client = api_client
        self._users_cache = []
        self._users_cache_time = None
        self._cache_timeout = 300  # 5 minutes cache timeout
        self._session_data_callbacks = []
    
    def add_session_callback(self, callback: Callable[[], None]) -> None:
        """
        Add a callback to be called when session data changes.
        
        Args:
            callback: Function to call when session data changes
        """
        self._session_data_callbacks.append(callback)
    
    def remove_session_callback(self, callback: Callable[[], None]) -> None:
        """
        Remove a session data callback.
        
        Args:
            callback: Callback function to remove
        """
        if callback in self._session_data_callbacks:
            self._session_data_callbacks.remove(callback)
    
    def _notify_session_change(self) -> None:
        """Notify all registered callbacks about session data change."""
        for callback in self._session_data_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in session callback: {e}")
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current authenticated user data.
        
        Returns:
            User data dictionary or None if not authenticated
        """
        return self.api_client.get_current_user()
    
    def is_admin(self) -> bool:
        """
        Check if current user is admin.
        
        Returns:
            True if current user is admin, False otherwise
        """
        return self.api_client.is_admin()
    
    def get_users(self, force_refresh: bool = False) -> Tuple[bool, Optional[List[Dict]], str]:
        """
        Get list of all users with caching.
        
        Args:
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            Tuple of (success, users_list, error_message)
        """
        # Check if we should use cached data
        if not force_refresh and self._is_cache_valid():
            return True, self._users_cache.copy(), ""
        
        # Fetch fresh data from API
        success, users, error = self.api_client.get_users()
        
        if success:
            # Update cache
            self._users_cache = users or []
            self._users_cache_time = datetime.now()
            self._notify_session_change()
            return True, self._users_cache.copy(), ""
        else:
            # Return cached data if available and there's an error
            if self._users_cache:
                return True, self._users_cache.copy(), f"Using cached data: {error}"
            return False, None, error
    
    def _is_cache_valid(self) -> bool:
        """
        Check if the users cache is still valid.
        
        Returns:
            True if cache is valid, False if expired or empty
        """
        if not self._users_cache or not self._users_cache_time:
            return False
        
        elapsed = (datetime.now() - self._users_cache_time).total_seconds()
        return elapsed < self._cache_timeout
    
    def invalidate_users_cache(self) -> None:
        """Invalidate the users cache to force refresh on next request."""
        self._users_cache = []
        self._users_cache_time = None
        self._notify_session_change()
    
    def update_profile(self, profile_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update current user's profile.
        
        Args:
            profile_data: Dictionary with profile data
            
        Returns:
            Tuple of (success, error_message)
        """
        success, error = self.api_client.update_profile(profile_data)
        
        if success:
            # Invalidate users cache since current user data changed
            self.invalidate_users_cache()
            self._notify_session_change()
        
        return success, error
    
    def change_password(self, new_password: str, repeat_password: str) -> Tuple[bool, str]:
        """
        Change current user's password.
        
        Args:
            new_password: New password
            repeat_password: Repeated password for confirmation
            
        Returns:
            Tuple of (success, error_message)
        """
        return self.api_client.change_password(new_password, repeat_password)
    
    def admin_delete_user(self, user_id: int) -> Tuple[bool, str]:
        """
        Delete a user (admin only).
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            Tuple of (success, error_message)
        """
        if not self.is_admin():
            return False, "Insufficient permissions"
        
        success, error = self.api_client.admin_delete_user(user_id)
        
        if success:
            # Remove user from cache
            self._users_cache = [u for u in self._users_cache if u.get('id') != user_id]
            self._notify_session_change()
        
        return success, error
    
    def admin_change_user_password(self, user_id: int, new_password: str) -> Tuple[bool, str]:
        """
        Change another user's password (admin only).
        
        Args:
            user_id: ID of the user whose password to change
            new_password: New password for the user
            
        Returns:
            Tuple of (success, error_message)
        """
        if not self.is_admin():
            return False, "Insufficient permissions"
        
        return self.api_client.admin_change_user_password(user_id, new_password)
    
    def find_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Find a user by ID in the cached users list.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User data dictionary or None if not found
        """
        for user in self._users_cache:
            if user.get('id') == user_id:
                return user.copy()
        return None
    
    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find a user by email in the cached users list.
        
        Args:
            email: Email address to search for
            
        Returns:
            User data dictionary or None if not found
        """
        for user in self._users_cache:
            if user.get('email') == email:
                return user.copy()
        return None
    
    def get_users_count(self) -> int:
        """
        Get the number of users in cache.
        
        Returns:
            Number of cached users
        """
        return len(self._users_cache)
    
    def clear_session_data(self) -> None:
        """Clear all session data and caches."""
        self._users_cache = []
        self._users_cache_time = None
        self._notify_session_change()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the current cache state.
        
        Returns:
            Dictionary with cache information
        """
        return {
            'users_cached': len(self._users_cache),
            'cache_time': self._users_cache_time,
            'cache_valid': self._is_cache_valid(),
            'cache_age_seconds': (
                (datetime.now() - self._users_cache_time).total_seconds()
                if self._users_cache_time else None
            )
        }