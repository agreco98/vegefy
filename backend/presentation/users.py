from fastapi import APIRouter, Request, Depends
from typing import Collection

from application.users.user_service import UserService
from domain.users import User, UserDB


router = APIRouter()

def get_database(request: Request) -> Collection:
    return request.app.state.db


@router.get("/users",  status_code=200, response_model=list[User])
async def users(db: Collection = Depends(get_database)):
    service = UserService(db.local)
    return service.get_all()


# Path
@router.get("/user/{_id}", status_code=200, response_model=User)
async def user(_id: str, db: Collection = Depends(get_database)):
    service = UserService(db.local)
    return service.get_user_by_id(_id)


@router.post("/user", response_model=UserDB, status_code=201)
async def create_user(user: UserDB, db: Collection = Depends(get_database)):
    service = UserService(db.local)
    return service.create(user)


@router.put("/user", response_model=User, status_code=201)
async def update_user(user: UserDB, db: Collection = Depends(get_database)):
    service = UserService(db.local)
    return service.update(user)


@router.delete("/user/{_id}")
async def delete_user(_id: str, db: Collection = Depends(get_database)):
    service = UserService(db.local)
    return service.delete(_id)