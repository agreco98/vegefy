from pydantic import  BaseModel
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


load_dotenv()


class AccessTokenSettings(BaseModel):
    secret_key: str = "test"
    ttl: int = 60000 # seconds 


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

class GeminiSettings(BaseSettings):
    api_key: str = os.getenv("API_KEY")


class Settings(BaseSettings):
    authentication: AuthenticationSettings = AuthenticationSettings()
    database: DataBaseSettings = DataBaseSettings()
    gemini: GeminiSettings = GeminiSettings()


settings = Settings()