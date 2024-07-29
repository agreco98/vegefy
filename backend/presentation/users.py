from fastapi import APIRouter, HTTPException
from bson import ObjectId

from application.auth import search_user
from application.users.user import user_schema, users_schema
from infrastructure.auth import hash_password
import infrastructure.database.client as db
from domain.users import User, UserDB

router = APIRouter()


@router.get("/users", response_model=list[User])
async def users():
    return users_schema(db.client.local.users.find())


# Path
@router.get("/user/{id}", response_model=User)
async def user(id: str):
    return search_user("_id", ObjectId(id))


@router.post("/user", response_model=User, status_code=201)
async def create_user(user: UserDB):

    if isinstance(search_user("email", user.email), User):
        raise HTTPException(status_code=404, detail="User already exist" )

    user.password = hash_password(user.password)

    user_dict = dict(user)
    del user_dict["id"]

    id = db.client.local.users.insert_one(user_dict).inserted_id

    new_user = user_schema(db.client.local.users.find_one({"_id": id}))
    UserDB(**new_user)

    return search_user("_id", ObjectId(id))


@router.put("/user")
async def update_user(user: User):
    user_dict = dict(user)

    try:
        db.client.local.users.find_one_and_replace(
            {"_id": ObjectId(user.id)}, user_dict)
    except:
        raise HTTPException(status_code=404, detail="User was not updated")

    return search_user("_id", ObjectId(user.id))


@router.delete("/user/{id}")
async def delete_user(id: str):
    found = db.client.local.users.find_one_and_delete({"_id": ObjectId(id)})
                                                
    if not found:
        raise HTTPException(status_code=404, detail="User was not found")