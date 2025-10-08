"""
Authentication API routes
"""
from fastapi import APIRouter, HTTPException, status, Request, Response, Depends
from typing import Optional
import time

# Import models
from models.auth import (
    UserRegister, UserLogin, UserResponse, ChangePasswordRequest,
    ChangeEmailRequest, UpdateProfileRequest, ForgotPasswordRequest,
    ResetPasswordRequest, VerifyEmailRequest, ResendVerificationRequest,
    SessionResponse, CheckAvailabilityResponse, PasswordStrengthResponse
)

# Import database queries
from database.auth_queries import (
    create_user, get_user_by_email, get_user_by_username, get_user_by_id,
    check_username_exists, check_email_exists, update_user_email_verified,
    update_user_last_login, update_user_password, update_user_profile,
    update_user_email, soft_delete_user, create_session, get_session,
    delete_session, delete_user_sessions, get_user_sessions,
    create_verification_token, get_verification_token, mark_token_used,
    delete_user_tokens, log_login_attempt, log_user_activity
)

# Import auth utilities
from auth.password import hash_password, verify_password
from auth.validators import (
    validate_email, validate_username, validate_password,
    get_password_strength, sanitize_input
)
from auth.middleware import (
    get_current_user, require_auth, get_client_ip, get_user_agent,
    check_login_rate_limit, check_registration_rate_limit,
    check_password_reset_rate_limit, check_email_verification_rate_limit
)

# Import email service
from services.email_service import (
    send_verification_email, send_password_reset_email,
    send_password_changed_email, send_email_change_verification
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# REGISTRATION
# ============================================================================

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, request: Request):
    """Register a new user"""
    
    # Get client info
    ip_address = get_client_ip(request)
    
    # Check rate limit
    allowed, error_msg = check_registration_rate_limit(ip_address)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=error_msg)
    
    # Sanitize inputs
    username = sanitize_input(user_data.username, 20)
    email = user_data.email.lower().strip()
    
    # Validate username
    is_valid, error = validate_username(username)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    # Validate email
    is_valid, error = validate_email(email)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    # Validate password
    is_valid, error = validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    # Check if username exists
    if check_username_exists(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Check if email exists
    if check_email_exists(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = hash_password(user_data.password)
    
    # Create user
    try:
        user_id = create_user(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=sanitize_input(user_data.full_name, 100) if user_data.full_name else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Create verification token
    verification_token = create_verification_token(email, 'email_verification', 24)
    
    # Send verification email
    try:
        send_verification_email(email, username, verification_token)
    except Exception as e:
        print(f"Failed to send verification email: {e}")
    
    # Log activity
    log_user_activity(user_id, 'register', 'User registered', ip_address, get_user_agent(request))
    
    return {
        "success": True,
        "message": "Account created successfully! Please check your email to verify your account.",
        "user_id": user_id
    }


# ============================================================================
# LOGIN
# ============================================================================

@router.post("/login", response_model=dict)
async def login(credentials: UserLogin, request: Request, response: Response):
    """Login user"""
    
    # Get client info
    ip_address = get_client_ip(request)
    identifier = credentials.identifier.strip()
    
    # Check rate limit
    allowed, error_msg = check_login_rate_limit(identifier, ip_address)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=error_msg)
    
    # Find user by email or username
    user = None
    if '@' in identifier:
        user = get_user_by_email(identifier.lower())
    else:
        user = get_user_by_username(identifier)
    
    # Check if user exists
    if not user:
        log_login_attempt(identifier, ip_address, False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user['password_hash']):
        log_login_attempt(identifier, ip_address, False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password"
        )
    
    # Check if user is active
    if not user['is_active']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Check if user is banned
    if user['is_banned']:
        reason = user.get('ban_reason', 'No reason provided')
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is banned. Reason: {reason}"
        )
    
    # Check if email is verified (warning only)
    email_verified = user['email_verified']
    
    # Create session
    expires_hours = 720 if credentials.remember_me else 24  # 30 days or 24 hours
    device_info = {
        'device': 'Web',
        'ip': ip_address,
        'user_agent': get_user_agent(request)
    }
    session_token = create_session(user['id'], expires_hours, device_info)
    
    # Update last login
    update_user_last_login(user['id'])
    
    # Log successful login
    log_login_attempt(identifier, ip_address, True)
    log_user_activity(user['id'], 'login', 'User logged in', ip_address, get_user_agent(request))
    
    # Set session cookie
    max_age = expires_hours * 3600
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=max_age,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    # Return user data
    return {
        "success": True,
        "message": "Login successful",
        "email_verified": email_verified,
        "user": {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "email_verified": email_verified,
            "full_name": user.get('full_name'),
            "avatar_path": user.get('avatar_path'),
            "role": user['role']
        },
        "session_token": session_token
    }


# ============================================================================
# LOGOUT
# ============================================================================

@router.post("/logout")
async def logout(request: Request, response: Response):
    """Logout user"""
    
    # Get session token
    session_token = request.cookies.get("session_token")
    
    if session_token:
        # Get user info before deleting session
        session = get_session(session_token)
        
        # Delete session
        delete_session(session_token)
        
        # Log activity
        if session:
            log_user_activity(
                session['user_id'],
                'logout',
                'User logged out',
                get_client_ip(request),
                get_user_agent(request)
            )
    
    # Clear session cookie
    response.delete_cookie("session_token")
    
    return {"success": True, "message": "Logged out successfully"}


# ============================================================================
# GET CURRENT USER
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_me(request: Request):
    """Get current authenticated user"""
    
    user = await get_current_user(request)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Get full user data
    user_data = get_user_by_id(user['user_id'])
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user_data['id'],
        username=user_data['username'],
        email=user_data['email'],
        email_verified=bool(user_data['email_verified']),
        full_name=user_data.get('full_name'),
        avatar_path=user_data.get('avatar_path'),
        bio=user_data.get('bio'),
        role=user_data['role'],
        contribution_count=user_data['contribution_count'],
        review_count=user_data['review_count'],
        is_active=bool(user_data['is_active']),
        is_banned=bool(user_data['is_banned']),
        ban_reason=user_data.get('ban_reason'),
        last_login=user_data.get('last_login'),
        created_at=user_data['created_at']
    )


# ============================================================================
# EMAIL VERIFICATION
# ============================================================================

@router.post("/verify-email")
async def verify_email(data: VerifyEmailRequest, request: Request):
    """Verify email with token"""
    
    # Get token data
    token_data = get_verification_token(data.token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    if token_data['type'] != 'email_verification':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type"
        )
    
    # Get user
    user = get_user_by_email(token_data['identifier'])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user email verified status
    update_user_email_verified(user['id'], True)
    
    # Mark token as used
    mark_token_used(data.token)
    
    # Log activity
    log_user_activity(user['id'], 'email_verified', 'Email verified', get_client_ip(request), get_user_agent(request))
    
    return {
        "success": True,
        "message": "Email verified successfully! You can now login."
    }


@router.post("/resend-verification")
async def resend_verification(data: ResendVerificationRequest, request: Request):
    """Resend verification email"""
    
    email = data.email.lower().strip()
    
    # Check rate limit
    allowed, error_msg = check_email_verification_rate_limit(email)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=error_msg)
    
    # Get user
    user = get_user_by_email(email)
    
    if not user:
        # Don't reveal if email exists
        return {"success": True, "message": "If the email exists, a verification link has been sent."}
    
    # Check if already verified
    if user['email_verified']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Delete old tokens
    delete_user_tokens(email, 'email_verification')
    
    # Create new verification token
    verification_token = create_verification_token(email, 'email_verification', 24)
    
    # Send verification email
    try:
        send_verification_email(email, user['username'], verification_token)
    except Exception as e:
        print(f"Failed to send verification email: {e}")
    
    return {
        "success": True,
        "message": "Verification email sent successfully"
    }


# ============================================================================
# PASSWORD RESET
# ============================================================================

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, request: Request):
    """Request password reset"""
    
    email = data.email.lower().strip()
    
    # Check rate limit
    allowed, error_msg = check_password_reset_rate_limit(email)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=error_msg)
    
    # Get user
    user = get_user_by_email(email)
    
    # Always return success (don't reveal if email exists)
    if not user:
        return {"success": True, "message": "If the email exists, a password reset link has been sent."}
    
    # Delete old tokens
    delete_user_tokens(email, 'password_reset')
    
    # Create password reset token (1 hour expiry)
    reset_token = create_verification_token(email, 'password_reset', 1)
    
    # Send password reset email
    try:
        send_password_reset_email(email, user['username'], reset_token)
    except Exception as e:
        print(f"Failed to send password reset email: {e}")
    
    # Log activity
    log_user_activity(user['id'], 'password_reset_requested', 'Password reset requested', get_client_ip(request), get_user_agent(request))
    
    return {
        "success": True,
        "message": "If the email exists, a password reset link has been sent."
    }


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, request: Request):
    """Reset password with token"""
    
    # Get token data
    token_data = get_verification_token(data.token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    if token_data['type'] != 'password_reset':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type"
        )
    
    # Validate new password
    is_valid, error = validate_password(data.new_password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    # Get user
    user = get_user_by_email(token_data['identifier'])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Hash new password
    new_password_hash = hash_password(data.new_password)
    
    # Update password
    update_user_password(user['id'], new_password_hash)
    
    # Mark token as used
    mark_token_used(data.token)
    
    # Invalidate all sessions (security measure)
    delete_user_sessions(user['id'])
    
    # Send password changed email
    try:
        send_password_changed_email(user['email'], user['username'])
    except Exception as e:
        print(f"Failed to send password changed email: {e}")
    
    # Log activity
    log_user_activity(user['id'], 'password_reset', 'Password reset', get_client_ip(request), get_user_agent(request))
    
    return {
        "success": True,
        "message": "Password reset successfully. Please login with your new password."
    }


# ============================================================================
# CHECK AVAILABILITY
# ============================================================================

@router.get("/check-username/{username}", response_model=CheckAvailabilityResponse)
async def check_username_availability(username: str):
    """Check if username is available"""
    
    # Validate username format
    is_valid, error = validate_username(username)
    if not is_valid:
        return CheckAvailabilityResponse(available=False, message=error)
    
    # Check if exists
    exists = check_username_exists(username)
    
    return CheckAvailabilityResponse(
        available=not exists,
        message="Username is available" if not exists else "Username is already taken"
    )


@router.get("/check-email/{email}", response_model=CheckAvailabilityResponse)
async def check_email_availability(email: str):
    """Check if email is available"""
    
    email = email.lower().strip()
    
    # Validate email format
    is_valid, error = validate_email(email)
    if not is_valid:
        return CheckAvailabilityResponse(available=False, message=error)
    
    # Check if exists
    exists = check_email_exists(email)
    
    return CheckAvailabilityResponse(
        available=not exists,
        message="Email is available" if not exists else "Email is already registered"
    )


# ============================================================================
# PASSWORD STRENGTH
# ============================================================================

@router.post("/password-strength", response_model=PasswordStrengthResponse)
async def check_password_strength(password: str):
    """Check password strength"""
    
    strength = get_password_strength(password)
    feedback = []
    
    # Generate feedback
    if len(password) < 8:
        feedback.append("Password should be at least 8 characters")
    if len(password) < 12:
        feedback.append("Consider using 12+ characters for better security")
    
    import re
    if not re.search(r'[a-z]', password):
        feedback.append("Add lowercase letters")
    if not re.search(r'[A-Z]', password):
        feedback.append("Add uppercase letters")
    if not re.search(r'\d', password):
        feedback.append("Add numbers")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        feedback.append("Add special characters")
    
    # Calculate score
    score = 0
    if strength == 'weak':
        score = 1
    elif strength == 'medium':
        score = 2
    else:
        score = 3
    
    return PasswordStrengthResponse(
        strength=strength,
        score=score,
        feedback=feedback if feedback else ["Strong password!"]
    )