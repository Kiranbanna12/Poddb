"""
Admin API routes for user management
"""
from fastapi import APIRouter, HTTPException, status, Request, Depends, Query
from typing import Optional
import math

# Import models
from models.auth import (
    UserListResponse, UserResponse, BanUserRequest,
    UpdateUserRoleRequest, ActivityLogListResponse, ActivityLogResponse
)

# Import database queries
from database.auth_queries import (
    get_all_users, get_user_by_id, update_user_role,
    ban_user, unban_user, soft_delete_user,
    get_user_activity_logs, log_user_activity
)

# Import auth utilities
from auth.middleware import require_admin, get_client_ip, get_user_agent
from auth.validators import validate_role

# Import email service
from services.email_service import send_account_banned_email

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.get("/users", response_model=UserListResponse)
async def get_users(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    admin: dict = Depends(require_admin)
):
    """Get paginated list of users with filters"""
    
    # Build filters
    filters = {}
    if role:
        filters['role'] = role
    if status:
        filters['status'] = status
    if search:
        filters['search'] = search
    
    # Get users
    users, total = get_all_users(page, limit, filters)
    
    # Calculate total pages
    total_pages = math.ceil(total / limit)
    
    # Format user responses
    user_list = []
    for user_data in users:
        user_list.append(UserResponse(
            id=user_data['id'],
            username=user_data['username'],
            email=user_data['email'],
            email_verified=bool(user_data['email_verified']),
            full_name=user_data.get('full_name'),
            avatar_path=user_data.get('avatar_path'),
            bio=None,  # Don't include bio in list view
            role=user_data['role'],
            contribution_count=user_data['contribution_count'],
            review_count=user_data['review_count'],
            is_active=bool(user_data['is_active']),
            is_banned=bool(user_data['is_banned']),
            ban_reason=user_data.get('ban_reason'),
            last_login=user_data.get('last_login'),
            created_at=user_data['created_at']
        ))
    
    return UserListResponse(
        users=user_list,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_details(
    user_id: int,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Get detailed user information"""
    
    user_data = get_user_by_id(user_id)
    
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
# USER ROLE MANAGEMENT
# ============================================================================

@router.put("/users/{user_id}/role", response_model=dict)
async def update_role(
    user_id: int,
    role_data: UpdateUserRoleRequest,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Update user role"""
    
    # Get user
    user = get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate role
    is_valid, error = validate_role(role_data.role)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    # Prevent self-demotion from admin
    if admin['user_id'] == user_id and role_data.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own admin role"
        )
    
    # Update role
    success = update_user_role(user_id, role_data.role)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update role"
        )
    
    # Log activity
    log_user_activity(
        admin['user_id'],
        'role_updated',
        f"Changed role of user {user_id} to {role_data.role}",
        get_client_ip(request),
        get_user_agent(request)
    )
    
    # Log activity for target user
    log_user_activity(
        user_id,
        'role_changed',
        f"Role changed to {role_data.role} by admin",
        get_client_ip(request),
        get_user_agent(request)
    )
    
    return {"success": True, "message": f"User role updated to {role_data.role}"}


# ============================================================================
# BAN/UNBAN USER
# ============================================================================

@router.put("/users/{user_id}/ban", response_model=dict)
async def ban_user_account(
    user_id: int,
    ban_data: BanUserRequest,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Ban a user"""
    
    # Get user
    user = get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-ban
    if admin['user_id'] == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot ban yourself"
        )
    
    # Prevent banning other admins
    if user['role'] == 'admin':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot ban other administrators"
        )
    
    # Ban user
    success = ban_user(user_id, ban_data.reason)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ban user"
        )
    
    # Send ban notification email
    try:
        send_account_banned_email(user['email'], user['username'], ban_data.reason)
    except Exception as e:
        print(f"Failed to send ban email: {e}")
    
    # Invalidate all user sessions
    from database.auth_queries import delete_user_sessions
    delete_user_sessions(user_id)
    
    # Log activity
    log_user_activity(
        admin['user_id'],
        'user_banned',
        f"Banned user {user_id}. Reason: {ban_data.reason}",
        get_client_ip(request),
        get_user_agent(request)
    )
    
    # Log activity for target user
    log_user_activity(
        user_id,
        'account_banned',
        f"Account banned by admin. Reason: {ban_data.reason}",
        get_client_ip(request),
        get_user_agent(request)
    )
    
    return {"success": True, "message": "User banned successfully"}


@router.put("/users/{user_id}/unban", response_model=dict)
async def unban_user_account(
    user_id: int,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Unban a user"""
    
    # Get user
    user = get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user['is_banned']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not banned"
        )
    
    # Unban user
    success = unban_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unban user"
        )
    
    # Log activity
    log_user_activity(
        admin['user_id'],
        'user_unbanned',
        f"Unbanned user {user_id}",
        get_client_ip(request),
        get_user_agent(request)
    )
    
    # Log activity for target user
    log_user_activity(
        user_id,
        'account_unbanned',
        'Account unbanned by admin',
        get_client_ip(request),
        get_user_agent(request)
    )
    
    return {"success": True, "message": "User unbanned successfully"}


# ============================================================================
# DELETE USER
# ============================================================================

@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Soft delete a user"""
    
    # Get user
    user = get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-deletion
    if admin['user_id'] == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete yourself"
        )
    
    # Prevent deleting other admins
    if user['role'] == 'admin':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete other administrators"
        )
    
    # Soft delete user
    success = soft_delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
    
    # Invalidate all user sessions
    from database.auth_queries import delete_user_sessions
    delete_user_sessions(user_id)
    
    # Log activity
    log_user_activity(
        admin['user_id'],
        'user_deleted',
        f"Deleted user {user_id}",
        get_client_ip(request),
        get_user_agent(request)
    )
    
    return {"success": True, "message": "User deleted successfully"}


# ============================================================================
# ACTIVITY LOGS
# ============================================================================

@router.get("/users/{user_id}/activity-logs", response_model=ActivityLogListResponse)
async def get_activity_logs(
    user_id: int,
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    admin: dict = Depends(require_admin)
):
    """Get user activity logs"""
    
    # Get user
    user = get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get logs
    logs, total = get_user_activity_logs(user_id, page, limit)
    
    # Format logs
    log_list = []
    for log in logs:
        log_list.append(ActivityLogResponse(
            id=log['id'],
            user_id=log['user_id'],
            action_type=log['action_type'],
            action_details=log.get('action_details'),
            ip_address=log.get('ip_address'),
            user_agent=log.get('user_agent'),
            created_at=log['created_at']
        ))
    
    return ActivityLogListResponse(
        logs=log_list,
        total=total,
        page=page,
        limit=limit
    )