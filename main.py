#!/usr/bin/env python


from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.gzip import GZipMiddleware

from pathlib import Path
import uvicorn


# Discover the base directory relative to this file
BASE_DIR = Path(__file__).parent

app = FastAPI()
app.add_middleware(
    GZipMiddleware,  # pyrefly: ignore
    minimum_size=1000,
    compresslevel=9,
)

app.mount(
    "/style",
    StaticFiles(directory=BASE_DIR / "style", follow_symlink=True),
    name="style",
)

templates = Jinja2Templates(directory=BASE_DIR / "style" / "templates")


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@app.get("/favicon.ico")
async def favicon(request: Request):
    return FileResponse(BASE_DIR / "style" / "assets" / "favicon.ico")


@app.get("/health")
async def health(request: Request):
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7999)
