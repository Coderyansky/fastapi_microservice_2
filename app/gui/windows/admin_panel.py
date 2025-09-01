"""
Admin Panel window for administrative functions.

This module provides administrative functions like deleting users
and changing other users' passwords (admin@example.com only).
"""

import tkinter as tk
from tkinter import ttk
import threading
from typing import Callable, Optional, List, Dict, Any
from ..components.auth_manager import AuthenticationManager
from ..components.session_manager import UserSessionManager
from ..utils.validators import validate_required_field
from ..utils.helpers import (
    center_window, StatusLabel, clear_entry_fields,
    bind_enter_key, show_success_message, show_confirmation_dialog,
    show_error_message, safe_get
)


class AdminPanel:
    """
    Admin panel window for administrative functions.
    
    Provides functionality for admin users to delete users
    and change other users' passwords.
    """
    
    def __init__(
        self,
        auth_manager: AuthenticationManager,
        session_manager: UserSessionManager,
        on_data_changed: Optional[Callable[[], None]] = None
    ):
        """
        Initialize the admin panel.
        
        Args:
            auth_manager: Authentication manager instance
            session_manager: Session manager instance
            on_data_changed: Callback function to call when data is changed
        """
        self.auth_manager = auth_manager
        self.session_manager = session_manager
        self.on_data_changed = on_data_changed
        
        # Check admin permissions
        if not self.auth_manager.is_admin():
            show_error_message("Ошибка доступа", "Недостаточно прав для доступа к панели администратора")
            return
        
        # Create the window
        self.window = tk.Toplevel()
        self.window.title("Панель администратора")
        self.window.resizable(False, False)
        self.window.transient()
        self.window.grab_set()
        
        # Variables
        self.selected_user_var = tk.StringVar()
        self.new_password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()
        
        # UI elements
        self.users_combobox = None
        self.delete_button = None
        self.new_password_entry = None
        self.confirm_password_entry = None
        self.change_password_button = None
        self.close_button = None
        self.status_label = None
        self.status_manager = None
        
        # State
        self.is_processing = False
        self.users_data = []
        
        self._setup_ui()
        self._center_window()
        self._load_users()
    
    def _setup_ui(self) -> None:
        """Set up the user interface elements."""
        # Main frame with padding
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title label
        title_label = ttk.Label(
            main_frame,
            text="Панель администратора",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Warning label
        warning_label = ttk.Label(
            main_frame,
            text="⚠ Будьте осторожны! Эти действия необратимы.",
            foreground="red"
        )
        warning_label.grid(row=1, column=0, columnspan=2, pady=(0, 15))
        
        # User selection section
        self._setup_user_selection_section(main_frame)
        
        # Delete user section
        self._setup_delete_user_section(main_frame)
        
        # Change password section
        self._setup_change_password_section(main_frame)
        
        # Buttons section
        self._setup_buttons_section(main_frame)
        
        # Status section
        self._setup_status_section(main_frame)
        
        # Configure column weight for resizing
        main_frame.columnconfigure(1, weight=1)
    
    def _setup_user_selection_section(self, parent: ttk.Frame) -> None:
        """Set up the user selection section."""
        # User selection frame
        user_frame = ttk.LabelFrame(parent, text="Выбор пользователя", padding="10")
        user_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        user_frame.columnconfigure(1, weight=1)
        
        ttk.Label(user_frame, text="Пользователь:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        
        self.users_combobox = ttk.Combobox(
            user_frame,
            textvariable=self.selected_user_var,
            state="readonly",
            width=40
        )
        self.users_combobox.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.users_combobox.bind('<<ComboboxSelected>>', self._on_user_selected)
    
    def _setup_delete_user_section(self, parent: ttk.Frame) -> None:
        """Set up the delete user section."""
        # Delete user frame
        delete_frame = ttk.LabelFrame(parent, text="Удаление пользователя", padding="10")
        delete_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(
            delete_frame,
            text="Удалить выбранного пользователя из системы",
            foreground="gray"
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.delete_button = ttk.Button(
            delete_frame,
            text="Удалить пользователя",
            command=self._on_delete_user_click
        )
        self.delete_button.grid(row=1, column=0, sticky=tk.W)
    
    def _setup_change_password_section(self, parent: ttk.Frame) -> None:
        """Set up the change password section."""
        # Change password frame
        password_frame = ttk.LabelFrame(parent, text="Смена пароля пользователя", padding="10")
        password_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        password_frame.columnconfigure(1, weight=1)
        
        # New password field
        ttk.Label(password_frame, text="Новый пароль:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.new_password_entry = ttk.Entry(
            password_frame,
            textvariable=self.new_password_var,
            show="*",
            width=30
        )
        self.new_password_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Confirm password field
        ttk.Label(password_frame, text="Подтвердите пароль:").grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        self.confirm_password_entry = ttk.Entry(
            password_frame,
            textvariable=self.confirm_password_var,
            show="*",
            width=30
        )
        self.confirm_password_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Change password button
        self.change_password_button = ttk.Button(
            password_frame,
            text="Сменить пароль",
            command=self._on_change_password_click
        )
        self.change_password_button.grid(row=4, column=0, sticky=tk.W)
        
        # Bind Enter key to change password
        bind_enter_key(self.new_password_entry, self._on_change_password_click)
        bind_enter_key(self.confirm_password_entry, self._on_change_password_click)
    
    def _setup_buttons_section(self, parent: ttk.Frame) -> None:
        """Set up the buttons section."""
        # Buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        
        # Close button
        self.close_button = ttk.Button(
            buttons_frame,
            text="Закрыть",
            command=self._on_close_click
        )
        self.close_button.grid(row=0, column=0)
    
    def _setup_status_section(self, parent: ttk.Frame) -> None:
        """Set up the status section."""
        self.status_label = ttk.Label(
            parent,
            text="",
            wraplength=400
        )
        self.status_label.grid(row=6, column=0, columnspan=2, pady=(5, 0))
        
        self.status_manager = StatusLabel(self.status_label)
    
    def _center_window(self) -> None:
        """Center the window on the screen."""
        center_window(self.window, 500, 480)
    
    def _load_users(self) -> None:
        """Load users data for the combobox."""
        success, users, error = self.session_manager.get_users()
        
        if success and users:
            self.users_data = users
            
            # Filter out current admin user
            current_user = self.auth_manager.get_current_user()
            current_email = current_user.get('email') if current_user else None
            
            filtered_users = [
                user for user in users 
                if user.get('email') != current_email
            ]
            
            # Create display values for combobox
            user_options = []
            for user in filtered_users:
                display_name = f"{safe_get(user, 'name', 'N/A')} ({safe_get(user, 'email', 'N/A')})"
                user_options.append(display_name)
            
            self.users_combobox['values'] = user_options
            
            if user_options:
                self.status_manager.show_success(f"Загружено {len(user_options)} пользователей")
            else:
                self.status_manager.show_info("Нет пользователей для администрирования")
                self._disable_admin_functions()
        else:
            self.status_manager.show_error(error or "Ошибка при загрузке пользователей")
            self._disable_admin_functions()
    
    def _disable_admin_functions(self) -> None:
        """Disable admin function buttons."""
        self.delete_button.config(state="disabled")
        self.change_password_button.config(state="disabled")
        self.new_password_entry.config(state="disabled")
        self.confirm_password_entry.config(state="disabled")
    
    def _on_user_selected(self, event) -> None:
        """Handle user selection in combobox."""
        selected_index = self.users_combobox.current()
        
        if selected_index >= 0:
            # Enable admin functions
            self.delete_button.config(state="normal")
            self.change_password_button.config(state="normal")
            self.new_password_entry.config(state="normal")
            self.confirm_password_entry.config(state="normal")
            
            # Clear password fields
            clear_entry_fields(self.new_password_entry, self.confirm_password_entry)
            self.status_manager.clear()
        else:
            # Disable admin functions
            self.delete_button.config(state="disabled")
            self.change_password_button.config(state="disabled")
            self.new_password_entry.config(state="disabled")
            self.confirm_password_entry.config(state="disabled")
    
    def _get_selected_user(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently selected user data.
        
        Returns:
            User data dictionary or None if no user selected
        """
        selected_index = self.users_combobox.current()
        
        if selected_index >= 0:
            # Filter users again (excluding current admin)
            current_user = self.auth_manager.get_current_user()
            current_email = current_user.get('email') if current_user else None
            
            filtered_users = [
                user for user in self.users_data 
                if user.get('email') != current_email
            ]
            
            if selected_index < len(filtered_users):
                return filtered_users[selected_index]
        
        return None
    
    def _on_delete_user_click(self) -> None:
        """Handle delete user button click."""
        if self.is_processing:
            return
        
        selected_user = self._get_selected_user()
        if not selected_user:
            self.status_manager.show_error("Выберите пользователя для удаления")
            return
        
        # Confirm deletion
        user_name = safe_get(selected_user, 'name', 'Пользователь')
        user_email = safe_get(selected_user, 'email', '')
        
        confirmed = show_confirmation_dialog(
            "Подтверждение удаления",
            f"Вы действительно хотите удалить пользователя {user_name} ({user_email})?\n\nЭто действие необратимо!"
        )
        
        if confirmed:
            self._start_delete_user(selected_user)
    
    def _start_delete_user(self, user: Dict[str, Any]) -> None:
        """
        Start the delete user process in a separate thread.
        
        Args:
            user: User data to delete
        """
        self.is_processing = True
        
        # Disable UI elements
        self._set_ui_state(False, "Удаляем пользователя...")
        
        user_id = user.get('id')
        
        # Start delete in separate thread
        delete_thread = threading.Thread(
            target=self._perform_delete_user,
            args=(user_id, user.get('name', 'Пользователь')),
            daemon=True
        )
        delete_thread.start()
    
    def _perform_delete_user(self, user_id: int, user_name: str) -> None:
        """
        Perform the actual user deletion operation.
        
        Args:
            user_id: ID of the user to delete
            user_name: Name of the user for display purposes
        """
        try:
            success, error = self.session_manager.admin_delete_user(user_id)
            
            # Schedule UI update on main thread
            self.window.after(0, self._on_delete_user_complete, success, error, user_name)
            
        except Exception as e:
            error_msg = f"Неожиданная ошибка: {str(e)}"
            self.window.after(0, self._on_delete_user_complete, False, error_msg, user_name)
    
    def _on_delete_user_complete(self, success: bool, error: str, user_name: str) -> None:
        """
        Handle delete user completion on the main thread.
        
        Args:
            success: Whether deletion was successful
            error: Error message if deletion failed
            user_name: Name of the user for display purposes
        """
        self.is_processing = False
        
        # Re-enable UI elements
        self._set_ui_state(True, "")
        
        if success:
            self.status_manager.show_success(f"Пользователь {user_name} успешно удален")
            
            # Clear selection and reload users
            self.selected_user_var.set("")
            self._load_users()
            
            # Call data changed callback
            if self.on_data_changed:
                try:
                    self.on_data_changed()
                except Exception as e:
                    print(f"Error in data changed callback: {e}")
            
            show_success_message("Успех", f"Пользователь {user_name} успешно удален")
        else:
            self.status_manager.show_error(error)
    
    def _on_change_password_click(self) -> None:
        """Handle change password button click."""
        if self.is_processing:
            return
        
        selected_user = self._get_selected_user()
        if not selected_user:
            self.status_manager.show_error("Выберите пользователя для смены пароля")
            return
        
        # Validate passwords
        new_password = self.new_password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        # Validate new password
        is_valid, error = validate_required_field(new_password, "Новый пароль")
        if not is_valid:
            self.status_manager.show_error(error)
            return
        
        # Check minimum password length
        if len(new_password) < 4:
            self.status_manager.show_error("Пароль должен содержать не менее 4 символов")
            return
        
        # Validate password confirmation
        if new_password != confirm_password:
            self.status_manager.show_error("Пароли не совпадают")
            return
        
        # Confirm password change
        user_name = safe_get(selected_user, 'name', 'Пользователь')
        
        confirmed = show_confirmation_dialog(
            "Подтверждение смены пароля",
            f"Вы действительно хотите сменить пароль пользователя {user_name}?"
        )
        
        if confirmed:
            self._start_change_password(selected_user, new_password)
    
    def _start_change_password(self, user: Dict[str, Any], new_password: str) -> None:
        """
        Start the change password process in a separate thread.
        
        Args:
            user: User data
            new_password: New password to set
        """
        self.is_processing = True
        
        # Disable UI elements
        self._set_ui_state(False, "Меняем пароль...")
        
        user_id = user.get('id')
        
        # Start change password in separate thread
        change_thread = threading.Thread(
            target=self._perform_change_password,
            args=(user_id, new_password, user.get('name', 'Пользователь')),
            daemon=True
        )
        change_thread.start()
    
    def _perform_change_password(self, user_id: int, new_password: str, user_name: str) -> None:
        """
        Perform the actual password change operation.
        
        Args:
            user_id: ID of the user whose password to change
            new_password: New password to set
            user_name: Name of the user for display purposes
        """
        try:
            success, error = self.session_manager.admin_change_user_password(user_id, new_password)
            
            # Schedule UI update on main thread
            self.window.after(0, self._on_change_password_complete, success, error, user_name)
            
        except Exception as e:
            error_msg = f"Неожиданная ошибка: {str(e)}"
            self.window.after(0, self._on_change_password_complete, False, error_msg, user_name)
    
    def _on_change_password_complete(self, success: bool, error: str, user_name: str) -> None:
        """
        Handle change password completion on the main thread.
        
        Args:
            success: Whether password change was successful
            error: Error message if password change failed
            user_name: Name of the user for display purposes
        """
        self.is_processing = False
        
        # Re-enable UI elements
        self._set_ui_state(True, "")
        
        if success:
            self.status_manager.show_success(f"Пароль пользователя {user_name} успешно изменен")
            
            # Clear password fields
            clear_entry_fields(self.new_password_entry, self.confirm_password_entry)
            
            show_success_message("Успех", f"Пароль пользователя {user_name} успешно изменен")
        else:
            self.status_manager.show_error(error)
            # Clear password fields for security
            clear_entry_fields(self.new_password_entry, self.confirm_password_entry)
    
    def _set_ui_state(self, enabled: bool, status_text: str) -> None:
        """
        Set the UI state (enabled/disabled).
        
        Args:
            enabled: Whether UI should be enabled
            status_text: Status text to display
        """
        state = "normal" if enabled else "disabled"
        
        self.users_combobox.config(state="readonly" if enabled else "disabled")
        self.delete_button.config(state=state)
        self.change_password_button.config(state=state)
        self.new_password_entry.config(state=state)
        self.confirm_password_entry.config(state=state)
        self.close_button.config(state=state)
        
        if status_text:
            self.status_manager.show_info(status_text)
    
    def _on_close_click(self) -> None:
        """Handle close button click."""
        self._close_window()
    
    def _close_window(self) -> None:
        """Close the admin panel window."""
        # Clear password fields for security
        clear_entry_fields(self.new_password_entry, self.confirm_password_entry)
        
        try:
            self.window.destroy()
        except tk.TclError:
            pass  # Window already destroyed
    
    def destroy(self) -> None:
        """Destroy the admin panel window."""
        # Clear password fields for security
        clear_entry_fields(self.new_password_entry, self.confirm_password_entry)
        try:
            self.window.destroy()
        except tk.TclError:
            pass  # Window already destroyed

    def is_visible(self) -> bool:
        """
        Check if the admin panel window is visible.
        
        Returns:
            True if window is visible, False otherwise
        """
        try:
            return self.window.winfo_viewable()
        except tk.TclError:
            return False

    def show(self) -> None:
        """Show the admin panel window."""
        # Clear password fields when showing
        clear_entry_fields(self.new_password_entry, self.confirm_password_entry)
        self.status_manager.clear()
        
        self.window.deiconify()
        self.window.lift()
    
    def hide(self) -> None:
        """Hide the admin panel window."""
        # Clear password fields for security
        clear_entry_fields(self.new_password_entry, self.confirm_password_entry)
        self.window.withdraw()
    
    def is_visible(self) -> bool:
        """
        Check if the admin panel window is visible.
        
        Returns:
            True if window is visible, False otherwise
        """
        try:
            return self.window.winfo_viewable()
        except tk.TclError:
            return False