"""
Password Changer window for changing user password.

This module provides an interface for users to change their password
with proper validation and confirmation.
"""

import tkinter as tk
from tkinter import ttk
import threading
from typing import Callable, Optional
from ..components.auth_manager import AuthenticationManager
from ..components.session_manager import UserSessionManager
from ..utils.validators import validate_password_match, validate_required_field
from ..utils.helpers import (
    center_window, StatusLabel, clear_entry_fields,
    bind_enter_key, show_success_message
)


class PasswordChanger:
    """
    Password changer window for changing user password.
    
    Provides fields for new password and password confirmation
    with proper validation and error handling.
    """
    
    def __init__(
        self,
        auth_manager: AuthenticationManager,
        session_manager: UserSessionManager,
        on_password_changed: Optional[Callable[[], None]] = None
    ):
        """
        Initialize the password changer.
        
        Args:
            auth_manager: Authentication manager instance
            session_manager: Session manager instance
            on_password_changed: Callback function to call when password is changed
        """
        self.auth_manager = auth_manager
        self.session_manager = session_manager
        self.on_password_changed = on_password_changed
        
        # Create the window
        self.window = tk.Toplevel()
        self.window.title("Смена пароля")
        self.window.resizable(False, False)
        self.window.transient()
        self.window.grab_set()
        
        # Variables for form fields
        self.new_password_var = tk.StringVar()
        self.repeat_password_var = tk.StringVar()
        
        # UI elements
        self.new_password_entry = None
        self.repeat_password_entry = None
        self.save_button = None
        self.cancel_button = None
        self.status_label = None
        self.status_manager = None
        
        # State
        self.is_saving = False
        
        self._setup_ui()
        self._center_window()
        
        # Focus on new password field
        if self.new_password_entry:
            self.new_password_entry.focus()
    
    def _setup_ui(self) -> None:
        """Set up the user interface elements."""
        # Main frame with padding
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title label
        title_label = ttk.Label(
            main_frame,
            text="Смена пароля",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Info label
        info_label = ttk.Label(
            main_frame,
            text="Введите новый пароль и подтвердите его",
            foreground="gray"
        )
        info_label.grid(row=1, column=0, columnspan=2, pady=(0, 15))
        
        # New password field
        ttk.Label(main_frame, text="Новый пароль:").grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.new_password_entry = ttk.Entry(
            main_frame,
            textvariable=self.new_password_var,
            show="*",
            width=30
        )
        self.new_password_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Repeat password field
        ttk.Label(main_frame, text="Повторите пароль:").grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.repeat_password_entry = ttk.Entry(
            main_frame,
            textvariable=self.repeat_password_var,
            show="*",
            width=30
        )
        self.repeat_password_entry.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        
        # Save button
        self.save_button = ttk.Button(
            buttons_frame,
            text="Сменить пароль",
            command=self._on_save_click
        )
        self.save_button.grid(row=0, column=0, padx=(0, 10))
        
        # Cancel button
        self.cancel_button = ttk.Button(
            buttons_frame,
            text="Отмена",
            command=self._on_cancel_click
        )
        self.cancel_button.grid(row=0, column=1)
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="",
            wraplength=300
        )
        self.status_label.grid(row=7, column=0, columnspan=2, pady=(5, 0))
        
        # Set up status manager
        self.status_manager = StatusLabel(self.status_label)
        
        # Bind Enter key to save
        bind_enter_key(self.new_password_entry, self._on_save_click)
        bind_enter_key(self.repeat_password_entry, self._on_save_click)
        
        # Configure column weight for resizing
        main_frame.columnconfigure(1, weight=1)
    
    def _center_window(self) -> None:
        """Center the window on the screen."""
        center_window(self.window, 400, 300)
    
    def _validate_form(self) -> Optional[str]:
        """
        Validate the form data.
        
        Returns:
            Error message if validation fails, None if all data is valid
        """
        new_password = self.new_password_var.get()
        repeat_password = self.repeat_password_var.get()
        
        # Validate new password
        is_valid, error = validate_required_field(new_password, "Новый пароль")
        if not is_valid:
            return error
        
        # Check minimum password length
        if len(new_password) < 4:  # Minimum password length
            return "Пароль должен содержать не менее 4 символов"
        
        # Validate password match
        is_valid, error = validate_password_match(new_password, repeat_password)
        if not is_valid:
            return error
        
        return None
    
    def _on_save_click(self) -> None:
        """Handle save button click."""
        if self.is_saving:
            return
        
        # Clear previous status
        self.status_manager.clear()
        
        # Validate form data
        validation_error = self._validate_form()
        if validation_error:
            self.status_manager.show_error(validation_error)
            return
        
        # Start save process
        self._start_save()
    
    def _start_save(self) -> None:
        """Start the save process in a separate thread."""
        self.is_saving = True
        
        # Disable UI elements
        self.save_button.config(state="disabled", text="Меняем пароль...")
        self.cancel_button.config(state="disabled")
        self.new_password_entry.config(state="disabled")
        self.repeat_password_entry.config(state="disabled")
        
        self.status_manager.show_info("Меняем пароль...")
        
        # Get passwords
        new_password = self.new_password_var.get()
        repeat_password = self.repeat_password_var.get()
        
        # Start save in separate thread
        save_thread = threading.Thread(
            target=self._perform_save,
            args=(new_password, repeat_password),
            daemon=True
        )
        save_thread.start()
    
    def _perform_save(self, new_password: str, repeat_password: str) -> None:
        """
        Perform the actual password change operation.
        
        Args:
            new_password: New password
            repeat_password: Repeated password for confirmation
        """
        try:
            # Change password through session manager
            success, error = self.session_manager.change_password(new_password, repeat_password)
            
            # Schedule UI update on main thread
            self.window.after(0, self._on_save_complete, success, error)
            
        except Exception as e:
            error_msg = f"Неожиданная ошибка: {str(e)}"
            self.window.after(0, self._on_save_complete, False, error_msg)
    
    def _on_save_complete(self, success: bool, error: str) -> None:
        """
        Handle save completion on the main thread.
        
        Args:
            success: Whether save was successful
            error: Error message if save failed
        """
        self.is_saving = False
        
        # Re-enable UI elements
        self.save_button.config(state="normal", text="Сменить пароль")
        self.cancel_button.config(state="normal")
        self.new_password_entry.config(state="normal")
        self.repeat_password_entry.config(state="normal")
        
        if success:
            self.status_manager.show_success("Пароль успешно изменён!")
            
            # Clear password fields for security
            clear_entry_fields(self.new_password_entry, self.repeat_password_entry)
            
            # Call callback if provided
            if self.on_password_changed:
                try:
                    self.on_password_changed()
                except Exception as e:
                    print(f"Error in password changed callback: {e}")
            
            # Show success message and close window after delay
            show_success_message("Успех", "Пароль успешно изменён!")
            self.window.after(1000, self._close_window)
            
        else:
            self.status_manager.show_error(error)
            # Clear password fields for security on error
            clear_entry_fields(self.new_password_entry, self.repeat_password_entry)
            # Focus back on new password field for retry
            self.new_password_entry.focus()
    
    def _on_cancel_click(self) -> None:
        """Handle cancel button click."""
        self._close_window()
    
    def _close_window(self) -> None:
        """Close the password changer window."""
        # Clear password fields for security
        clear_entry_fields(self.new_password_entry, self.repeat_password_entry)
        
        try:
            self.window.destroy()
        except tk.TclError:
            pass  # Window already destroyed
    
    def show(self) -> None:
        """Show the password changer window."""
        # Clear fields when showing
        clear_entry_fields(self.new_password_entry, self.repeat_password_entry)
        self.status_manager.clear()
        
        self.window.deiconify()
        self.window.lift()
        if self.new_password_entry:
            self.new_password_entry.focus()
    
    def hide(self) -> None:
        """Hide the password changer window."""
        # Clear password fields for security
        clear_entry_fields(self.new_password_entry, self.repeat_password_entry)
        self.window.withdraw()
    
    def destroy(self) -> None:
        """Destroy the password changer window."""
        # Clear password fields for security
        clear_entry_fields(self.new_password_entry, self.repeat_password_entry)
        try:
            self.window.destroy()
        except tk.TclError:
            pass  # Window already destroyed

    def is_visible(self) -> bool:
        """
        Check if the password changer window is visible.
        
        Returns:
            True if window is visible, False otherwise
        """
        try:
            return self.window.winfo_viewable()
        except tk.TclError:
            return False