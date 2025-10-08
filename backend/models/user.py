from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    role: str = 'user'
    contribution_count: int = 0
    created_at: int

    class Config:
        from_attributes = True

class UserInDB(User):
    password_hash: str