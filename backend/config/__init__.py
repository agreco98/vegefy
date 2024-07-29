from pydantic import  BaseModel
from pydantic_settings import BaseSettings


class AccessTokenSettings(BaseModel):
    secret_key: str = "test"
    ttl: int = 60 # seconds 


class RefreshTokenSettings(BaseModel):
    secret_key: str = "test"
    ttl: int = 604800 # seconds 


class AuthenticationSettings(BaseModel):
    access_token: AccessTokenSettings = AccessTokenSettings()
    refresh_token: RefreshTokenSettings = RefreshTokenSettings()
    algorithm: str = "HS256"
    scheme: str = "Bearer"


class DataBaseSettings(BaseModel):
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db_name: str = "database"


class Settings(BaseSettings):
    authentication: AuthenticationSettings = AuthenticationSettings()
    database: DataBaseSettings = DataBaseSettings()


settings = Settings()