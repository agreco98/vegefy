from typing import List, Optional
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection

from domain.users.user_model import User, UserDB
from domain.users.user_schema import user_schema
from infrastructure.auth import hash_password


class UserRepository:
    def __init__(self, db: Database):
        self.collection: Collection = db.users

    def create(self, user: UserDB) -> User:
        user.password = hash_password(user.password)

        user_dict = dict(user)
        del user_dict["id"]

        id = self.collection.insert_one(user_dict).inserted_id

        new_user = user_schema(self.collection.find_one({"_id": id}))
        
        return UserDB(**new_user)

    def get_all(self) -> List[User]:
        users = self.collection.find()
        return [User(**user_schema(user)) for user in users]

    def get_user(self, _id: str) -> User:
        user = self.search_user("_id", ObjectId(_id))
        if user:
            return User(**user_schema(user))
        return None


    def search_user(self, field: str, key) -> Optional[User]:
        user = self.collection.find_one({field: key})
        return User(**user_schema(user)) if user else None
    

    def search_user_db(self, field: str, key) -> Optional[UserDB]:
        user = self.collection.find_one({field: key})
        return UserDB(**user_schema(user)) if user else None


    def update(self, user: UserDB) -> User:
        user_dict = dict(user)
        del user_dict["id"]

        self.collection.find_one_and_replace({"_id": ObjectId(user.id)}, user_dict)
        return self.search_user("_id", ObjectId(user.id))

    def delete(self, _id: str) -> bool:
        found = self.collection.find_one_and_delete({"_id": ObjectId(_id)})
        return found is not None