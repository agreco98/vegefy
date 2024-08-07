from typing import List, Optional
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends

from domain.users.user_model import User, UserDB
from domain.auth.auth_model import TokenPayload
from domain.users.user_schema import user_schema
from infrastructure.auth import hash_password


class AuthRepository:
    def __init__(self, db: Database):
        self.collection: Collection = db.users
        self.oauth2 = OAuth2PasswordBearer(tokenUrl="login")

    def register(self, user: UserDB) -> User:
        user.password = hash_password(user.password)

        user_dict = dict(user)
        del user_dict["id"]

        id = self.collection.insert_one(user_dict).inserted_id

        new_user = user_schema(self.collection.find_one({"_id": id}))
        
        return User(**new_user)

    def authenticate(self, token: str = Depends(oauth2)) -> UserDB:
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
        
        return search_user("username", username)