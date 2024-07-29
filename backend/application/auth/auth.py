from datetime import timedelta
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends


from infrastructure.auth import create_access_token, create_refresh_token, verify_refresh_token, verify_access_token, verify_password
from config import settings
from domain.users import UserDB, User


__all__ = (
    "authenticate_user",
    "login",
    "refresh_access_token",
    "search_user_db",
    "users_db",
)

oauth2 = OAuth2PasswordBearer(tokenUrl="login")


users_db = {
    "agredev": {
        "id": 1,
        "username": "agredev",
        "full_name": "Ariel Greco",
        "email": "fgwrf@gmail.com",
        "disabled": False,
        "password": "$2a$12$JjM8uLfKWavuKGzYzkO9cO/nZpDEwAP5F9zpRtFxGlSjzQfHn.9v6"
    },
    "agredev2": {
        "id": 2,
        "username": "agredev2",
        "full_name": "Ariel Greco 2",
        "email": "fgwrf2@gmail.com",
        "disabled": True,
        "password": "654321"
    }

}

def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    

def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])
    

def authenticate_user(token: str = Depends(oauth2)) -> UserDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    return search_user_db(username)


def login(username: str, password: str) -> Optional[dict]:
    user = search_user_db(username)
    if not user:
        return None
    
    if not verify_password(password, user.password):
        return None

    access_token_expires = timedelta(seconds=settings.access_token.ttl)
    refresh_token_expires = timedelta(seconds=settings.refresh_token.ttl)
    access_token_str = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    refresh_token_str = create_refresh_token(data={"sub": user.username}, expires_delta=refresh_token_expires)
    return {
        "access_token": access_token_str,
        "refresh_token": refresh_token_str,
        "token_type": "bearer"
    }


def refresh_access_token(refresh_token: str) -> Optional[str]:
    payload = verify_refresh_token(refresh_token)
    if not payload:
        return None
    
    username = payload.get("sub")
    if username is None:
        return None
    
    access_token_expires = timedelta(seconds=settings.access_token.ttl)
    return create_access_token(data={"sub": username}, expires_delta=access_token_expires)