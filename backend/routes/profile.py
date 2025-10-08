"""
User profile API routes
"""
from fastapi import APIRouter, HTTPException, status, Request, Response, UploadFile, File, Depends
from typing import List
import os
import time
from pathlib import Path

# Import models
from models.auth import (
    UserResponse, ChangePasswordRequest, ChangeEmailRequest,
    UpdateProfileRequest, SessionResponse
)

# Import database queries
from database.auth_queries import (
    get_user_by_id, get_user_by_email, update_user_password,
    update_user_profile, update_user_email, soft_delete_user,
    get_user_sessions, delete_session, delete_user_sessions,
    check_email_exists, log_user_activity
)

# Import auth utilities
from auth.password import hash_password, verify_password
from auth.validators import validate_password, validate_email, sanitize_input
from auth.middleware import require_auth, get_client_ip, get_user_agent

# Import email service
from services.email_service import send_password_changed_email, send_email_change_verification

router = APIRouter(prefix="/profile", tags=["Profile"])

# Avatar upload directory
AVATAR_DIR = Path(__file__).parent.parent / "static" / "avatars"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# GET PROFILE
# ============================================================================

@router.get("", response_model=UserResponse)
async def get_profile(request: Request, user: dict = Depends(require_auth)):
    """Get current user's profile"""
    
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
# UPDATE PROFILE
# ============================================================================

@router.put("", response_model=dict)
async def update_profile(
    profile_data: UpdateProfileRequest,
    request: Request,
    user: dict = Depends(require_auth)
):
    """Update user profile"""
    
    update_data = {}
    
    if profile_data.full_name is not None:
        update_data['full_name'] = sanitize_input(profile_data.full_name, 100)
    
    if profile_data.bio is not None:
        update_data['bio'] = sanitize_input(profile_data.bio, 500)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update"
        )
    
    # Update profile
    success = update_user_profile(user['user_id'], update_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
    
    # Log activity
    log_user_activity(
        user['user_id'],
        'profile_updated',
        f"Updated: {', '.join(update_data.keys())}",
        get_client_ip(request),
        get_user_agent(request)
    )
    
    return {"success": True, "message": "Profile updated successfully"}


# ============================================================================
# CHANGE PASSWORD
# ============================================================================

@router.put("/change-password", response_model=dict)
async def change_password(
    password_data: ChangePasswordRequest,
    request: Request,
    user: dict = Depends(require_auth)
):
    """Change user password"""
    
    # Get user data
    user_data = get_user_by_id(user['user_id'])
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_data.current_password, user_data['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    is_valid, error = validate_password(password_data.new_password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    # Hash new password
    new_password_hash = hash_password(password_data.new_password)
    
    # Update password
    success = update_user_password(user['user_id'], new_password_hash)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )
    
    # Get current session token
    current_session = request.cookies.get("session_token")
    
    # Invalidate all other sessions (security measure)
    delete_user_sessions(user['user_id'], except_token=current_session)
    
    # Send password changed email
    try:
        send_password_changed_email(user_data['email'], user_data['username'])
    except Exception as e:
        print(f"Failed to send password changed email: {e}")
    
    # Log activity
    log_user_activity(
        user['user_id'],
        'password_changed',
        'Password changed',
        get_client_ip(request),
        get_user_agent(request)
    )
    
    return {"success": True, "message": "Password changed successfully"}


# ============================================================================
# CHANGE EMAIL
# ============================================================================

@router.put("/change-email", response_model=dict)
async def change_email(
    email_data: ChangeEmailRequest,
    request: Request,
    user: dict = Depends(require_auth)
):
    """Change user email"""
    
    # Get user data
    user_data = get_user_by_id(user['user_id'])
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify password
    if not verify_password(email_data.password, user_data['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect"
        )
    
    new_email = email_data.new_email.lower().strip()
    
    # Validate email
    is_valid, error = validate_email(new_email)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    # Check if email already in use
    if check_email_exists(new_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already in use"
        )
    
    # Update email
    success = update_user_email(user['user_id'], new_email)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change email"
        )
    
    # Send verification email to new address
    from database.auth_queries import create_verification_token
    verification_token = create_verification_token(new_email, 'email_verification', 24)
    
    try:
        send_email_change_verification(new_email, user_data['username'], verification_token)
    except Exception as e:
        print(f"Failed to send email verification: {e}")
    
    # Log activity
    log_user_activity(
        user['user_id'],
        'email_changed',
        f'Email changed to {new_email}',
        get_client_ip(request),
        get_user_agent(request)
    )
    
    return {
        "success": True,
        "message": "Email changed successfully. Please verify your new email address."
    }


# ============================================================================
# UPLOAD AVATAR
# ============================================================================

@router.post("/avatar", response_model=dict)
async def upload_avatar(
    file: UploadFile = File(...),
    request: Request = None,
    user: dict = Depends(require_auth)
):
    """Upload profile avatar"""
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: JPEG, PNG, WebP"
        )
    
    # Validate file size (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size: 5MB"
        )
    
    # Generate unique filename
    ext = file.filename.split('.')[-1]
    filename = f"user_{user['user_id']}_{int(time.time())}.{ext}"
    filepath = AVATAR_DIR / filename
    
    # Get current user data
    user_data = get_user_by_id(user['user_id'])
    
    # Delete old avatar if exists
    if user_data and user_data.get('avatar_path'):
        old_path = Path(__file__).parent.parent / user_data['avatar_path']
        if old_path.exists():
            try:
                old_path.unlink()
            except:
                pass
    
    # Save new avatar
    with open(filepath, 'wb') as f:
        f.write(contents)
    
    # Update user avatar path
    avatar_path = f"static/avatars/{filename}"
    success = update_user_profile(user['user_id'], {'avatar_path': avatar_path})
    
    if not success:
        # Clean up uploaded file
        filepath.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update avatar"
        )
    
    # Log activity
    log_user_activity(
        user['user_id'],
        'avatar_updated',
        'Avatar updated',
        get_client_ip(request),
        get_user_agent(request)
    )
    
    return {
        "success": True,
        "message": "Avatar uploaded successfully",
        "avatar_path": avatar_path
    }


# ============================================================================
# DELETE ACCOUNT
# ============================================================================

@router.delete("/delete-account", response_model=dict)
async def delete_account(
    password: str,
    request: Request,
    response: Response,
    user: dict = Depends(require_auth)
):
    """Soft delete user account"""
    
    # Get user data
    user_data = get_user_by_id(user['user_id'])
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify password
    if not verify_password(password, user_data['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect"
        )
    
    # Soft delete user
    success = soft_delete_user(user['user_id'])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
    
    # Delete all sessions
    delete_user_sessions(user['user_id'])
    
    # Clear session cookie
    response.delete_cookie("session_token")
    
    # Log activity
    log_user_activity(
        user['user_id'],
        'account_deleted',
        'Account deleted',
        get_client_ip(request),
        get_user_agent(request)
    )
    
    return {"success": True, "message": "Account deleted successfully"}


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(request: Request, user: dict = Depends(require_auth)):
    """Get all active sessions for current user"""
    
    current_session_token = request.cookies.get("session_token")
    sessions = get_user_sessions(user['user_id'])
    
    # Format sessions
    session_list = []
    for session in sessions:
        session_list.append(SessionResponse(
            id=session['id'],
            session_token=session['session_token'],
            device_info=session.get('device_info'),
            ip_address=session.get('ip_address'),
            user_agent=session.get('user_agent'),
            created_at=session['created_at'],
            updated_at=session['updated_at'],
            expires=session['expires'],
            is_current=(session['session_token'] == current_session_token)
        ))
    
    return session_list


@router.delete("/sessions/{session_id}", response_model=dict)
async def delete_session_by_id(
    session_id: int,
    request: Request,
    user: dict = Depends(require_auth)
):
    """Delete a specific session"""
    
    # Get all user sessions
    sessions = get_user_sessions(user['user_id'])
    
    # Find session
    target_session = None
    for session in sessions:
        if session['id'] == session_id:
            target_session = session
            break
    
    if not target_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Delete session
    success = delete_session(target_session['session_token'])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )
    
    # Log activity
    log_user_activity(
        user['user_id'],
        'session_deleted',
        f"Session {session_id} deleted",
        get_client_ip(request),
        get_user_agent(request)
    )
    
    return {"success": True, "message": "Session deleted successfully"}


@router.delete("/sessions", response_model=dict)
async def delete_all_sessions(
    request: Request,
    response: Response,
    user: dict = Depends(require_auth)
):
    """Delete all sessions except current"""
    
    current_session_token = request.cookies.get("session_token")
    
    # Delete all sessions except current
    deleted_count = delete_user_sessions(user['user_id'], except_token=current_session_token)
    
    # Log activity
    log_user_activity(
        user['user_id'],
        'all_sessions_deleted',
        f"Deleted {deleted_count} sessions",
        get_client_ip(request),
        get_user_agent(request)
    )
    
    return {
        "success": True,
        "message": f"Deleted {deleted_count} session(s) successfully"
    }