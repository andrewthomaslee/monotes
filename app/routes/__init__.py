from fastapi import APIRouter
from .logs import router as logs_router
from .machines import router as machines_router
from .users import router as users_router
from .settings import router as settings_router  # noqa: F401
from .packer import router as packer_router  # noqa: F401
from .admin import router as admin_router  # noqa: F401


api_router: APIRouter = APIRouter(prefix="/api")
api_router.include_router(logs_router)
api_router.include_router(machines_router)
api_router.include_router(users_router)
