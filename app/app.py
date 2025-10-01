# Standard Imports
from typing import Callable, Coroutine, Any
import logging
from logging import Logger
from contextlib import asynccontextmanager

# Third Party Imports
from fastapi import FastAPI, Request, Form, HTTPException, status, Response
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from starlette.templating import _TemplateResponse
from starlette.middleware.sessions import SessionMiddleware
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.fastapi import DatastarResponse, datastar_response
from datastar_py.consts import ElementPatchMode
from jinja2 import Template

# My Imports
from .utils import current_time
from .models import User, ActiveUsers, Task
from .routes import api_router, settings_router, packer_router, admin_router
from .db import init_db, load_fake_data
from .config import BASE_DIR, CONFIG_SETTINGS, templates


# ---------------Logging---------------#
logging.basicConfig(level=logging.INFO)
logger: Logger = logging.getLogger(__name__)


# ---------Setup-App---------------#
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await load_fake_data()
    yield


# Create FastAPI app
app: FastAPI = FastAPI(lifespan=lifespan)
app.add_middleware(
    GZipMiddleware,  # pyrefly: ignore
    minimum_size=1000,
    compresslevel=5,
)
# Add static files
app.mount(
    "/style",
    StaticFiles(directory=BASE_DIR / "style", follow_symlink=True, check_dir=True, html=True),
    name="style",
)


# ----------Login-Routes-----------#
@app.get("/login")
async def get_login(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_model=None)
async def post_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
) -> RedirectResponse | _TemplateResponse:
    user: User | None = await User.find_one(User.name == username, User.password == password)
    if user is not None:
        request.session["dark_mode"] = False
        request.session["username"] = user.name
        request.session["admin"] = user.admin
        request.session["user_id"] = str(user.id)
        request.session["missing_machines"] = list()
        found_active: ActiveUsers | None = await ActiveUsers.find_one(
            ActiveUsers.user_id == str(user.id)
        )
        if found_active is not None:
            request.session["active"] = True
        else:
            request.session["active"] = False

        logger.info(f"User Login at {current_time()}: `{user}`")
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    logger.warning(f"Failed login attempt for user `{username}` and password `{password}`")
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Invalid credentials"}
    )


@app.get("/logout")
async def logout(request: Request) -> RedirectResponse:
    username: str | None = request.session.get("username")
    request.session.clear()
    logger.info(f"User {username} logged out")
    return RedirectResponse(url="/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


# ---------Default-Routes---------#
@app.get("/", response_class=HTMLResponse)
async def read_index(
    request: Request,
) -> _TemplateResponse:
    context: dict[str, Any] = {"request": request}
    if not request.session["active"]:
        context["tasks"] = Task
    return templates.TemplateResponse("index.html", context)


@app.get("/favicon.ico")
async def favicon(request: Request) -> FileResponse:
    return FileResponse(BASE_DIR / "style" / "assets" / "favicon.ico")


@app.get("/health")
async def health(request: Request) -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> _TemplateResponse:
    logger.error(f"HTTP error occurred: {exc.detail}")
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "detail": exc.detail},
        status_code=exc.status_code,
    )


# -------Middleware-&-Routers-------#
app.include_router(api_router)
app.include_router(settings_router)
app.include_router(packer_router)
app.include_router(admin_router)


@app.middleware("http")
async def auth_admin_middleware(
    request: Request,
    call_next: Callable[[Request], Coroutine[None, None, Response]],
) -> Response:
    included_paths: list[str] = [
        "/api",
        "/docs",
        "/admin",
    ]
    if any(request.url.path.startswith(path) for path in included_paths):
        if request.session.get("admin"):
            return await call_next(request)
        else:
            logger.warning(
                f"User `{request.session.get('user_id')}` attempted to access admin route"
            )
            return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    else:
        return await call_next(request)


@app.middleware("http")
async def auth_middleware(
    request: Request,
    call_next: Callable[[Request], Coroutine[None, None, Response]],
) -> Response:
    excluded_paths: list[str] = [
        "/login",
        "/style/output.css",
        "/health",
        "/style/assets/favicon.ico",
    ]
    if any(request.url.path.startswith(path) for path in excluded_paths):
        return await call_next(request)

    if "username" not in request.session or "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    return await call_next(request)


app.add_middleware(
    SessionMiddleware,  # pyrefly: ignore
    secret_key=CONFIG_SETTINGS.SECRET_KEY,
    max_age=None,
)
