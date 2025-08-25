#!/usr/bin/env python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.gzip import GZipMiddleware

from pathlib import Path
import uvicorn
import asyncio
from datetime import datetime

from datastar_py import ServerSentEventGenerator as SSE, attribute_generator as data
from datastar_py.fastapi import datastar_response, read_signals

from mohtml import (
    span,  # pyrefly: ignore
    html,  # pyrefly: ignore
    head,  # pyrefly: ignore
    script,  # pyrefly: ignore
    body,  # pyrefly: ignore
)

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


@app.get("/data", response_class=HTMLResponse)
def index(request: Request) -> str:
    return str(
        html(
            head(
                script(
                    type="module",
                    src="https://cdn.jsdelivr.net/gh/starfederation/datastar@main/bundles/datastar.js",
                )
            ),
            body(
                span(id="currentTime"),
                span(data_text="$currentTime"),
                data_on_load="@get('/updates')",
                klass="bg-blue-900",
            ),
        )
    )


@app.get("/updates")
@datastar_response
async def updates(request: Request):
    # Retrieve a dictionary with the current state of the signals from the frontend
    # signals = await read_signals(request)  # pyrefly: ignore
    # Alternate updating an element from the backend, and updating a signal from the backend
    while True:
        yield SSE.patch_elements(
            f"""<span id="currentTime">{datetime.now().isoformat()}"""
        )
        await asyncio.sleep(1)
        yield SSE.patch_signals({"currentTime": f"{datetime.now().isoformat()}"})
        await asyncio.sleep(1)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7999)
