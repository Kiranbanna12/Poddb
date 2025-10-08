"""
Pydantic models for authentication
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)
    terms_accepted: bool = Field(...)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('terms_accepted')
    def terms_must_be_accepted(cls, v):
        if not v:
            raise ValueError('You must accept the terms and conditions')
        return v

class UserLogin(BaseModel):
    identifier: str = Field(..., description="Email or username")
    password: str = Field(...)
    remember_me: bool = Field(default=False)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    email_verified: bool
    full_name: Optional[str]
    avatar_path: Optional[str]
    bio: Optional[str]
    role: str
    contribution_count: int
    review_count: int
    is_active: bool
    is_banned: bool
    ban_reason: Optional[str]
    last_login: Optional[int]
    created_at: int
    
    class Config:
        from_attributes = True

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(...)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class ChangeEmailRequest(BaseModel):
    new_email: EmailStr
    password: str = Field(..., description="Current password for verification")

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str = Field(...)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class VerifyEmailRequest(BaseModel):
    token: str = Field(...)

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class SessionResponse(BaseModel):
    id: int
    session_token: str
    device_info: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: int
    updated_at: int
    expires: int
    is_current: bool = False

class BanUserRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)

class UpdateUserRoleRequest(BaseModel):
    role: str = Field(..., pattern="^(user|moderator|admin)$")

class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class ActivityLogResponse(BaseModel):
    id: int
    user_id: int
    action_type: str
    action_details: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: int

class ActivityLogListResponse(BaseModel):
    logs: list[ActivityLogResponse]
    total: int
    page: int
    limit: int

class PasswordStrengthResponse(BaseModel):
    strength: str  # weak, medium, strong
    score: int
    feedback: list[str]

class CheckAvailabilityResponse(BaseModel):
    available: bool
    message: Optional[str] = None
