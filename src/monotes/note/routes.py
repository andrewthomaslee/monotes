# Standard Imports
from typing import Any
from datetime import datetime

# Third Party Imports
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.fastapi import datastar_response, read_signals, DatastarResponse  # noqa: F401

# My Imports
from .elements import note

# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/note",
    tags=["note"],
)


# ------------------Routes-------------------#
@router.get("/", response_class=HTMLResponse)
async def read_index(request: Request) -> DatastarResponse:
    return DatastarResponse(
        [SSE.patch_elements(note(f"Hello World @ {datetime.now().isoformat()}"))]
    )


@router.post("/submit")
async def submit_note(request: Request):
    signals: dict[str, Any] | None = await read_signals(request)
    print(signals)
