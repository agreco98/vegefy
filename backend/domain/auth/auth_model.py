from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str
    exp: str


class AccessToken(BaseModel):
    payload: TokenPayload
    raw_token: str


class RefreshToken(BaseModel):
    payload: TokenPayload
    raw_token: str


class TokenResponse(BaseModel):
    access_token: AccessToken
    refresh_token: RefreshToken