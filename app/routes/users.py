# Standard Imports
from typing import Annotated

# Third Party Imports
from fastapi import APIRouter, Request, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from starlette.templating import _TemplateResponse
from beanie.operators import Set, RegEx, GTE, LTE, Eq, NE, LT, GT

# My Imports
from ..config import templates

from ..models import (
    User,
    UserQuery,
    UserCreate,
    UserUpdate,
)


# ------------------Helpers-------------------#
async def validate_user(user: User | None) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/users",
    tags=["users"],
)


# ------------------HTML-Routes-------------------#
@router.get("/", response_class=HTMLResponse)
async def read_index(
    request: Request,
) -> _TemplateResponse:
    return templates.TemplateResponse("create_user.html", {"request": request})


# -------------------User-Routes-------------------#
@router.post("/create/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_request: UserCreate) -> User:
    try:
        user = User(**user_request.model_dump())
        await user.create()
    except Exception as e:
        raise e
    return user


@router.get("/get_all/", response_model=list[User])
async def get_users() -> list[User]:
    try:
        users: list[User] = await User.find_all().to_list()
    except Exception as e:
        raise e
    return users


@router.get("/query/", response_model=list[User])
async def query_users(user_query: Annotated[UserQuery, Query()]) -> list[User]:
    query_params: list[GTE | LTE | RegEx | Eq | NE | LT | GT] = []
    try:
        operator: type[GTE] | type[LTE] | type[Eq] | type[NE] | type[LT] | type[GT] = Eq
        match user_query.operator:
            case "gte":
                operator = GTE
            case "lte":
                operator = LTE
            case "eq":
                operator = Eq
            case "ne":
                operator = NE
            case "lt":
                operator = LT
            case "gt":
                operator = GT

        if user_query.joined_time is not None:
            query_params.append(operator("joined_time", user_query.joined_time))

        if user_query.name is not None:
            query_params.append(RegEx("name", user_query.name, "ixsm"))

        if user_query.admin is not None:
            query_params.append(Eq("admin", user_query.admin))

        if user_query.password is not None:
            query_params.append(RegEx("password", user_query.password))

        users: list[User] = await User.find(*query_params).to_list()
    except Exception as e:
        raise e
    return users


@router.get("/by_name/", response_model=list[User])
async def get_users_by_name(user_name: Annotated[str, Query(min_length=1)]) -> list[User]:
    try:
        users: list[User] = await User.find(RegEx("name", user_name, "ixsm")).to_list()
    except Exception as e:
        raise e
    return users


@router.get("/by_id/{user_id}", response_model=User)
async def get_user(user_id: str) -> User:
    try:
        user: User = await validate_user(await User.get(user_id))
    except Exception as e:
        raise e
    return user


@router.put("/by_id/{user_id}", response_model=User, status_code=status.HTTP_202_ACCEPTED)
async def update_user(user_id: str, user_request: UserUpdate) -> User:
    try:
        user: User = await validate_user(await User.get(user_id))
        await user.update(Set(user_request.model_dump(exclude_unset=True)))
        user = await validate_user(await User.get(user_id))
    except Exception as e:
        raise e
    return user


@router.delete("/by_id/{user_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_user(user_id: str) -> str:
    try:
        user: User = await validate_user(await User.get(user_id))
        await user.delete()
    except Exception as e:
        raise e
    return f"User {user_id} deleted"
