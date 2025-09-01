"""
Login Window for user authentication.

This module provides the login interface for users to authenticate
with their email and password.
"""

import tkinter as tk
from tkinter import ttk
import threading
from typing import Callable, Optional
from ..components.auth_manager import AuthenticationManager
from ..utils.validators import validate_email, validate_required_field
from ..utils.helpers import center_window, StatusLabel, bind_enter_key


class LoginWindow:
    """
    Login window for user authentication.
    
    Provides email and password input fields, login functionality,
    and displays appropriate error messages for authentication failures.
    """
    
    def __init__(
        self, 
        auth_manager: AuthenticationManager,
        on_login_success: Callable[[], None]
    ):
        """
        Initialize the login window.
        
        Args:
            auth_manager: Authentication manager for handling login
            on_login_success: Callback function to call on successful login
        """
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success
        
        # Create the window
        self.window = tk.Tk()
        self.window.title("Вход в систему")
        self.window.resizable(False, False)
        
        # Variables for form fields
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        # UI elements
        self.email_entry = None
        self.password_entry = None
        self.login_button = None
        self.status_label = None
        self.status_manager = None
        
        # State
        self.is_logging_in = False
        
        self._setup_ui()
        self._center_window()
        
        # Focus on email field
        self.window.after(100, lambda: self.email_entry.focus())
    
    def _setup_ui(self) -> None:
        """Set up the user interface elements."""
        # Main frame with padding
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title label
        title_label = ttk.Label(
            main_frame, 
            text="Авторизация", 
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Email field
        ttk.Label(main_frame, text="Email:").grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.email_entry = ttk.Entry(
            main_frame, 
            textvariable=self.email_var, 
            width=30
        )
        self.email_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Password field
        ttk.Label(main_frame, text="Пароль:").grid(
            row=3, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.password_entry = ttk.Entry(
            main_frame, 
            textvariable=self.password_var, 
            show="*", 
            width=30
        )
        self.password_entry.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Login button
        self.login_button = ttk.Button(
            main_frame, 
            text="Войти", 
            command=self._on_login_click
        )
        self.login_button.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(
            main_frame, 
            text="", 
            foreground="red",
            wraplength=250
        )
        self.status_label.grid(row=6, column=0, columnspan=2, pady=(5, 0))
        
        # Set up status manager
        self.status_manager = StatusLabel(self.status_label)
        
        # Bind Enter key to login
        bind_enter_key(self.email_entry, self._on_login_click)
        bind_enter_key(self.password_entry, self._on_login_click)
        
        # Configure column weight for resizing
        main_frame.columnconfigure(1, weight=1)
    
    def _center_window(self) -> None:
        """Center the window on the screen."""
        center_window(self.window, 350, 280)
    
    def _validate_inputs(self) -> Optional[str]:
        """
        Validate user inputs.
        
        Returns:
            Error message if validation fails, None if all inputs are valid
        """
        email = self.email_var.get().strip()
        password = self.password_var.get()
        
        # Validate email
        is_valid, error = validate_email(email)
        if not is_valid:
            return error
        
        # Validate password
        is_valid, error = validate_required_field(password, "Пароль")
        if not is_valid:
            return error
        
        return None
    
    def _on_login_click(self) -> None:
        """Handle login button click."""
        if self.is_logging_in:
            return
        
        # Clear previous status
        self.status_manager.clear()
        
        # Validate inputs
        validation_error = self._validate_inputs()
        if validation_error:
            self.status_manager.show_error(validation_error)
            return
        
        # Start login process
        self._start_login()
    
    def _start_login(self) -> None:
        """Start the login process in a separate thread."""
        self.is_logging_in = True
        
        # Disable UI elements
        self.login_button.config(state="disabled", text="Входим...")
        self.email_entry.config(state="disabled")
        self.password_entry.config(state="disabled")
        
        self.status_manager.show_info("Проверяем данные...")
        
        # Get credentials
        email = self.email_var.get().strip()
        password = self.password_var.get()
        
        # Start login in separate thread
        login_thread = threading.Thread(
            target=self._perform_login,
            args=(email, password),
            daemon=True
        )
        login_thread.start()
    
    def _perform_login(self, email: str, password: str) -> None:
        """
        Perform the actual login operation.
        
        Args:
            email: User email
            password: User password
        """
        try:
            # Attempt authentication
            success, error = self.auth_manager.login(email, password)
            
            # Schedule UI update on main thread
            self.window.after(0, self._on_login_complete, success, error)
            
        except Exception as e:
            # Handle unexpected errors
            error_msg = f"Неожиданная ошибка: {str(e)}"
            self.window.after(0, self._on_login_complete, False, error_msg)
    
    def _on_login_complete(self, success: bool, error: str) -> None:
        """
        Handle login completion on the main thread.
        
        Args:
            success: Whether login was successful
            error: Error message if login failed
        """
        self.is_logging_in = False
        
        # Re-enable UI elements
        self.login_button.config(state="normal", text="Войти")
        self.email_entry.config(state="normal")
        self.password_entry.config(state="normal")
        
        if success:
            self.status_manager.show_success("Вход выполнен успешно!")
            # Call success callback after a short delay
            self.window.after(500, self._handle_login_success)
        else:
            self.status_manager.show_error(error)
            # Focus back on password field for retry
            self.password_entry.focus()
    
    def _handle_login_success(self) -> None:
        """Handle successful login."""
        try:
            self.on_login_success()
        except Exception as e:
            self.status_manager.show_error(f"Ошибка при входе: {str(e)}")
    
    def show(self) -> None:
        """Show the login window."""
        self.window.deiconify()
        self.window.lift()
        self.email_entry.focus()
    
    def hide(self) -> None:
        """Hide the login window."""
        self.window.withdraw()
    
    def destroy(self) -> None:
        """Destroy the login window."""
        self.window.destroy()
    
    def clear_fields(self) -> None:
        """Clear the input fields."""
        self.email_var.set("")
        self.password_var.set("")
        self.status_manager.clear()
    
    def set_email(self, email: str) -> None:
        """
        Set the email field value.
        
        Args:
            email: Email address to set
        """
        self.email_var.set(email)
    
    def focus_password(self) -> None:
        """Focus on the password field."""
        self.password_entry.focus()
    
    def is_visible(self) -> bool:
        """
        Check if the login window is visible.
        
        Returns:
            True if window is visible, False otherwise
        """
        try:
            return self.window.winfo_viewable()
        except tk.TclError:
            return False