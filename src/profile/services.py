from sqlalchemy.orm import Session
from datetime import datetime

# LOCALE DEFINITIONS
from ..activity.models import Activity
from ..auth.models import User, Follow
from ..auth.service import existing_user, get_current_user, get_user_from_user_id
from ..database import get_db
from .schemas import ProfileModel, FollowersList, FollowingList


async def follow(db: Session, follower: str, following: int):
    db_follower = await existing_user(db, follower, "")
    db_following = await existing_user(db, following, "")

    if not db_follower or not db_following:
        return False

    db_follow = (
        db.query(Follow)
        .filter_by(follower_id=db_follower.id, following_id=db_following.id)
        .first()
    )
    if db_follow:
        return False

    db_follow = Follow(follower_id=db_follower.id, following_id=db_following.id)
    db.add(db_follow)

    db_follower.following_count += 1
    db_following.followers_count += 1

    follow_Activity = Activity(
        username=following,
        followed_username=db_follower.username,
        followed_user_pic=db_follower.profile_pic,
    )

    db.add(follow_Activity)
    db.commit()


async def unfollow(db: Session, follower: str, following: int):
    db_follower = await existing_user(db, follower, "")
    db_following = await existing_user(db, following, "")

    if not db_follower or not db_following:
        return False

    db_follow = (
        db.query(Follow)
        .filter_by(follower_id=db_follower.id, following_id=db_following.id)
        .first()
    )
    if not db_follow:
        return False

    db.delete(db_follow)

    db_follower.following_count -= 1
    db_following.followers_count -= 1

    db.commit()


async def get_followers(db: Session, user_id: int) -> list[FollowersList]:
    db_user = await get_user_from_user_id(db, user_id)

    if not db_user:
        return []

    db_followers = (
        db.query(Follow)
        .filter_by(following_id=user_id)
        .join(User, User.id == Follow.follower_id)
        .all()
    )

    followers = []
    for users in db_followers:
        followers.append(
            {
                "profile_pic": users.follower.profile_pic,
                "name": users.follower.name,
                "username": users.follower.username,
            }
        )

    return FollowersList(followers=followers)


async def get_following(db: Session, user_id: int) -> list[FollowingList]:
    db_user = await get_user_from_user_id(db, user_id)

    if not db_user:
        return []

    db_followers = (
        db.query(Follow)
        .filter_by(follower_id=user_id)
        .join(User, User.id == Follow.following_id)
        .all()
    )

    following = []
    for users in db_followers:
        following.append(
            {
                "profile_pic": users.follower.profile_pic,
                "name": users.follower.name,
                "username": users.follower.username,
            }
        )

    return FollowingList(following=following)


async def check_follow(db: Session, current_user: User, user: str):
    db_follower = await existing_user(db, current_user, "")
    db_following = await existing_user(db, user, "")

    if not db_follower or not db_following:
        return False

    db_following = (
        db.query(Follow)
        .filter_by(follower_id=db_follower.id, following_id=db_following.id)
        .first()
    )

    if db_following:
        return True
    return False
