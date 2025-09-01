"""
User Profile View for regular users to see their profile information.

This module provides a nice interface for regular users to view their own
profile information in a card-like format, instead of seeing all users.
"""

import tkinter as tk
from tkinter import ttk
import threading
from typing import Callable, Optional, Dict, Any
from ..components.auth_manager import AuthenticationManager
from ..components.session_manager import UserSessionManager
from ..utils.helpers import (
    center_window, StatusLabel, show_error_message, 
    show_success_message, format_datetime, safe_get
)


class UserProfileView:
    """
    User profile view window for regular users.
    
    Shows the user's own profile information in a nice card format
    with options to edit profile and change password.
    """
    
    def __init__(
        self,
        auth_manager: AuthenticationManager,
        session_manager: UserSessionManager,
        on_edit_profile: Callable[[], None],
        on_change_password: Callable[[], None],
        on_logout: Callable[[], None]
    ):
        """
        Initialize the user profile view.
        
        Args:
            auth_manager: Authentication manager instance
            session_manager: Session manager instance
            on_edit_profile: Callback for edit profile action
            on_change_password: Callback for change password action
            on_logout: Callback for logout action
        """
        self.auth_manager = auth_manager
        self.session_manager = session_manager
        self.on_edit_profile = on_edit_profile
        self.on_change_password = on_change_password
        self.on_logout = on_logout
        
        # Create the window
        self.window = tk.Toplevel()
        self.window.title("Мой профиль")
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # UI elements
        self.profile_frame = None
        self.name_label = None
        self.email_label = None
        self.phone_label = None
        self.created_label = None
        self.edit_button = None
        self.password_button = None
        self.logout_button = None
        self.refresh_button = None
        self.status_label = None
        self.status_manager = None
        
        # State
        self.is_refreshing = False
        
        self._setup_ui()
        self._center_window()
        self._update_profile_display()
    
    def _setup_ui(self) -> None:
        """Set up the user interface elements."""
        # Main frame with padding
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Мой профиль", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Profile card frame
        self._setup_profile_card(main_frame)
        
        # Buttons frame
        self._setup_buttons_frame(main_frame)
        
        # Status frame
        self._setup_status_frame(main_frame)
    
    def _setup_profile_card(self, parent: ttk.Frame) -> None:
        """Set up the profile information card."""
        # Profile card frame with border
        self.profile_frame = ttk.LabelFrame(
            parent, 
            text="Информация о профиле", 
            padding="20"
        )
        self.profile_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        self.profile_frame.columnconfigure(1, weight=1)
        
        # Profile picture placeholder (you could add an image here)
        profile_icon = ttk.Label(
            self.profile_frame, 
            text="👤", 
            font=("Arial", 48)
        )
        profile_icon.grid(row=0, column=0, rowspan=4, padx=(0, 20), sticky=tk.N)
        
        # Profile information
        # Name
        ttk.Label(
            self.profile_frame, 
            text="Имя:", 
            font=("Arial", 10, "bold")
        ).grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        self.name_label = ttk.Label(
            self.profile_frame, 
            text="", 
            font=("Arial", 12)
        )
        self.name_label.grid(row=0, column=2, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Email
        ttk.Label(
            self.profile_frame, 
            text="Email:", 
            font=("Arial", 10, "bold")
        ).grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        
        self.email_label = ttk.Label(
            self.profile_frame, 
            text="", 
            font=("Arial", 12)
        )
        self.email_label.grid(row=1, column=2, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Phone
        ttk.Label(
            self.profile_frame, 
            text="Телефон:", 
            font=("Arial", 10, "bold")
        ).grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        self.phone_label = ttk.Label(
            self.profile_frame, 
            text="", 
            font=("Arial", 12)
        )
        self.phone_label.grid(row=2, column=2, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Created date
        ttk.Label(
            self.profile_frame, 
            text="Зарегистрирован:", 
            font=("Arial", 10, "bold")
        ).grid(row=3, column=1, sticky=tk.W, pady=(0, 5))
        
        self.created_label = ttk.Label(
            self.profile_frame, 
            text="", 
            font=("Arial", 12)
        )
        self.created_label.grid(row=3, column=2, sticky=tk.W, padx=(10, 0), pady=(0, 5))
    
    def _setup_buttons_frame(self, parent: ttk.Frame) -> None:
        """Set up the buttons frame."""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=2, column=0, pady=(0, 20))
        
        # Edit profile button
        self.edit_button = ttk.Button(
            buttons_frame,
            text="Редактировать профиль",
            command=self._on_edit_profile_click
        )
        self.edit_button.grid(row=0, column=0, padx=(0, 10))
        
        # Change password button
        self.password_button = ttk.Button(
            buttons_frame,
            text="Сменить пароль",
            command=self._on_change_password_click
        )
        self.password_button.grid(row=0, column=1, padx=(0, 10))
        
        # Refresh button
        self.refresh_button = ttk.Button(
            buttons_frame,
            text="Обновить",
            command=self._on_refresh_click
        )
        self.refresh_button.grid(row=0, column=2, padx=(0, 10))
        
        # Logout button
        self.logout_button = ttk.Button(
            buttons_frame,
            text="Выйти",
            command=self._on_logout_click
        )
        self.logout_button.grid(row=0, column=3)
    
    def _setup_status_frame(self, parent: ttk.Frame) -> None:
        """Set up the status frame."""
        self.status_label = ttk.Label(parent, text="")
        self.status_label.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        self.status_manager = StatusLabel(self.status_label)
    
    def _center_window(self) -> None:
        """Center the window on the screen."""
        center_window(self.window, 500, 400)
    
    def _update_profile_display(self) -> None:
        """Update the profile display with current user data."""
        current_user = self.auth_manager.get_current_user()
        
        if current_user:
            # Update profile information
            self.name_label.config(text=safe_get(current_user, 'name', 'N/A'))
            self.email_label.config(text=safe_get(current_user, 'email', 'N/A'))
            phone = safe_get(current_user, 'phone', '')
            self.phone_label.config(text=phone if phone else 'Не указан')
            
            created_at = format_datetime(safe_get(current_user, 'created_at', ''))
            self.created_label.config(text=created_at)
            
            self.status_manager.show_success("Профиль загружен")
        else:
            # Clear profile information
            self.name_label.config(text="N/A")
            self.email_label.config(text="N/A")
            self.phone_label.config(text="N/A")
            self.created_label.config(text="N/A")
            
            self.status_manager.show_error("Не удалось загрузить профиль")
    
    def _on_refresh_click(self) -> None:
        """Handle refresh button click."""
        if self.is_refreshing:
            return
        
        self.is_refreshing = True
        self.refresh_button.config(state="disabled", text="Обновляем...")
        self.status_manager.show_info("Обновляем профиль...")
        
        # Start refresh in separate thread
        refresh_thread = threading.Thread(
            target=self._perform_refresh,
            daemon=True
        )
        refresh_thread.start()
    
    def _perform_refresh(self) -> None:
        """Perform the actual refresh operation."""
        try:
            # Get fresh user data
            success, users, error = self.session_manager.get_users(force_refresh=True)
            
            if success and users:
                # Find current user in the list
                current_email = self.auth_manager.get_current_user().get('email')
                for user in users:
                    if user.get('email') == current_email:
                        # Update current user data
                        self.auth_manager.api_client.current_user = user
                        break
            
            # Schedule UI update on main thread
            self.window.after(0, self._on_refresh_complete, success, error)
            
        except Exception as e:
            error_msg = f"Ошибка при обновлении: {str(e)}"
            self.window.after(0, self._on_refresh_complete, False, error_msg)
    
    def _on_refresh_complete(self, success: bool, error: str) -> None:
        """Handle refresh completion on the main thread."""
        self.is_refreshing = False
        self.refresh_button.config(state="normal", text="Обновить")
        
        if success:
            self._update_profile_display()
        else:
            self.status_manager.show_error(error or "Ошибка при обновлении")
    
    def _on_edit_profile_click(self) -> None:
        """Handle edit profile button click."""
        try:
            self.on_edit_profile()
        except Exception as e:
            show_error_message("Ошибка", f"Не удалось открыть редактор профиля: {str(e)}")
    
    def _on_change_password_click(self) -> None:
        """Handle change password button click."""
        try:
            self.on_change_password()
        except Exception as e:
            show_error_message("Ошибка", f"Не удалось открыть форму смены пароля: {str(e)}")
    
    def _on_logout_click(self) -> None:
        """Handle logout button click."""
        try:
            self.on_logout()
        except Exception as e:
            show_error_message("Ошибка", f"Ошибка при выходе: {str(e)}")
    
    def _on_window_close(self) -> None:
        """Handle window close event."""
        self._on_logout_click()
    
    def show(self) -> None:
        """Show the profile view window."""
        self.window.deiconify()
        self.window.lift()
        self._update_profile_display()
    
    def hide(self) -> None:
        """Hide the profile view window."""
        self.window.withdraw()
    
    def destroy(self) -> None:
        """Destroy the profile view window."""
        self.window.destroy()
    
    def refresh_data(self) -> None:
        """Refresh profile data."""
        self._update_profile_display()
    
    def is_visible(self) -> bool:
        """
        Check if the profile view window is visible.
        
        Returns:
            True if window is visible, False otherwise
        """
        try:
            return self.window.winfo_viewable()
        except tk.TclError:
            return False