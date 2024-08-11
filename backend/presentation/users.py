from fastapi import APIRouter, Request, Depends
from typing import Collection

from application.users.user_service import UserService
from domain.users import User, UserDB
from application.auth.auth import get_current_user
from infrastructure.globals import DatabaseDependency


router = APIRouter()




@router.get("/users",  status_code=200, response_model=list[User])
async def users(db: DatabaseDependency):
    service = UserService(db.local)
    return service.get_all()


# Path
@router.get("/user/{_id}", status_code=200, response_model=User)
async def user(_id: str, db: DatabaseDependency):
    service = UserService(db.local)
    return service.get_user_by_id(_id)


@router.post("/user", response_model=UserDB, status_code=201)
async def create_user(user: UserDB, db: DatabaseDependency):
    service = UserService(db.local)
    return service.create(user)


@router.put("/user", response_model=User, status_code=201)
async def update_user(user: UserDB, db: DatabaseDependency):
    service = UserService(db.local)
    return service.update(user)


@router.delete("/user/{_id}")
async def delete_user(_id: str, db: DatabaseDependency):
    service = UserService(db.local)
    return service.delete(_id)