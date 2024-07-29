from pydantic import  BaseModel


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


settings = AuthenticationSettings()