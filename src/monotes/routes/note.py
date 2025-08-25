# Standard Imports
from typing import Any
from datetime import datetime

# Third Party Imports
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.fastapi import datastar_response, read_signals, DatastarResponse
import marimo as mo
from mohtml import (
    div,  # pyrefly: ignore
    p,  # pyrefly: ignore
    span,  # pyrefly: ignore
    h1,  # pyrefly: ignore
    h2,  # pyrefly: ignore
    h3,  # pyrefly: ignore
    button,  # pyrefly: ignore
    a,  # pyrefly: ignore
    textarea,  # pyrefly: ignore
    input,  # pyrefly: ignore
)
# My Imports

# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/note",
    tags=["note"],
)


# ------------------Elements-------------------#
def note(text: str) -> str:
    return str(
        div(
            div(  # This is the main note container
                textarea(
                    text,
                    data_bind="note_text",
                    klass="text-base text-[var(--base05)] glow-text glass-card p-10 rounded-xl shadow-lg w-full h-full transition-all duration-300 hover:shadow-xl hover:scale-[1.02] flex flex-col justify-between items-start space-y-4",
                ),
                div(  # Wrapper for the button to position it
                    submit_note_button(),
                    klass="absolute top-4 right-4 z-10",  # Position button in top right
                ),
                klass="relative w-full max-w-4xl h-[calc(100vh-4rem)] mx-auto my-4",  # Responsive note container
            ),
            id="note",
            klass="flex justify-center items-center min-h-screen p-4",  # Centering div with padding
        )
    )


def submit_note_button() -> str:
    return str(
        button(
            "Submit",
            data_on_click="@post('/note/submit')",
            klass="glass-button text-[var(--base05)] hover:text-[var(--base07)] font-bold py-2 px-4 rounded-lg text-sm",
        )
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
