from pydantic import BaseModel


class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool


class UserDB(User):
    password: str