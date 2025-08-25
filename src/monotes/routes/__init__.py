from fastapi import APIRouter
from .note import router as note_router

router: APIRouter = APIRouter()

router.include_router(note_router)
