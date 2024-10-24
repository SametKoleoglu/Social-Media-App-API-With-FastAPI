from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from .services import get_activities_by_username


activity_router = APIRouter(
    prefix="/activities",
    tags=["activities"],
)


@activity_router.get("/user/{username}")
async def activity(
    username: str, db: Session = Depends(get_db), page: int = 1, limit: int = 10
):
    return await get_activities_by_username(db, username, page, limit)
