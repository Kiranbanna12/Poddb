from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    identifier: str  # Can be email or username
    password: str
    remember_me: Optional[bool] = False

class User(UserBase):
    id: int
    role: str = 'user'
    contribution_count: int = 0
    created_at: int

    class Config:
        from_attributes = True

class UserInDB(User):
    password_hash: str