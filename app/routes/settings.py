# Standard Imports


# Third Party Imports
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

# My Imports


class DarkMode(BaseModel):
    dark_mode: bool | None = None


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/settings",
    tags=["settings"],
)


# -------------------Settings-Routes-------------------#
@router.get("/dark_mode/", description="Toggle dark mode")
async def update_dark_mode(request: Request) -> RedirectResponse:
    if request.session.get("dark_mode"):
        request.session["dark_mode"] = False
    else:
        request.session["dark_mode"] = True

    return RedirectResponse(url="/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
