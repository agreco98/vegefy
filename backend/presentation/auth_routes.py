from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from infrastructure.globals import DatabaseDependency
from application.users.user_service import UserService
from application.auth.auth import AuthService
from domain.users.user_model import UserDB
from domain.auth import RefreshToken, TokenPayload, TokenResponse
from config import settings
from infrastructure.auth import verify_access_token


router = APIRouter(tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(
    user: UserDB,
    db: DatabaseDependency
):
    plain_password = user.password
    user_service = UserService(db)
    new_user = user_service.create(user) 

    tokens = user_service.login(new_user.email, plain_password)

    access_token = {
        "payload": TokenPayload(sub=new_user.email, exp=str(settings.authentication.access_token.ttl)),
        "raw_token": tokens["access_token"]
    }
    refresh_token = {
        "payload": TokenPayload(sub=new_user.email, exp=str(settings.authentication.refresh_token.ttl)),
        "raw_token": tokens["refresh_token"]
    }
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }



@router.post("/login", response_model=TokenResponse)
async def login(
    db: DatabaseDependency, 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user_service = UserService(db)
    tokens = user_service.login(form_data.email, form_data.password)

    access_token = {
        "payload": TokenPayload(sub=form_data.email, exp=str(settings.authentication.access_token.ttl)),
        "raw_token": tokens["access_token"]
    }
    refresh_token = {
        "payload": TokenPayload(sub=form_data.email, exp=str(settings.authentication.refresh_token.ttl)),
        "raw_token": tokens["refresh_token"]
    }
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: RefreshToken,
    db: DatabaseDependency
):
    user_service = UserService(db)
    
    return user_service.refresh_access_token(refresh_token)