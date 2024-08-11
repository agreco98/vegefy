from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Collection


from application.users.user_service import UserService
from application.auth.auth import AuthService
from domain.users.user_model import UserDB
from domain.auth import AccessToken, RefreshToken, TokenPayload, TokenResponse
from config import settings
from infrastructure.auth import verify_access_token


router = APIRouter()


def get_database(request: Request) -> Collection:
    return request.app.state.db


@router.post("/register", response_model=TokenResponse)
async def register(
    user: UserDB,
    db: Collection = Depends(get_database)
):
    user_service = UserService(db.local)
    new_user = user_service.create(user) 
    
    return AuthService.create_tokens(new_user)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Collection = Depends(get_database)
):
    user_service = UserService(db.local)
    tokens = user_service.login(form_data.username, form_data.password)

    access_token = {
        "payload": TokenPayload(sub=form_data.username, exp=str(settings.authentication.access_token.ttl)),
        "raw_token": tokens["access_token"]
    }
    refresh_token = {
        "payload": TokenPayload(sub=form_data.username, exp=str(settings.authentication.refresh_token.ttl)),
        "raw_token": tokens["refresh_token"]
    }
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: RefreshToken,
    db: Collection = Depends(get_database)
):
    user_service = UserService(db.local)
    
    return user_service.refresh_access_token(refresh_token)



@router.post("/login_test", response_model=TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Collection = Depends(get_database)):
    tokens = login(form_data.username, form_data.password, db.local)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = {
        "payload": TokenPayload(sub=form_data.username, exp=str(settings.authentication.access_token.ttl)),
        "raw_token": tokens["access_token"]
    }
    refresh_token = {
        "payload": TokenPayload(sub=form_data.username, exp=str(settings.authentication.refresh_token.ttl)),
        "raw_token": tokens["refresh_token"]
    }
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@router.post("/refresh_test", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    new_tokens = refresh_token
    if not new_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_access_token(new_tokens)

    new_access_token = {
        "payload": TokenPayload(sub=payload.get("sub"), exp=str(settings.authentication.access_token.ttl)),
        "raw_token": new_tokens["access_token"]
    }
    new_refresh_token = {
        "payload": TokenPayload(sub=payload.get("sub"), exp=str(settings.authentication.refresh_token.ttl)),
        "raw_token": new_tokens["refresh_token"]
    }
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }