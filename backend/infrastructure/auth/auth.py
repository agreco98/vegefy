from datetime import datetime, timedelta
import jwt
from jwt.exceptions import PyJWTError
from typing import Optional

from config import settings


__all__ = (
    "create_access_token", 
    "create_refresh_token", 
    "verify_access_token", 
    "verify_refresh_token",
)
    

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=settings.access_token.ttl)
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.access_token.secret_key, settings.algorithm)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=settings.refresh_token.ttl)
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.refresh_token.secret_key, settings.algorithm)


def verify_token(token: str, secret_key: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, secret_key, settings.algorithm)
        return payload
    except PyJWTError:
        return None
    

def verify_access_token(token: str) -> Optional[dict]:
    return verify_token(token, settings.access_token.secret_key)


def verify_refresh_token(token: str) -> Optional[dict]:
    return verify_token(token, settings.refresh_token.secret_key)