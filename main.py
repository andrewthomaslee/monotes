#!/usr/bin/env python
# Standard Imports
from pathlib import Path

# Third Party Imports
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
from starlette.templating import _TemplateResponse

# My Impors
from monotes import router

# ---------Setup-App---------------#
# Discover the base directory relative to this file
BASE_DIR: Path = Path(__file__).parent
# Create FastAPI app
app: FastAPI = FastAPI()
app.add_middleware(
    GZipMiddleware,  # pyrefly: ignore
    minimum_size=500,
    compresslevel=9,
)
# Add static files
app.mount(
    "/style",
    StaticFiles(directory=BASE_DIR / "style", follow_symlink=True),
    name="style",
)
# Create Jinja2 templates
templates: Jinja2Templates = Jinja2Templates(directory=BASE_DIR / "style" / "templates")


# ---------Default-Routes---------#
@app.get("/", response_class=HTMLResponse)
async def read_index(
    request: Request,
) -> _TemplateResponse:
    return templates.TemplateResponse(request=request, name="index.html", context={})


@app.get("/favicon.ico")
async def favicon(request: Request) -> FileResponse:
    return FileResponse(BASE_DIR / "style" / "assets" / "favicon.ico")


@app.get("/health")
async def health(request: Request) -> dict[str, str]:
    return {"status": "ok"}


# ---------Home-Routes-----------#
@app.get("/note", response_class=HTMLResponse)
async def note_home(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(request=request, name="note.html", context={})


# ---------API-Routes---------#
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7999,
        workers=3,
        timeout_graceful_shutdown=10,
        use_colors=True,
    )
