import os
import jwt
import time
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 24))

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = int(time.time()) + (EXPIRATION_HOURS * 3600)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user_id(token: str) -> Optional[int]:
    """Get user ID from token"""
    payload = verify_token(token)
    if payload:
        return payload.get("user_id")
    return None