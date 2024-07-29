from fastapi import APIRouter, HTTPException

from application.auth import search_user_db, users_db
from infrastructure.auth import hash_password
from domain.users import User, UserDB

router = APIRouter()


@router.get("/users")
async def users():
    return users_db


# Path
@router.get("/user/{id}")
async def user(username: str):
    return search_user_db(username)


# Query
@router.get("/user")  
async def user(username: str):
    return search_user_db(username)


@router.post("/user", status_code=201)
async def create_user(user: UserDB):
    if isinstance(search_user_db(user.username), User):
        raise HTTPException(status_code=204, detail="User already exist" )

    user.password = hash_password(user.password)
    users_db.update(user)
    return user


@router.put("/user")
async def update_user(user: User):
    for index, saved_user in enumerate(users_db):
        if saved_user.id == user.id:
            users_db[index] = user 
            return user

    return { "error": "user did not update" }


@router.delete("/user/{id}")
async def delete_user(id: int):
    for index, saved_user in enumerate(users_db):
        if saved_user.id == id:
            del users_db[index]
            return
    
    return { "error": "user does not exist" }