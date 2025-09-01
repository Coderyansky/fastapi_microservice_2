"""
Profile Editor window for editing user profile information.

This module provides an interface for users to edit their personal
information including name, email, and phone number.
"""

import tkinter as tk
from tkinter import ttk
import threading
from typing import Callable, Optional, Dict, Any
from ..components.auth_manager import AuthenticationManager
from ..components.session_manager import UserSessionManager
from ..utils.validators import validate_form_data
from ..utils.helpers import (
    center_window, StatusLabel, set_entry_text, 
    bind_enter_key, show_success_message
)


class ProfileEditor:
    """
    Profile editor window for editing user profile information.
    
    Allows users to modify their name, email, and phone number
    with proper validation and error handling.
    """
    
    def __init__(
        self,
        auth_manager: AuthenticationManager,
        session_manager: UserSessionManager,
        on_profile_updated: Optional[Callable[[], None]] = None
    ):
        """
        Initialize the profile editor.
        
        Args:
            auth_manager: Authentication manager instance
            session_manager: Session manager instance
            on_profile_updated: Callback function to call when profile is updated
        """
        self.auth_manager = auth_manager
        self.session_manager = session_manager
        self.on_profile_updated = on_profile_updated
        
        # Create the window
        self.window = tk.Toplevel()
        self.window.title("Редактирование профиля")
        self.window.resizable(False, False)
        self.window.transient()
        self.window.grab_set()
        
        # Variables for form fields
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        
        # UI elements
        self.name_entry = None
        self.email_entry = None
        self.phone_entry = None
        self.save_button = None
        self.cancel_button = None
        self.status_label = None
        self.status_manager = None
        
        # State
        self.is_saving = False
        self.original_data = {}
        
        self._setup_ui()
        self._center_window()
        self._load_current_data()
        
        # Focus on name field
        if self.name_entry:
            self.name_entry.focus()
    
    def _setup_ui(self) -> None:
        """Set up the user interface elements."""
        # Main frame with padding
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title label
        title_label = ttk.Label(
            main_frame,
            text="Редактирование профиля",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Name field
        ttk.Label(main_frame, text="Имя:").grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.name_entry = ttk.Entry(
            main_frame,
            textvariable=self.name_var,
            width=30
        )
        self.name_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Email field
        ttk.Label(main_frame, text="Email:").grid(
            row=3, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.email_entry = ttk.Entry(
            main_frame,
            textvariable=self.email_var,
            width=30
        )
        self.email_entry.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Phone field
        ttk.Label(main_frame, text="Телефон:").grid(
            row=5, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.phone_entry = ttk.Entry(
            main_frame,
            textvariable=self.phone_var,
            width=30
        )
        self.phone_entry.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=7, column=0, columnspan=2, pady=(0, 10))
        
        # Save button
        self.save_button = ttk.Button(
            buttons_frame,
            text="Сохранить",
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
        self.status_label.grid(row=8, column=0, columnspan=2, pady=(5, 0))
        
        # Set up status manager
        self.status_manager = StatusLabel(self.status_label)
        
        # Bind Enter key to save
        bind_enter_key(self.name_entry, self._on_save_click)
        bind_enter_key(self.email_entry, self._on_save_click)
        bind_enter_key(self.phone_entry, self._on_save_click)
        
        # Configure column weight for resizing
        main_frame.columnconfigure(1, weight=1)
    
    def _center_window(self) -> None:
        """Center the window on the screen."""
        center_window(self.window, 400, 350)
    
    def _load_current_data(self) -> None:
        """Load current user data into the form fields."""
        current_user = self.auth_manager.get_current_user()
        
        if current_user:
            self.original_data = current_user.copy()
            
            # Set form field values
            set_entry_text(self.name_entry, current_user.get('name', ''))
            set_entry_text(self.email_entry, current_user.get('email', ''))
            set_entry_text(self.phone_entry, current_user.get('phone', ''))
        else:
            self.status_manager.show_error("Не удалось загрузить данные пользователя")
    
    def _get_form_data(self) -> Dict[str, str]:
        """
        Get current form data.
        
        Returns:
            Dictionary with form field values
        """
        return {
            'name': self.name_var.get().strip(),
            'email': self.email_var.get().strip(),
            'phone': self.phone_var.get().strip()
        }
    
    def _validate_form(self) -> Optional[str]:
        """
        Validate the form data.
        
        Returns:
            Error message if validation fails, None if all data is valid
        """
        form_data = self._get_form_data()
        required_fields = ['name', 'email']
        
        return validate_form_data(form_data, required_fields)
    
    def _has_changes(self) -> bool:
        """
        Check if the form data has changed from original.
        
        Returns:
            True if there are changes, False otherwise
        """
        current_data = self._get_form_data()
        
        for field in ['name', 'email', 'phone']:
            original_value = self.original_data.get(field, '').strip()
            current_value = current_data.get(field, '').strip()
            
            if original_value != current_value:
                return True
        
        return False
    
    def _on_save_click(self) -> None:
        """Handle save button click."""
        if self.is_saving:
            return
        
        # Clear previous status
        self.status_manager.clear()
        
        # Check if there are any changes
        if not self._has_changes():
            self.status_manager.show_info("Нет изменений для сохранения")
            return
        
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
        self.save_button.config(state="disabled", text="Сохраняем...")
        self.cancel_button.config(state="disabled")
        self.name_entry.config(state="disabled")
        self.email_entry.config(state="disabled")
        self.phone_entry.config(state="disabled")
        
        self.status_manager.show_info("Сохраняем изменения...")
        
        # Get form data
        form_data = self._get_form_data()
        
        # Start save in separate thread
        save_thread = threading.Thread(
            target=self._perform_save,
            args=(form_data,),
            daemon=True
        )
        save_thread.start()
    
    def _perform_save(self, form_data: Dict[str, str]) -> None:
        """
        Perform the actual save operation.
        
        Args:
            form_data: Form data to save
        """
        try:
            # Update profile through session manager
            success, error = self.session_manager.update_profile(form_data)
            
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
        self.save_button.config(state="normal", text="Сохранить")
        self.cancel_button.config(state="normal")
        self.name_entry.config(state="normal")
        self.email_entry.config(state="normal")
        self.phone_entry.config(state="normal")
        
        if success:
            self.status_manager.show_success("Профиль успешно обновлен!")
            
            # Update original data to reflect changes
            self.original_data = self._get_form_data()
            
            # Call callback if provided
            if self.on_profile_updated:
                try:
                    self.on_profile_updated()
                except Exception as e:
                    print(f"Error in profile updated callback: {e}")
            
            # Show success message and close window after delay
            show_success_message("Успех", "Профиль успешно обновлен!")
            self.window.after(1000, self._close_window)
            
        else:
            self.status_manager.show_error(error)
    
    def _on_cancel_click(self) -> None:
        """Handle cancel button click."""
        self._close_window()
    
    def _close_window(self) -> None:
        """Close the profile editor window."""
        try:
            self.window.destroy()
        except tk.TclError:
            pass  # Window already destroyed
    
    def show(self) -> None:
        """Show the profile editor window."""
        self.window.deiconify()
        self.window.lift()
        if self.name_entry:
            self.name_entry.focus()
    
    def hide(self) -> None:
        """Hide the profile editor window."""
        self.window.withdraw()
    
    def destroy(self) -> None:
        """Destroy the profile editor window."""
        try:
            self.window.destroy()
        except tk.TclError:
            pass  # Window already destroyed

    def is_visible(self) -> bool:
        """
        Check if the profile editor window is visible.
        
        Returns:
            True if window is visible, False otherwise
        """
        try:
            return self.window.winfo_viewable()
        except tk.TclError:
            return False