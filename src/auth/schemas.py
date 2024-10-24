from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

from .enums import Gender


class UserBaseModel(BaseModel):
    username: str
    email: str
    name: str
    dob: Optional[date] = None
    gender: Optional[Gender] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    profile_pic: Optional[str] = None


class UserCreateModel(UserBaseModel):
    password: str


class UserUpdateModel(BaseModel):
    name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[Gender] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    profile_pic: Optional[str] = None


class User(UserBaseModel):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
