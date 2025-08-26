from fastapi import APIRouter
from .note import note_router

router: APIRouter = APIRouter()

router.include_router(note_router)


def hello() -> None:
    print("Hello from monotes!\n❄️🐍💨")
