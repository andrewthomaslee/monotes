from fastapi import APIRouter
from .users import router as users_router
from .settings import router as settings_router  # noqa: F401


api_router: APIRouter = APIRouter(prefix="/api")
api_router.include_router(users_router)
