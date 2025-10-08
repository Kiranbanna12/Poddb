"""
Validation utilities for authentication
"""
import re
from typing import Dict, List, Optional

def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Validate email format
    Returns: (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 255:
        return False, "Email is too long"
    
    return True, None

def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Validate username
    Returns: (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 20:
        return False, "Username must be at most 20 characters"
    
    # Allow alphanumeric and underscore only
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, None

def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if len(password) > 128:
        return False, "Password is too long"
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None

def get_password_strength(password: str) -> str:
    """
    Calculate password strength
    Returns: 'weak', 'medium', or 'strong'
    """
    if not password:
        return 'weak'
    
    score = 0
    
    # Length
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    
    # Character types
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    if score <= 3:
        return 'weak'
    elif score <= 5:
        return 'medium'
    else:
        return 'strong'

def validate_full_name(full_name: Optional[str]) -> tuple[bool, Optional[str]]:
    """
    Validate full name
    Returns: (is_valid, error_message)
    """
    if full_name and len(full_name) > 100:
        return False, "Full name is too long"
    
    return True, None

def sanitize_input(input_str: str, max_length: int = 255) -> str:
    """
    Sanitize user input by removing potentially harmful characters
    """
    if not input_str:
        return ""
    
    # Remove null bytes
    sanitized = input_str.replace('\x00', '')
    
    # Trim to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()
    
    return sanitized

def validate_role(role: str) -> tuple[bool, Optional[str]]:
    """
    Validate user role
    Returns: (is_valid, error_message)
    """
    valid_roles = ['user', 'moderator', 'admin']
    
    if role not in valid_roles:
        return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
    
    return True, None
