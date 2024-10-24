from fastapi import APIRouter


from src.auth.views import auth_router
from src.post.views import post_router
from src.activity.views import activity_router
from src.profile.views import profile_router

base_router = APIRouter(prefix="/api/v1")

base_router.include_router(auth_router)
base_router.include_router(post_router)
base_router.include_router(profile_router)
base_router.include_router(activity_router)
