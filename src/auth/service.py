from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta


from src.auth.schemas import UserCreateModel, UserUpdateModel,User as UserSchema
from src.auth.models import User


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="v1/auth/token")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


async def existing_user(db: Session, username: str, email: str):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    user = db.query(User).filter(User.email == email).first()
    return user if user else None


async def create_access_token(username: str, id: int):
    encode = {"sub": username, "id": id}
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(db: Session, token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id: str = payload.get("id")
        expires: datetime = payload.get("exp")
        if datetime.fromtimestamp(expires) < datetime.now():
            return None

        if username is None or id is None:
            return None
        return db.query(User).filter(User.id == id).first()
    except JWTError:
        return None


async def get_user_from_user_id(db: Session,user_id: int):
    return db.query(User).filter(User.id == user_id).first()


async def create_user(db: Session, user: UserCreateModel):
    db_user = User(
        username=user.username,
        email=user.email,
        name=user.name or None,
        hashed_password=bcrypt_context.hash(user.password),
        dob=user.dob or None,
        gender=user.gender or None,
        bio=user.bio or None,
        location=user.location or None,
        profile_pic=user.profile_pic or None,
    )
    db.add(db_user)
    db.commit()
    return db_user

async def get_users(db: Session):
    users = db.query(User).all()
    return users

async def authenticate(username: str, password: str, db: Session):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        return False
    if not bcrypt_context.verify(password, db_user.hashed_password):
        return False
    return db_user


async def user_update(db: Session, user: User, user_update_model: UserUpdateModel):
    user.name = user_update_model.name or user.name
    user.dob = user_update_model.dob or user.dob
    user.gender = user_update_model.gender or user.gender
    user.location = user_update_model.location or user.location
    user.bio = user_update_model.bio or user.bio
    user.profile_pic = user_update_model.profile_pic or user.profile_pic

    db.commit()
    
