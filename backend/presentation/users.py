from fastapi import APIRouter

from application.users.user_service import UserService
from domain.users import User, UserDB
from infrastructure.globals import DatabaseDependency, CurrentUser


router = APIRouter(tags=["users"])


@router.get("/users",  status_code=200, response_model=list[User])
async def users(db: DatabaseDependency, current_user: CurrentUser):
    service = UserService(db)
    return service.get_all()


# Path
@router.get("/user/{_id}", status_code=200, response_model=User)
async def user(_id: str, db: DatabaseDependency, current_user: CurrentUser):
    service = UserService(db)
    return service.get_user_by_id(_id)


@router.post("/user", response_model=UserDB, status_code=201)
async def create_user(user: UserDB, db: DatabaseDependency, current_user: CurrentUser):
    service = UserService(db)
    return service.create(user)


@router.put("/user", response_model=User, status_code=201)
async def update_user(user: UserDB, db: DatabaseDependency, current_user: CurrentUser):
    service = UserService(db)
    return service.update(user)


@router.delete("/user/{_id}")
async def delete_user(_id: str, db: DatabaseDependency, current_user: CurrentUser):
    service = UserService(db)
    return service.delete(_id)