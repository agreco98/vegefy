from datetime import timedelta
from typing import Optional, Collection
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends, Request
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import PyJWTError, ExpiredSignatureError
from typing import Optional
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from infrastructure.auth import create_access_token, create_refresh_token, verify_refresh_token, verify_access_token, verify_password
from config import settings
from domain.users import UserDB, User
from domain.users.user_schema import user_schema
import domain.auth.auth_model as TokenPayload
from domain.users.user_repository import UserRepository


def get_database(request: Request) -> Collection:
    return request.app.state.db

#oauth2 = OAuth2PasswordBearer(tokenUrl="login")
crypt = CryptContext(schemes=["bcrypt"])

class AuthService:

    @staticmethod
    def create_access_token(user: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = user.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=settings.authentication.access_token.ttl)
    
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.authentication.access_token.secret_key, settings.authentication.algorithm)

    @staticmethod
    def create_refresh_token(user: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = user.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=settings.authentication.refresh_token.ttl)

        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.authentication.refresh_token.secret_key, settings.authentication.algorithm)

    @staticmethod
    def verify_refresh_token(token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, settings.refresh_token.secret_key, settings.authentication.algorithm)
        except PyJWTError:
            return None

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return crypt.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return crypt.hash(password)
    
    def create_tokens(self, user: User, access_expires_delta: Optional[timedelta] = None, refresh_expires_delta: Optional[timedelta] = None) -> dict:
        access_token = self.create_access_token(user, access_expires_delta)
        refresh_token = self.create_refresh_token(user, refresh_expires_delta)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }


class CustomHTTPBearer(HTTPBearer):
    async def __call__(
        self, request: Request, db: Collection = Depends(get_database)
    ) -> Optional[HTTPAuthorizationCredentials]:
        res = await super().__call__(request)

        try:
            payload = jwt.decode(
                res.credentials, 
                settings.authentication.access_token.secret_key, 
                settings.authentication.algorithm
            )
            
            user_repository = UserRepository(db.local)
            user = user_repository.search_user("username", payload["sub"])
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            #if user.banned:
             #   raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Banned user")
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except (PyJWTError) as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
            )
        else:
            request.state.user = user
            return user


oauth2_scheme = CustomHTTPBearer()


async def get_current_user(user: User = Depends(oauth2_scheme)) -> User:
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user