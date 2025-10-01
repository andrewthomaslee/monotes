# Standard Imports
from typing import Literal
from datetime import datetime

# Third Party Imports
from pydantic import BaseModel, Field
from beanie import Document, Indexed

# My Imports
from ..utils import current_time


class User(Document):
    joined_time: datetime = Field(default_factory=current_time)
    admin: bool = False
    name: Indexed(str) = Field(min_length=1)  # pyrefly: ignore
    password: str = Field(min_length=1)

    class Settings:
        name = "users"


class UserQuery(BaseModel):
    operator: Literal["gte", "lte", "eq", "ne", "lt", "gt"] = Field(default="eq")
    joined_time: datetime | None = None
    admin: bool | None = False
    name: str | None = None
    password: str | None = None


class UserCreate(BaseModel):
    name: str = Field(min_length=1, alias="user_create_name")
    password: str = Field(min_length=1, alias="user_create_password")
    admin: bool = Field(alias="user_create_admin")


class UserUpdate(BaseModel):
    admin: bool | None = None
    name: str | None = None
    password: str | None = None
