from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Collection


from application.auth import login, refresh_access_token
from domain.auth import AccessToken, RefreshToken, TokenPayload
from config import settings
from infrastructure.auth import verify_access_token


router = APIRouter()


def get_database(request: Request) -> Collection:
    return request.app.state.db

@router.post("/login", response_model=AccessToken)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Collection = Depends(get_database)):
    tokens = login(form_data.username, form_data.password, db.local)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "payload": TokenPayload(sub=form_data.username, exp=str(settings.authentication.access_token.ttl)),
        "raw_token": tokens["access_token"]
    }


@router.post("/refresh", response_model=AccessToken)
async def refresh_token(refresh_token: str):
    new_access_token = refresh_access_token(refresh_token)
    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_access_token(new_access_token)
    return {
        "payload": TokenPayload(sub=payload.get("sub"), exp=str(settings.authentication.access_token.ttl)),
        "raw_token": new_access_token
    }