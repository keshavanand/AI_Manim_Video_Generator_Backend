# OAuth2 and user authentication
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token,get_current_user, get_password_hash, get_user
from app.core.auth import refresh_token
from app.schemas import RegisterUser, Token, UserData
from app.models import User as User_model
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register/", status_code=status.HTTP_201_CREATED) 
async def register(user: RegisterUser)-> UserData:
    hashed_password = get_password_hash(user.password)
    if await get_user(User_model,user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    user = User_model(username=user.username, email=user.email, hashed_password=hashed_password)
    await user.insert()
    return user

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> list[Token]:
    user = await authenticate_user(User_model, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    alpha_access_token_expires = timedelta(hours=24)
    alpha_access_token = create_access_token(
        data={"sub": user.username}, expires_delta=alpha_access_token_expires
    )
    access_token = Token(access_token=access_token, token_type="bearer")
    alpha_access_token = Token(access_token=alpha_access_token, token_type="aplha")
    return [access_token, alpha_access_token]


@router.get("/users/me/", response_model=UserData)
async def read_users_me(
    current_user: Annotated[User_model, Depends(get_current_user)],
):
    return current_user

@router.get("/regenerate_token/", response_model=Token)
async def regenerate_token(alpha_token: Optional[str] = Header(None)) -> Token:
    if not alpha_token:
        raise HTTPException(status_code=401, detail="Alpha token missing")
    return await refresh_token(alpha_token)

