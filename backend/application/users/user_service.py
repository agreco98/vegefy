from typing import List
from fastapi import HTTPException
from bson import ObjectId
from pymongo.database import Database
from domain.users.user_repository import UserRepository
from domain.users.user_model import User, UserDB

import infrastructure.database.client as db
from domain.users.user_model import User, UserDB


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
    
    def get_user_by_username(self, username: str) -> User:
        return self.repository.search_user("username", username)

    def update(self, user: UserDB) -> User:
        if not self.repository.search_user("_id", ObjectId(user.id)):
            raise HTTPException(status_code=404, detail="User not found")
        return self.repository.update(user)
    
    def delete(self, _id: str) -> bool:
        if not self.repository.search_user("_id", ObjectId(_id)):
            raise HTTPException(status_code=404, detail="User not found")
        return self.repository.delete(_id)