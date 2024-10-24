from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


# LOCALE DEFINITIONS
from ..database import get_db
from .schemas import PostCreateModel, PostModel
from .services import (
    create_post,
    delete_post,
    get_post_by_id,
    get_posts,
    get_user_posts,
    get_random_posts,
    get_posts_from_hashtag,
    like_post,
    liked_post_users,
    unlike_post,
)
from src.auth.service import get_current_user, existing_user
from src.auth.schemas import User as UserSchema


post_router = APIRouter(prefix="/posts", tags=["post"])


@post_router.get("/", response_model=list[PostModel])
async def get_posts_view(db: Session = Depends(get_db)):
    posts = await get_posts(db)
    return posts


@post_router.post("/", response_model=PostModel, status_code=status.HTTP_201_CREATED)
async def create_post_view(
    post: PostCreateModel, token: str, db: Session = Depends(get_db)
):
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    new_post = await create_post(db, post, user.id)
    return new_post


@post_router.get("/user", response_model=list[PostModel])
async def get_current_user_posts_view(token: str, db: Session = Depends(get_db)):
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await get_user_posts(db, user.id)


@post_router.get("/user/{username}", response_model=list[PostModel])
async def get_user_posts_view(username: str, db: Session = Depends(get_db)):
    user = await existing_user(db, username, "")

    return await get_user_posts(db, user.id)


@post_router.get("/hashtag/{hashtag}")
async def get_posts_from_hashtag_view(hashtag: str, db: Session = Depends(get_db)):
    return await get_posts_from_hashtag(db, hashtag)


@post_router.get("/feed")
async def get_random_posts_view(
    page: int = 1, limit: int = 5, hashtag: str = None, db: Session = Depends(get_db)
):
    return await get_random_posts(db, page, limit, hashtag)


@post_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_view(post_id: int, token: str, db: Session = Depends(get_db)):
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    post = await get_post_by_id(db, post_id)
    if post.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    await delete_post(db, post_id)


@post_router.post("/like", status_code=status.HTTP_204_NO_CONTENT)
async def like_post_view(post_id: int, username: str, db: Session = Depends(get_db)):
    res, detail = await like_post(db, post_id, username)
    if res == False:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return res


@post_router.post("/unlike", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_post_view(post_id: int, username: str, db: Session = Depends(get_db)):
    res, detail = await unlike_post(db, post_id, username)
    if res == False:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return res


@post_router.get("/likes/{post_id}", response_model=list[UserSchema])
async def liked_post_users_view(post_id: int, db: Session = Depends(get_db)):
    return await liked_post_users(db, post_id)


@post_router.get("/{post_id}",response_model=PostModel)
async def get_post_view(post_id: int, db: Session = Depends(get_db)):
    post = await get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post
