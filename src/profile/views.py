from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from src.database import get_db
from src.auth.service import get_current_user
from .schemas import ProfileModel, FollowersList, FollowingList
from .services import (
    get_followers,
    get_following,
    follow,
    unfollow,
    check_follow,
    existing_user,
)


profile_router = APIRouter(prefix="/profile", tags=["profile"])


@profile_router.get("/user/{username}", response_model=ProfileModel)
async def profile_view(username: str, db: Session = Depends(get_db)):
    user = await existing_user(db, username, "")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@profile_router.post("/follow/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def follow_view(username: str, token: str, db: Session = Depends(get_db)):
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token invalid or expired"
        )

    response = await follow(db, user.username, username)
    if response == False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Couldn't follow user"
        )


@profile_router.post("/unfollow/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def follow_view(username: str, token: str, db: Session = Depends(get_db)):
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token invalid or expired"
        )

    response = await unfollow(db, user.username, username)
    if response == False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Couldn't follow user"
        )


@profile_router.get("/followers", response_model=FollowersList)
async def get_followers_view(token: str, db: Session = Depends(get_db)):
    current_user = await get_current_user(db, token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await get_followers(db, current_user.id)


@profile_router.get("/following", response_model=FollowingList)
async def get_followers_view(token: str, db: Session = Depends(get_db)):
    current_user = await get_current_user(db, token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await get_following(db, current_user.id)