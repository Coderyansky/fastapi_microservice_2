"""
Validation utilities for the GUI application.

This module provides various validation functions for user inputs
including email validation, password validation, and required field checks.
"""

import re
from typing import Optional, Tuple


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    if not email.strip():
        return False, "Email cannot be empty"
    
    # Basic email pattern validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email.strip()):
        return False, "Invalid email format"
    
    return True, ""


def validate_required_field(value: str, field_name: str) -> Tuple[bool, str]:
    """
    Validate that a required field has a value.
    
    Args:
        value: Field value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, f"{field_name} is required"
    
    return True, ""


def validate_password_match(password: str, repeat_password: str) -> Tuple[bool, str]:
    """
    Validate that password and repeat password match.
    
    Args:
        password: Original password
        repeat_password: Repeated password for confirmation
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if not repeat_password:
        return False, "Please repeat the password"
    
    if password != repeat_password:
        return False, "Passwords do not match"
    
    return True, ""


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number format (optional field).
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return True, ""  # Phone is optional
    
    if not phone.strip():
        return True, ""  # Empty phone is valid
    
    # Basic phone validation - allows digits, spaces, dashes, parentheses, plus
    phone_pattern = r'^[\+]?[\d\s\-\(\)]+$'
    if not re.match(phone_pattern, phone.strip()):
        return False, "Invalid phone number format"
    
    return True, ""


def validate_name(name: str) -> Tuple[bool, str]:
    """
    Validate name field.
    
    Args:
        name: Name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Name is required"
    
    # Name should contain only letters, spaces, and basic punctuation
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long"
    
    return True, ""


class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


def validate_form_data(data: dict, required_fields: list = None) -> Optional[str]:
    """
    Validate form data with multiple fields.
    
    Args:
        data: Dictionary of field names to values
        required_fields: List of required field names
        
    Returns:
        Error message if validation fails, None if all validations pass
    """
    required_fields = required_fields or []
    
    # Check required fields
    for field in required_fields:
        if field not in data or not data[field] or not str(data[field]).strip():
            return f"{field.capitalize()} is required"
    
    # Validate email if present
    if 'email' in data:
        is_valid, error = validate_email(data['email'])
        if not is_valid:
            return error
    
    # Validate name if present
    if 'name' in data:
        is_valid, error = validate_name(data['name'])
        if not is_valid:
            return error
    
    # Validate phone if present
    if 'phone' in data:
        is_valid, error = validate_phone(data['phone'])
        if not is_valid:
            return error
    
    # Validate password match if both passwords are present
    if 'new_password' in data and 'new_password_repeat' in data:
        is_valid, error = validate_password_match(
            data['new_password'], 
            data['new_password_repeat']
        )
        if not is_valid:
            return error
    
    return None