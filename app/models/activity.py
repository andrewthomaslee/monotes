# Standard Imports
import logging
from logging import Logger
from typing import Literal
from datetime import datetime

# Third Party Imports
from pydantic import BaseModel, Field
from beanie import Document, Indexed

# My Imports
from ..utils import current_time
from .logs import Task

logging.basicConfig(level=logging.INFO)
logger: Logger = logging.getLogger(__name__)


class ActiveUsers(Document):
    ts: datetime = Field(default_factory=current_time)
    user_id: Indexed(str, unique=True)  # pyrefly: ignore
    machine_name: Indexed(str, unique=True)  # pyrefly: ignore
    username: Indexed(str)  # pyrefly: ignore
    task: Task

    class Settings:
        name = "activity"


class ActiveUsersQuery(BaseModel):
    operator: Literal["gte", "lte", "eq", "ne", "lt", "gt"] = Field(default="eq")
    ts: datetime | None = Field(default=None)
    user_id: str | None = Field(default=None, min_length=1)
    username: str | None = Field(default=None, min_length=1)
    machine_name: str | None = Field(default=None, min_length=1)
    task: Task | None = None


class ActiveUsersCreate(BaseModel):
    user_id: str = Field(min_length=1, alias="create_active_user_id")
    username: str = Field(min_length=1, alias="create_active_username")
    machine_name: str = Field(min_length=1, alias="create_active_machine_name")
    task: Task = Field(alias="create_active_task")


class ActiveUsersMachinesProjection(BaseModel):
    machine_name: str
