from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import List
import re


# LOCALE DEFINITIONS
from .schemas import PostCreateModel, PostModel, HashtagModel,PostUpdateModel
from .models import Hashtag, Post, post_hashtags
from src.auth.models import User
from src.auth.schemas import UserBaseModel
from ..activity.models import Activity


# CREATE HASHTAG FROM POST'S CONTENT
async def create_hashtag(db: Session, post: PostModel):
    regex = r"#\w+"
    matches = re.findall(regex, post.content)

    for match in matches:
        name = match[1:]

        hashtag = db.query(Hashtag).filter(Hashtag.name == name).first()
        if not hashtag:
            hashtag = Hashtag(name=name)
            db.add(hashtag)
            db.commit()
            db.refresh(hashtag)
        post.hashtags.append(hashtag)


async def create_post(db: Session, post: PostCreateModel, user_id: int):
    db_post = Post(
        content=post.content,
        image=post.image,
        location=post.location,
        author_id=user_id,
    )

    await create_hashtag(db, db_post)

    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


async def update_post(db: Session, post_id: int, post: PostUpdateModel):
    pass


async def get_user_posts(db: Session, user_id: int) -> List[PostModel]:
    posts = (
        db.query(Post)
        .filter(Post.author_id == user_id)
        .order_by(Post.created_at.desc())
        .all()
    )
    return posts


async def get_posts_from_hashtag(db: Session, hashtag_name: str):
    hashtag = db.query(Hashtag).filter(Hashtag.name == hashtag_name).first()
    if not hashtag:
        return None
    return hashtag.posts


#!!!! get random posts and return latest posts all user !!!!
async def get_random_posts(
    db: Session, page: int = 1, limit: int = 10, hashtag: str = None
) -> List[PostModel]:
    total_posts = db.query(Post).count()

    offset = (page - 1) * limit
    if offset >= total_posts:
        return []

    posts = db.query(Post, User.username).join(User).order_by(desc(Post.created_at))

    if hashtag:
        posts = posts.join(post_hashtags).join(Hashtag).filter(Hashtag.name == hashtag)

    posts = posts.offset(offset).limit(limit).all()

    result = []

    for post, username in posts:
        post_dict = post.__dict__
        post_dict["username"] = username
        result.append(post_dict)

    return result


# !!!! POST PROCESS !!!!


async def get_posts(db: Session):
    posts = db.query(Post).all()
    return posts


async def get_post_by_id(db: Session, post_id: int) -> PostModel:
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    return post


async def delete_post(db: Session, post_id: int):
    post = await get_post_by_id(db, post_id)
    db.delete(post)
    db.commit()


async def like_post(db: Session, post_id: int, username: str):
    post = await get_post_by_id(db, post_id)

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user in post.liked_by_users:
        return False, "Already liked !"

    post.liked_by_users.append(user)
    post.likes_count = len(post.liked_by_users)

    like_activity = Activity(
        username=post.author.username,
        liked_post_id=post_id,
        username_like=username,
        liked_post_image=post.image,
    )
    db.add(like_activity)

    db.commit()
    return True, "done"


async def unlike_post(db: Session, post_id: int, username: str):
    post = await get_post_by_id(db, post_id)

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user not in post.liked_by_users:
        return False, "Already unliked !"

    post.liked_by_users.remove(user)
    post.likes_count = len(post.liked_by_users)

    db.commit()
    return True, "done"


# users who liked post
async def liked_post_users(db: Session, post_id: int) -> list[UserBaseModel]:
    post = await get_post_by_id(db, post_id)
    liked_users = post.liked_by_users
    # return [UserBaseModel.from_orm(user) for user in liked_users]
    return liked_users
