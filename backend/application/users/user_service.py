from typing import List, Optional
from fastapi import HTTPException
from bson import ObjectId
from pymongo.database import Database
from datetime import timedelta

from application.auth.auth import AuthService
from domain.auth.auth_model import AccessToken, RefreshToken
from domain.users.user_model import User, UserDB
from domain.users.user_repository import UserRepository
from config import settings


class UserService:
    def __init__(self, db: Database):
        self.repository = UserRepository(db)

    def create(self, user: UserDB) -> User:
        if self.repository.search_user("email", user.email) is not None:
            raise HTTPException(status_code=400, detail="User already exists")
        return self.repository.create(user)

    def get_all(self) -> List[User]:
        return self.repository.get_all()
    
    def get_user_by_id(self, _id: str) -> User:
        return self.repository.search_user("_id", ObjectId(_id))
    
    def get_user_by_email(self, email: str) -> User:
        return self.repository.search_user("email", email)

    def update(self, user: UserDB) -> User:
        if not self.repository.search_user("_id", ObjectId(user.id)):
            raise HTTPException(status_code=404, detail="User not found")
        return self.repository.update(user)
    
    def delete(self, _id: str) -> bool:
        if not self.repository.search_user("_id", ObjectId(_id)):
            raise HTTPException(status_code=404, detail="User not found")
        return self.repository.delete(_id)
    
    def login(self, email: str, password: str) -> Optional[dict]:
        user_db = self.repository.search_user_db("email", email)
        if not user_db or not AuthService.verify_password(password, user_db.password): 
            return None

        access_token_expires = timedelta(seconds=settings.authentication.access_token.ttl)
        refresh_token_expires = timedelta(seconds=settings.authentication.refresh_token.ttl)
        access_token_str = AuthService.create_access_token({"sub": user_db.email, "premium": user_db.premium}, expires_delta=access_token_expires)
        refresh_token_str = AuthService.create_refresh_token({"sub": user_db.email, "premium": user_db.premium}, expires_delta=refresh_token_expires)
        return {
            "access_token": access_token_str,
            "refresh_token": refresh_token_str,
            "token_type": "bearer"
        }

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        payload = AuthService.verify_refresh_token(refresh_token)
        if not payload:
            return None
        
        email = payload.get("sub")
        if email is None:
            return None
        
        access_token_expires = timedelta(seconds=settings.authentication.access_token.ttl)
        user = self.get_user_by_email(email)

        return AuthService.create_access_token(user, access_token_expires)