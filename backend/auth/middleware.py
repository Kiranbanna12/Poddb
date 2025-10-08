"""
Middleware for authentication and authorization
"""
from fastapi import Request, HTTPException, status
from typing import Optional, Dict
import time
from database.auth_queries import get_session, get_recent_failed_attempts_by_ip

# Rate limiting storage (in-memory for MVP, use Redis in production)
rate_limit_storage: Dict[str, list] = {}

def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def get_user_agent(request: Request) -> str:
    """Get user agent from request"""
    return request.headers.get("User-Agent", "unknown")

async def get_current_user(request: Request) -> Optional[Dict]:
    """
    Get current authenticated user from session token
    Returns None if not authenticated
    """
    # Try to get session token from cookie
    session_token = request.cookies.get("session_token")
    
    # If not in cookie, try Authorization header
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    
    if not session_token:
        return None
    
    # Get session from database
    session = get_session(session_token)
    
    if not session:
        return None
    
    # Check if user is active and not banned
    if not session.get('is_active') or session.get('is_banned'):
        return None
    
    return session

async def require_auth(request: Request) -> Dict:
    """
    Require authentication
    Raises HTTPException if not authenticated
    """
    user = await get_current_user(request)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def require_role(request: Request, allowed_roles: list) -> Dict:
    """
    Require specific role(s)
    Raises HTTPException if not authorized
    """
    user = await require_auth(request)
    
    if user.get('role') not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return user

async def require_admin(request: Request) -> Dict:
    """Require admin role"""
    return await require_role(request, ['admin'])

async def require_moderator(request: Request) -> Dict:
    """Require moderator or admin role"""
    return await require_role(request, ['moderator', 'admin'])

def check_rate_limit(identifier: str, max_requests: int, window_seconds: int) -> tuple[bool, int]:
    """
    Check rate limit for an identifier (IP address, email, etc.)
    Returns: (is_allowed, retry_after_seconds)
    """
    current_time = int(time.time())
    
    # Initialize if not exists
    if identifier not in rate_limit_storage:
        rate_limit_storage[identifier] = []
    
    # Remove old timestamps outside the window
    rate_limit_storage[identifier] = [
        timestamp for timestamp in rate_limit_storage[identifier]
        if current_time - timestamp < window_seconds
    ]
    
    # Check if limit exceeded
    if len(rate_limit_storage[identifier]) >= max_requests:
        # Calculate retry_after
        oldest_timestamp = rate_limit_storage[identifier][0]
        retry_after = window_seconds - (current_time - oldest_timestamp)
        return False, retry_after
    
    # Add current timestamp
    rate_limit_storage[identifier].append(current_time)
    
    return True, 0

def check_login_rate_limit(identifier: str, ip_address: str) -> tuple[bool, str]:
    """
    Check login rate limits
    Returns: (is_allowed, error_message)
    """
    # Check IP-based rate limit (max 10 attempts per 15 minutes)
    allowed, retry_after = check_rate_limit(f"login_ip_{ip_address}", 10, 900)
    if not allowed:
        return False, f"Too many login attempts from this IP. Try again in {retry_after} seconds"
    
    # Check identifier-based rate limit (max 5 attempts per 15 minutes)
    allowed, retry_after = check_rate_limit(f"login_id_{identifier}", 5, 900)
    if not allowed:
        return False, f"Too many failed login attempts. Try again in {retry_after} seconds"
    
    # Check database for failed attempts
    failed_count = get_recent_failed_attempts_by_ip(ip_address, 15)
    if failed_count >= 10:
        return False, "Too many failed login attempts from this IP. Please try again later"
    
    return True, ""

def check_registration_rate_limit(ip_address: str) -> tuple[bool, str]:
    """
    Check registration rate limit
    Returns: (is_allowed, error_message)
    """
    # Max 3 registrations per IP per hour
    allowed, retry_after = check_rate_limit(f"register_{ip_address}", 3, 3600)
    if not allowed:
        return False, f"Too many registration attempts. Try again in {retry_after // 60} minutes"
    
    return True, ""

def check_password_reset_rate_limit(email: str) -> tuple[bool, str]:
    """
    Check password reset rate limit
    Returns: (is_allowed, error_message)
    """
    # Max 3 password reset requests per email per hour
    allowed, retry_after = check_rate_limit(f"reset_{email}", 3, 3600)
    if not allowed:
        return False, f"Too many password reset requests. Try again in {retry_after // 60} minutes"
    
    return True, ""

def check_email_verification_rate_limit(email: str) -> tuple[bool, str]:
    """
    Check email verification resend rate limit
    Returns: (is_allowed, error_message)
    """
    # Max 3 verification emails per hour
    allowed, retry_after = check_rate_limit(f"verify_{email}", 3, 3600)
    if not allowed:
        return False, f"Too many verification emails sent. Try again in {retry_after // 60} minutes"
    
    return True, ""

def check_api_rate_limit(ip_address: str) -> tuple[bool, str]:
    """
    Check general API rate limit
    Returns: (is_allowed, error_message)
    """
    # Max 100 requests per minute
    allowed, retry_after = check_rate_limit(f"api_{ip_address}", 100, 60)
    if not allowed:
        return False, f"Rate limit exceeded. Try again in {retry_after} seconds"
    
    return True, ""

def cleanup_rate_limit_storage():
    """Clean up old entries from rate limit storage"""
    current_time = int(time.time())
    
    for identifier in list(rate_limit_storage.keys()):
        # Remove entries older than 1 hour
        rate_limit_storage[identifier] = [
            timestamp for timestamp in rate_limit_storage[identifier]
            if current_time - timestamp < 3600
        ]
        
        # Remove empty lists
        if not rate_limit_storage[identifier]:
            del rate_limit_storage[identifier]
