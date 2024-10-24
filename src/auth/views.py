from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime

from .schemas import User as UserSchema, UserCreateModel, UserUpdateModel
from .service import (
    create_access_token,
    existing_user,
    get_user_from_user_id,
    create_user,
    user_update,
    authenticate,
    get_current_user,
    get_users,
)
from ..database import get_db


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get(
    "/users", status_code=status.HTTP_200_OK, response_model=list[UserSchema]
)
async def all_users(db: Session = Depends(get_db)):
    return await get_users(db)


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def add_user(user: UserCreateModel, db: Session = Depends(get_db)):
    db_user = await existing_user(db, user.username, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username or email already exists",
        )

    db_user = await create_user(db, user)

    access_token = await create_access_token(user.username, db_user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.username,
    }


@auth_router.post("/token", status_code=status.HTTP_201_CREATED)
async def sign_in(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    user = await authenticate(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await create_access_token(user.username, user.id)
    return {"access_token": access_token, "token_type": "bearer", "user": user.username}


@auth_router.get("/profile", status_code=status.HTTP_200_OK, response_model=UserSchema)
async def current_user(token: str, db: Session = Depends(get_db)):
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@auth_router.put("/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(
    username: str,
    token: str,
    update_user: UserUpdateModel,
    db: Session = Depends(get_db),
):
    user = await get_current_user(db, token)

    if user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await user_update(db, user, update_user)
