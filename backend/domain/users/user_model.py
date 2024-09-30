from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: Optional[str]
    fullname: str
    email: str
    disabled: bool
    premium: bool


class UserDB(User):
    password: str