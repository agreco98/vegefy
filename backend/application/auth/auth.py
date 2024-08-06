from datetime import timedelta
from typing import Optional, Collection
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends, Request


from infrastructure.auth import create_access_token, create_refresh_token, verify_refresh_token, verify_access_token, verify_password
from config import settings
from domain.users import UserDB, User
from domain.users.user_schema import user_schema
import infrastructure.database.client as db
from domain.users.user_repository import UserRepository
from application.users.user_service import UserService


__all__ = (
    "authenticate_user",
    "login",
    "refresh_access_token",
    "search_user"
)

oauth2 = OAuth2PasswordBearer(tokenUrl="login")



def search_user_db(field: str, key, db: Collection):
    try:
        user = db.users.find_one({field: key})
        print(user)
        return UserDB(**user_schema(user))
    except Exception as e:
        print(str(e))
        return {"error": "User was not found"}


def search_user(field: str, key, db: Collection):
    try:
        user = db.users.find_one({field: key})
        print(UserDB(**user_schema(user)))
        return UserDB(**user_schema(user))
    except:
        return {"error": "User was not found"}

    
def authenticate_user(token: str = Depends(oauth2)) -> str:
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
    
    return username


def login(username: str, password: str, db: Collection) -> Optional[dict]:
    user = search_user_db("username", username, db)
    print(user)
    if not user:
        return None
    print(user)
    if not verify_password(password, user.password):
        return None

    access_token_expires = timedelta(seconds=settings.authentication.access_token.ttl)
    refresh_token_expires = timedelta(seconds=settings.authentication.refresh_token.ttl)
    access_token_str = create_access_token(data={"sub": user.username, "premium": user.premium}, expires_delta=access_token_expires)
    refresh_token_str = create_refresh_token(data={"sub": user.username, "premium": user.premium}, expires_delta=refresh_token_expires)
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
    
    access_token_expires = timedelta(seconds=settings.authentication.access_token.ttl)
    return create_access_token(data={"sub": username}, expires_delta=access_token_expires)