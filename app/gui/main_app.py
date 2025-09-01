"""
Main Application class for orchestrating all GUI components.

This module provides the main application controller that manages
all windows, authentication flow, and component coordination.
"""

import tkinter as tk
from typing import Optional
from .components.api_client import APIClient
from .components.auth_manager import AuthenticationManager
from .components.session_manager import UserSessionManager
from .windows.login_window import LoginWindow
from .windows.main_dashboard import MainDashboard
from .windows.profile_editor import ProfileEditor
from .windows.password_changer import PasswordChanger
from .windows.admin_panel import AdminPanel


class MainApplication:
    """
    Main application controller for the GUI application.
    
    Orchestrates all GUI components, manages authentication flow,
    and coordinates between different windows and managers.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize the main application.
        
        Args:
            api_base_url: Base URL for the FastAPI service
        """
        # Core components
        self.api_client = APIClient(api_base_url)
        self.auth_manager = AuthenticationManager(self.api_client)
        self.session_manager = UserSessionManager(self.api_client)
        
        # Windows
        self.login_window: Optional[LoginWindow] = None
        self.main_dashboard: Optional[MainDashboard] = None
        self.profile_editor: Optional[ProfileEditor] = None
        self.password_changer: Optional[PasswordChanger] = None
        self.admin_panel: Optional[AdminPanel] = None
        
        # Application state
        self.is_running = False
        
        # Set up authentication callbacks
        self.auth_manager.add_authentication_callback(self._on_authentication_changed)
        
        # Initialize login window
        self._create_login_window()
    
    def _create_login_window(self) -> None:
        """Create the login window."""
        if self.login_window:
            try:
                self.login_window.destroy()
            except tk.TclError:
                pass
        
        self.login_window = LoginWindow(
            auth_manager=self.auth_manager,
            on_login_success=self._on_login_success
        )
    
    def _create_main_dashboard(self) -> None:
        """Create the main dashboard window."""
        if self.main_dashboard:
            try:
                self.main_dashboard.destroy()
            except tk.TclError:
                pass
        
        self.main_dashboard = MainDashboard(
            auth_manager=self.auth_manager,
            session_manager=self.session_manager,
            on_edit_profile=self._on_edit_profile,
            on_change_password=self._on_change_password,
            on_admin_panel=lambda: None,  # Not used anymore
            on_logout=self._on_logout
        )
    
    def _on_login_success(self) -> None:
        """Handle successful login."""
        # Hide login window
        if self.login_window:
            self.login_window.hide()
        
        # Create and show main dashboard
        self._create_main_dashboard()
        
        # Show dashboard
        if self.main_dashboard:
            self.main_dashboard.show()
    
    def _on_authentication_changed(self, is_authenticated: bool) -> None:
        """
        Handle authentication state changes.
        
        Args:
            is_authenticated: Current authentication state
        """
        if not is_authenticated:
            # User logged out or session expired
            self._show_login_screen()
    
    def _show_login_screen(self) -> None:
        """Show the login screen and hide other windows."""
        # Hide all windows except login
        self._hide_all_windows_except_login()
        
        # Clear login form and show login window
        if self.login_window:
            self.login_window.clear_fields()
            self.login_window.show()
        else:
            self._create_login_window()
            if self.login_window:
                self.login_window.show()
    
    def _hide_all_windows_except_login(self) -> None:
        """Hide all windows except the login window."""
        windows_to_hide = [
            self.main_dashboard,
            self.profile_editor,
            self.password_changer,
            self.admin_panel
        ]
        
        for window in windows_to_hide:
            if window and hasattr(window, 'hide'):
                try:
                    window.hide()
                except (tk.TclError, AttributeError) as e:
                    print(f"Warning: Could not hide window: {e}")
    
    def _on_edit_profile(self) -> None:
        """Handle edit profile action."""
        if not self.auth_manager.is_authenticated():
            return
        
        # Close existing profile editor if open
        if self.profile_editor and hasattr(self.profile_editor, 'destroy'):
            try:
                self.profile_editor.destroy()
            except (tk.TclError, AttributeError) as e:
                print(f"Warning: Could not destroy profile editor: {e}")
        
        # Create new profile editor
        self.profile_editor = ProfileEditor(
            auth_manager=self.auth_manager,
            session_manager=self.session_manager,
            on_profile_updated=self._on_profile_updated
        )
        
        # Show profile editor
        if hasattr(self.profile_editor, 'show'):
            self.profile_editor.show()
    
    def _on_profile_updated(self) -> None:
        """Handle profile update completion."""
        # Refresh dashboard data
        if self.main_dashboard:
            self.main_dashboard.refresh_data()
    
    def _on_change_password(self) -> None:
        """Handle change password action."""
        if not self.auth_manager.is_authenticated():
            return
        
        # Close existing password changer if open
        if self.password_changer and hasattr(self.password_changer, 'destroy'):
            try:
                self.password_changer.destroy()
            except (tk.TclError, AttributeError) as e:
                print(f"Warning: Could not destroy password changer: {e}")
        
        # Create new password changer
        self.password_changer = PasswordChanger(
            auth_manager=self.auth_manager,
            session_manager=self.session_manager,
            on_password_changed=self._on_password_changed
        )
        
        # Show password changer
        if hasattr(self.password_changer, 'show'):
            self.password_changer.show()
    
    def _on_password_changed(self) -> None:
        """Handle password change completion."""
        # No specific action needed for now
        pass
    
    def _on_admin_panel(self) -> None:
        """Handle admin panel action (deprecated - functionality integrated into dashboard)."""
        # Admin functionality is now integrated into the main dashboard
        pass
    
    def _on_admin_data_changed(self) -> None:
        """Handle admin data changes (user deletion, etc.)."""
        # Refresh dashboard data
        if self.main_dashboard:
            self.main_dashboard.refresh_data()
    
    def _on_logout(self) -> None:
        """Handle logout action."""
        # Clear authentication
        self.auth_manager.logout()
        
        # Clear session data
        self.session_manager.clear_session_data()
        
        # Show login screen
        self._show_login_screen()
    
    def run(self) -> None:
        """Start the application main loop."""
        self.is_running = True
        
        # Show initial login screen
        if self.login_window:
            self.login_window.show()
            
            # Start Tkinter main loop
            try:
                self.login_window.window.mainloop()
            except KeyboardInterrupt:
                self.quit()
            except Exception as e:
                print(f"Application error: {e}")
                self.quit()
        else:
            print("Failed to create login window")
    
    def quit(self) -> None:
        """Quit the application."""
        self.is_running = False
        
        # Logout if authenticated
        if self.auth_manager.is_authenticated():
            self.auth_manager.logout()
        
        # Destroy all windows safely
        windows_to_destroy = [
            self.login_window,
            self.main_dashboard,
            self.profile_editor,
            self.password_changer,
            self.admin_panel
        ]
        
        for window in windows_to_destroy:
            if window and hasattr(window, 'destroy'):
                try:
                    window.destroy()
                except (tk.TclError, AttributeError) as e:
                    print(f"Warning: Could not destroy window: {e}")
        
        # Quit Tkinter safely
        try:
            # Find the root window and quit
            root = tk._default_root
            if root:
                root.quit()
        except (tk.TclError, AttributeError) as e:
            print(f"Warning: Could not quit Tkinter: {e}")
    
    def is_login_window_visible(self) -> bool:
        """
        Check if login window is visible.
        
        Returns:
            True if login window is visible, False otherwise
        """
        try:
            return (self.login_window and 
                   hasattr(self.login_window, 'is_visible') and 
                   self.login_window.is_visible())
        except (tk.TclError, AttributeError):
            return False
    
    def is_dashboard_visible(self) -> bool:
        """
        Check if main dashboard is visible.
        
        Returns:
            True if main dashboard is visible, False otherwise
        """
        return self.main_dashboard and self.main_dashboard.is_visible()
    
    def get_current_state(self) -> str:
        """
        Get the current application state.
        
        Returns:
            String describing current state
        """
        if self.auth_manager.is_authenticated():
            if self.is_dashboard_visible():
                return "dashboard"
            elif self.profile_editor and self.profile_editor.is_visible():
                return "profile_editor"
            elif self.password_changer and self.password_changer.is_visible():
                return "password_changer"
            elif self.admin_panel and self.admin_panel.is_visible():
                return "admin_panel"
            else:
                return "authenticated_unknown"
        elif self.is_login_window_visible():
            return "login"
        else:
            return "unknown"
    
    def set_api_base_url(self, url: str) -> None:
        """
        Change the API base URL.
        
        Args:
            url: New base URL for the API
        """
        if self.api_client:
            self.api_client.base_url = url.rstrip('/')
    
    def get_session_info(self) -> dict:
        """
        Get current session information.
        
        Returns:
            Dictionary with session details
        """
        return self.auth_manager.get_session_info()
    
    def refresh_all_data(self) -> None:
        """Refresh all cached data."""
        if self.session_manager:
            self.session_manager.invalidate_users_cache()
        
        if self.main_dashboard:
            self.main_dashboard.refresh_data()