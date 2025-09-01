"""
Main Dashboard window for displaying users and navigation.

This module provides the main interface after successful login,
showing the list of users and providing navigation to other features.
"""

import tkinter as tk
from tkinter import ttk
import threading
from typing import Callable, Optional, List, Dict, Any
from ..components.auth_manager import AuthenticationManager
from ..components.session_manager import UserSessionManager
from ..utils.helpers import (
    center_window, StatusLabel, show_error_message, 
    show_success_message, format_datetime, safe_get
)


class MainDashboard:
    """
    Main dashboard window showing user list and navigation options.
    
    Provides functionality to view users, refresh data, and navigate
    to profile editing, password changing, and admin features.
    """
    
    def __init__(
        self,
        auth_manager: AuthenticationManager,
        session_manager: UserSessionManager,
        on_edit_profile: Callable[[], None],
        on_change_password: Callable[[], None],
        on_admin_panel: Callable[[], None],
        on_logout: Callable[[], None]
    ):
        """
        Initialize the main dashboard.
        
        Args:
            auth_manager: Authentication manager instance
            session_manager: Session manager instance
            on_edit_profile: Callback for edit profile action
            on_change_password: Callback for change password action
            on_admin_panel: Callback for admin panel action
            on_logout: Callback for logout action
        """
        self.auth_manager = auth_manager
        self.session_manager = session_manager
        self.on_edit_profile = on_edit_profile
        self.on_change_password = on_change_password
        self.on_admin_panel = on_admin_panel
        self.on_logout = on_logout
        
        # Create the window
        self.window = tk.Toplevel()
        self.window.title("Управление пользователями")
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # UI elements
        self.users_tree = None
        self.refresh_button = None
        self.edit_profile_button = None
        self.change_password_button = None
        self.admin_panel_button = None
        self.logout_button = None
        self.status_label = None
        self.status_manager = None
        self.user_info_label = None
        self.content_frame = None
        self.admin_buttons_frame = None
        self.selected_user_id = None
        
        # State
        self.is_loading = False
        
        self._setup_ui()
        self._center_window()
        self._update_ui_state()
        
        # Load users only if admin
        if self.auth_manager.is_admin():
            self._refresh_users()
    
    def _setup_ui(self) -> None:
        """Set up the user interface elements."""
        # Main frame with padding
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # User info frame
        self._setup_user_info_frame(main_frame)
        
        # Buttons frame
        self._setup_buttons_frame(main_frame)
        
        # Content frame - will show different content based on user role
        self._setup_content_frame(main_frame)
        
        # Status frame
        self._setup_status_frame(main_frame)
    
    def _setup_user_info_frame(self, parent: ttk.Frame) -> None:
        """Set up the user information frame."""
        info_frame = ttk.LabelFrame(parent, text="Текущий пользователь", padding="5")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.user_info_label = ttk.Label(info_frame, text="")
        self.user_info_label.grid(row=0, column=0, sticky=tk.W)
    
    def _setup_buttons_frame(self, parent: ttk.Frame) -> None:
        """Set up the buttons frame."""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Refresh button
        self.refresh_button = ttk.Button(
            buttons_frame,
            text="Обновить список",
            command=self._on_refresh_click
        )
        self.refresh_button.grid(row=0, column=0, padx=(0, 5))
        
        # Edit profile button
        self.edit_profile_button = ttk.Button(
            buttons_frame,
            text="Редактировать профиль",
            command=self._on_edit_profile_click
        )
        self.edit_profile_button.grid(row=0, column=1, padx=5)
        
        # Change password button
        self.change_password_button = ttk.Button(
            buttons_frame,
            text="Сменить пароль",
            command=self._on_change_password_click
        )
        self.change_password_button.grid(row=0, column=2, padx=5)
        
        # Logout button
        self.logout_button = ttk.Button(
            buttons_frame,
            text="Выйти",
            command=self._on_logout_click
        )
        self.logout_button.grid(row=0, column=3, padx=(5, 0))
    
    def _setup_content_frame(self, parent: ttk.Frame) -> None:
        """Set up the content frame that changes based on user role."""
        self.content_frame = ttk.Frame(parent)
        self.content_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Will be populated based on user role in _update_ui_state
    
    def _setup_users_table_frame(self, parent: ttk.Frame) -> None:
        """Set up the users table frame."""
        table_frame = ttk.LabelFrame(parent, text="Список пользователей", padding="5")
        table_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Configure table frame grid
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Create treeview with scrollbar
        tree_frame = ttk.Frame(table_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Define columns
        columns = ("ID", "Имя", "Email", "Телефон", "Создан")
        
        self.users_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=12
        )
        
        # Configure column headings and widths
        self.users_tree.heading("ID", text="ID")
        self.users_tree.heading("Имя", text="Имя")
        self.users_tree.heading("Email", text="Email")
        self.users_tree.heading("Телефон", text="Телефон")
        self.users_tree.heading("Создан", text="Создан")
        
        self.users_tree.column("ID", width=50, minwidth=50)
        self.users_tree.column("Имя", width=150, minwidth=100)
        self.users_tree.column("Email", width=200, minwidth=150)
        self.users_tree.column("Телефон", width=120, minwidth=100)
        self.users_tree.column("Создан", width=130, minwidth=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection and double-click events
        self.users_tree.bind('<<TreeviewSelect>>', self._on_user_selected)
        self.users_tree.bind('<Double-1>', self._on_user_double_click)
        
        # Grid the treeview and scrollbar
        self.users_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Admin buttons frame (for selected user actions)
        self._setup_admin_buttons_frame(table_frame)
    
    def _setup_admin_buttons_frame(self, parent: ttk.Frame) -> None:
        """Set up the admin buttons frame for user actions."""
        self.admin_buttons_frame = ttk.Frame(parent)
        self.admin_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Edit selected user button
        self.edit_selected_button = ttk.Button(
            self.admin_buttons_frame,
            text="Редактировать выбранного пользователя",
            command=self._on_edit_selected_user_click,
            state="disabled"
        )
        self.edit_selected_button.grid(row=0, column=0, padx=(0, 10))
        
        # Delete selected user button
        self.delete_selected_button = ttk.Button(
            self.admin_buttons_frame,
            text="Удалить выбранного пользователя",
            command=self._on_delete_selected_user_click,
            state="disabled"
        )
        self.delete_selected_button.grid(row=0, column=1, padx=(0, 10))
        
        # Change password for selected user button
        self.change_user_password_button = ttk.Button(
            self.admin_buttons_frame,
            text="Сменить пароль пользователя",
            command=self._on_change_user_password_click,
            state="disabled"
        )
        self.change_user_password_button.grid(row=0, column=2)
    
    def _setup_status_frame(self, parent: ttk.Frame) -> None:
        """Set up the status frame."""
        self.status_label = ttk.Label(parent, text="")
        self.status_label.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        self.status_manager = StatusLabel(self.status_label)
    
    def _center_window(self) -> None:
        """Center the window on the screen."""
        center_window(self.window, 800, 600)
    
    def _setup_user_profile_display(self, parent: ttk.Frame) -> None:
        """Set up the user profile display for regular users."""
        # Clear content frame
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Profile display frame
        profile_frame = ttk.LabelFrame(parent, text="Мой профиль", padding="20")
        profile_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=20)
        profile_frame.columnconfigure(1, weight=1)
        
        current_user = self.auth_manager.get_current_user()
        if current_user:
            # Profile icon
            profile_icon = ttk.Label(profile_frame, text="👤", font=("Arial", 48))
            profile_icon.grid(row=0, column=0, rowspan=4, padx=(0, 20), sticky=tk.N)
            
            # User information
            ttk.Label(profile_frame, text="Имя:", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
            ttk.Label(profile_frame, text=safe_get(current_user, 'name', 'N/A'), font=("Arial", 12)).grid(row=0, column=2, sticky=tk.W, padx=(10, 0), pady=(0, 10))
            
            ttk.Label(profile_frame, text="Email:", font=("Arial", 10, "bold")).grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
            ttk.Label(profile_frame, text=safe_get(current_user, 'email', 'N/A'), font=("Arial", 12)).grid(row=1, column=2, sticky=tk.W, padx=(10, 0), pady=(0, 10))
            
            ttk.Label(profile_frame, text="Телефон:", font=("Arial", 10, "bold")).grid(row=2, column=1, sticky=tk.W, pady=(0, 10))
            phone = safe_get(current_user, 'phone', '')
            ttk.Label(profile_frame, text=phone if phone else 'Не указан', font=("Arial", 12)).grid(row=2, column=2, sticky=tk.W, padx=(10, 0), pady=(0, 10))
            
            ttk.Label(profile_frame, text="Зарегистрирован:", font=("Arial", 10, "bold")).grid(row=3, column=1, sticky=tk.W)
            created_at = format_datetime(safe_get(current_user, 'created_at', ''))
            ttk.Label(profile_frame, text=created_at, font=("Arial", 12)).grid(row=3, column=2, sticky=tk.W, padx=(10, 0))
    
    def _update_ui_state(self) -> None:
        """Update UI state based on current user and authentication."""
        current_user = self.auth_manager.get_current_user()
        
        if current_user:
            # Update user info
            user_name = safe_get(current_user, 'name', 'Пользователь')
            user_email = safe_get(current_user, 'email', '')
            self.user_info_label.config(text=f"{user_name} ({user_email})")
            
            # Check if user is admin
            is_admin = self.auth_manager.is_admin()
            
            if is_admin:
                # Admin interface - show users table
                self._setup_users_table_frame(self.content_frame)
                self._refresh_users()
                # Show admin buttons frame
                if hasattr(self, 'admin_buttons_frame') and self.admin_buttons_frame:
                    self.admin_buttons_frame.grid()
            else:
                # Regular user interface - show profile
                self._setup_user_profile_display(self.content_frame)
                # Hide admin buttons frame if it exists
                if hasattr(self, 'admin_buttons_frame') and self.admin_buttons_frame:
                    self.admin_buttons_frame.grid_remove()
        else:
            self.user_info_label.config(text="Не авторизован")
    
    def _on_refresh_click(self) -> None:
        """Handle refresh button click."""
        self._refresh_users(force_refresh=True)
    
    def _refresh_users(self, force_refresh: bool = False) -> None:
        """Refresh the users list.
        
        Args:
            force_refresh: Whether to force refresh from server
        """
        if self.is_loading:
            return
        
        # Only refresh if admin and status manager is available
        if not self.auth_manager.is_admin() or not self.status_manager:
            return
        
        self.is_loading = True
        
        # Update UI state
        if self.refresh_button:
            self.refresh_button.config(state="disabled", text="Загрузка...")
        self.status_manager.show_info("Загружаем список пользователей...")
        
        # Start loading in separate thread
        load_thread = threading.Thread(
            target=self._perform_users_load,
            args=(force_refresh,),
            daemon=True
        )
        load_thread.start()
    
    def _perform_users_load(self, force_refresh: bool) -> None:
        """
        Perform the actual users loading operation.
        
        Args:
            force_refresh: Whether to force refresh from server
        """
        try:
            success, users, error = self.session_manager.get_users(force_refresh)
            
            # Schedule UI update on main thread
            self.window.after(0, self._on_users_load_complete, success, users, error)
            
        except Exception as e:
            error_msg = f"Ошибка при загрузке: {str(e)}"
            self.window.after(0, self._on_users_load_complete, False, None, error_msg)
    
    def _on_users_load_complete(
        self, 
        success: bool, 
        users: Optional[List[Dict[str, Any]]], 
        error: str
    ) -> None:
        """
        Handle users loading completion on the main thread.
        
        Args:
            success: Whether loading was successful
            users: List of users if successful
            error: Error message if loading failed
        """
        self.is_loading = False
        
        # Re-enable UI
        if self.refresh_button:
            self.refresh_button.config(state="normal", text="Обновить список")
        
        if success and users:
            self._populate_users_table(users)
            self.status_manager.show_success(f"Загружено {len(users)} пользователей")
        else:
            self.status_manager.show_error(error or "Ошибка при загрузке пользователей")
    
    def _populate_users_table(self, users: List[Dict[str, Any]]) -> None:
        """
        Populate the users table with data.
        
        Args:
            users: List of user dictionaries
        """
        # Clear existing data
        if self.users_tree:
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
        
        # Add users to the table
        if self.users_tree:
            for user in users:
                user_id = safe_get(user, 'id', 'N/A')
                name = safe_get(user, 'name', 'N/A')
                email = safe_get(user, 'email', 'N/A')
                phone = safe_get(user, 'phone', 'N/A')
                created_at = format_datetime(safe_get(user, 'created_at', ''))
                
                self.users_tree.insert(
                    '',
                    'end',
                    values=(user_id, name, email, phone, created_at)
                )
    
    def _on_user_selected(self, event) -> None:
        """Handle user selection in the tree view."""
        if not self.auth_manager.is_admin():
            return
        
        selection = self.users_tree.selection()
        if selection:
            # Get selected user data
            item = self.users_tree.item(selection[0])
            user_id = item['values'][0] if item['values'] else None
            
            if user_id:
                self.selected_user_id = user_id
                # Enable admin buttons
                if hasattr(self, 'edit_selected_button'):
                    self.edit_selected_button.config(state="normal")
                if hasattr(self, 'delete_selected_button'):
                    self.delete_selected_button.config(state="normal")
                if hasattr(self, 'change_user_password_button'):
                    self.change_user_password_button.config(state="normal")
        else:
            self.selected_user_id = None
            # Disable admin buttons
            if hasattr(self, 'edit_selected_button'):
                self.edit_selected_button.config(state="disabled")
            if hasattr(self, 'delete_selected_button'):
                self.delete_selected_button.config(state="disabled")
            if hasattr(self, 'change_user_password_button'):
                self.change_user_password_button.config(state="disabled")
    
    def _on_user_double_click(self, event) -> None:
        """Handle user double-click in the tree view."""
        if self.auth_manager.is_admin() and self.selected_user_id:
            self._on_edit_selected_user_click()
    
    def _on_edit_selected_user_click(self) -> None:
        """Handle edit selected user button click."""
        if not self.selected_user_id:
            return
        
        # Find user data
        selected_user = None
        success, users, error = self.session_manager.get_users()
        if success:
            for user in users:
                if user.get('id') == self.selected_user_id:
                    selected_user = user
                    break
        
        if selected_user:
            # Create admin profile editor for the selected user
            self._create_admin_profile_editor(selected_user)
        else:
            show_error_message("Ошибка", "Не удалось найти данные пользователя")
    
    def _on_delete_selected_user_click(self) -> None:
        """Handle delete selected user button click."""
        if not self.selected_user_id:
            return
        
        # Find user data for confirmation
        selected_user = None
        success, users, error = self.session_manager.get_users()
        if success:
            for user in users:
                if user.get('id') == self.selected_user_id:
                    selected_user = user
                    break
        
        if selected_user:
            user_name = safe_get(selected_user, 'name', 'Пользователь')
            user_email = safe_get(selected_user, 'email', '')
            
            from ..utils.helpers import show_confirmation_dialog
            confirmed = show_confirmation_dialog(
                "Подтверждение удаления",
                f"Вы действительно хотите удалить пользователя {user_name} ({user_email})?\n\nЭто действие необратимо!"
            )
            
            if confirmed:
                self._perform_user_deletion(self.selected_user_id, user_name)
    
    def _on_change_user_password_click(self) -> None:
        """Handle change user password button click."""
        if not self.selected_user_id:
            return
        
        # Find user data
        selected_user = None
        success, users, error = self.session_manager.get_users()
        if success:
            for user in users:
                if user.get('id') == self.selected_user_id:
                    selected_user = user
                    break
        
        if selected_user:
            self._create_admin_password_changer(selected_user)
        else:
            show_error_message("Ошибка", "Не удалось найти данные пользователя")
    
    def _perform_user_deletion(self, user_id: int, user_name: str) -> None:
        """Perform user deletion operation."""
        def delete_user():
            try:
                success, error = self.session_manager.admin_delete_user(user_id)
                self.window.after(0, self._on_user_deletion_complete, success, error, user_name)
            except Exception as e:
                self.window.after(0, self._on_user_deletion_complete, False, str(e), user_name)
        
        self.status_manager.show_info(f"Удаляем пользователя {user_name}...")
        
        delete_thread = threading.Thread(target=delete_user, daemon=True)
        delete_thread.start()
    
    def _on_user_deletion_complete(self, success: bool, error: str, user_name: str) -> None:
        """Handle user deletion completion."""
        if success:
            self.status_manager.show_success(f"Пользователь {user_name} успешно удален")
            self.selected_user_id = None
            self._refresh_users(force_refresh=True)
            show_success_message("Успех", f"Пользователь {user_name} успешно удален")
        else:
            self.status_manager.show_error(error)
    
    def _create_admin_profile_editor(self, user_data: Dict[str, Any]) -> None:
        """Create admin profile editor for selected user."""
        # Import here to avoid circular imports
        from .admin_profile_editor import AdminProfileEditor
        
        try:
            admin_editor = AdminProfileEditor(
                user_data=user_data,
                session_manager=self.session_manager,
                on_profile_updated=lambda: self._refresh_users(force_refresh=True)
            )
            admin_editor.show()
        except Exception as e:
            show_error_message("Ошибка", f"Не удалось открыть редактор профиля: {str(e)}")
    
    def _create_admin_password_changer(self, user_data: Dict[str, Any]) -> None:
        """Create admin password changer for selected user."""
        # Import here to avoid circular imports
        from .admin_password_changer import AdminPasswordChanger
        
        try:
            password_changer = AdminPasswordChanger(
                user_data=user_data,
                session_manager=self.session_manager
            )
            password_changer.show()
        except Exception as e:
            show_error_message("Ошибка", f"Не удалось открыть смену пароля: {str(e)}")
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
        """Show the dashboard window."""
        self.window.deiconify()
        self.window.lift()
        self._update_ui_state()
    
    def hide(self) -> None:
        """Hide the dashboard window."""
        self.window.withdraw()
    
    def destroy(self) -> None:
        """Destroy the dashboard window."""
        self.window.destroy()
    
    def refresh_data(self) -> None:
        """Refresh dashboard data."""
        self._update_ui_state()
        self._refresh_users(force_refresh=True)
    
    def is_visible(self) -> bool:
        """
        Check if the dashboard window is visible.
        
        Returns:
            True if window is visible, False otherwise
        """
        try:
            return self.window.winfo_viewable()
        except tk.TclError:
            return False