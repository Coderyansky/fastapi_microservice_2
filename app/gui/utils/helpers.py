"""
Helper utilities for the GUI application.

This module provides various helper functions for GUI operations,
formatting, and common tasks.
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from typing import Optional, Any


def center_window(window: tk.Toplevel, width: int, height: int) -> None:
    """
    Center a window on the screen.
    
    Args:
        window: The window to center
        width: Window width
        height: Window height
    """
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate position coordinates
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Set window geometry
    window.geometry(f"{width}x{height}+{x}+{y}")


def show_error_message(title: str, message: str, parent: tk.Widget = None) -> None:
    """
    Show an error message dialog.
    
    Args:
        title: Dialog title
        message: Error message
        parent: Parent widget (optional)
    """
    messagebox.showerror(title, message, parent=parent)


def show_success_message(title: str, message: str, parent: tk.Widget = None) -> None:
    """
    Show a success message dialog.
    
    Args:
        title: Dialog title
        message: Success message
        parent: Parent widget (optional)
    """
    messagebox.showinfo(title, message, parent=parent)


def show_confirmation_dialog(title: str, message: str, parent: tk.Widget = None) -> bool:
    """
    Show a confirmation dialog.
    
    Args:
        title: Dialog title
        message: Confirmation message
        parent: Parent widget (optional)
        
    Returns:
        True if user confirmed, False otherwise
    """
    result = messagebox.askyesno(title, message, parent=parent)
    return result


def format_datetime(dt_str: str) -> str:
    """
    Format datetime string for display.
    
    Args:
        dt_str: ISO format datetime string
        
    Returns:
        Formatted datetime string
    """
    try:
        # Parse ISO format datetime
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        # Format for display
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, AttributeError):
        return dt_str or "N/A"


def safe_get(dictionary: dict, key: str, default: Any = "N/A") -> Any:
    """
    Safely get a value from dictionary with default.
    
    Args:
        dictionary: Dictionary to get value from
        key: Key to lookup
        default: Default value if key not found
        
    Returns:
        Value from dictionary or default
    """
    return dictionary.get(key, default)


def clear_entry_fields(*entries: tk.Entry) -> None:
    """
    Clear multiple entry fields.
    
    Args:
        *entries: Variable number of Entry widgets to clear
    """
    for entry in entries:
        if isinstance(entry, tk.Entry):
            entry.delete(0, tk.END)


def set_entry_text(entry: tk.Entry, text: str) -> None:
    """
    Set text in an Entry widget.
    
    Args:
        entry: Entry widget
        text: Text to set
    """
    entry.delete(0, tk.END)
    entry.insert(0, text or "")


def configure_entry_state(entry: tk.Entry, enabled: bool = True) -> None:
    """
    Configure the state of an Entry widget.
    
    Args:
        entry: Entry widget
        enabled: Whether the entry should be enabled
    """
    state = tk.NORMAL if enabled else tk.DISABLED
    entry.configure(state=state)


def bind_enter_key(widget: tk.Widget, callback) -> None:
    """
    Bind the Enter key to a callback function.
    
    Args:
        widget: Widget to bind the key to
        callback: Function to call when Enter is pressed
    """
    widget.bind('<Return>', lambda event: callback())


class StatusLabel:
    """
    A utility class for managing status messages in a label.
    """
    
    def __init__(self, label: tk.Label):
        self.label = label
        try:
            self.default_fg = label.cget('foreground')
        except tk.TclError:
            # For ttk widgets, use 'foreground' style
            self.default_fg = 'black'
    
    def show_error(self, message: str) -> None:
        """Show an error message."""
        try:
            self.label.config(text=message, foreground='red')
        except tk.TclError:
            # Fallback for ttk widgets
            self.label.config(text=message)
    
    def show_success(self, message: str) -> None:
        """Show a success message."""
        try:
            self.label.config(text=message, foreground='green')
        except tk.TclError:
            # Fallback for ttk widgets
            self.label.config(text=message)
    
    def show_info(self, message: str) -> None:
        """Show an info message."""
        try:
            self.label.config(text=message, foreground=self.default_fg)
        except tk.TclError:
            # Fallback for ttk widgets
            self.label.config(text=message)
    
    def clear(self) -> None:
        """Clear the status message."""
        try:
            self.label.config(text="", foreground=self.default_fg)
        except tk.TclError:
            # Fallback for ttk widgets
            self.label.config(text="")