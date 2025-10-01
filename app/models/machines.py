# Standard Imports
import logging
from logging import Logger
from typing import Literal
from datetime import datetime

# Third Party Imports
from pydantic import BaseModel, Field
from beanie import Document, Indexed, Link, TimeSeriesConfig, Granularity

# My Imports
from ..utils import current_time
from .users import User


logging.basicConfig(level=logging.INFO)
logger: Logger = logging.getLogger(__name__)


class Machine(Document):
    joined_time: datetime = Field(default_factory=current_time)
    name: Indexed(str, unique=True)  # pyrefly: ignore
    joined_condition: int = Field(ge=0, le=5)
    special_note: str | None = None

    class Settings:
        name = "machines"


class MachineQuery(BaseModel):
    operator: Literal["gte", "lte", "eq", "ne", "lt", "gt"] = Field(default="eq")
    joined_time: datetime | None = Field(default=None)
    name: str | None = Field(default=None, min_length=1)
    joined_condition: int | None = Field(default=None, ge=0, le=5)


class MachineCreate(BaseModel):
    name: str = Field(min_length=1, alias="machine_create_name")
    joined_condition: int = Field(ge=0, le=5, alias="machine_create_joined_condition")
    special_note: str | None = Field(alias="machine_create_special_note")


class MachineUpdate(BaseModel):
    name: str | None = None
    joined_condition: int | None = None
    special_note: str | None = None


class MissingMachine(BaseModel):
    machine_name: str = Field(min_length=1, alias="prompt_machine_name")


class MachineMissingLog(Document):
    ts: datetime = Field(default_factory=current_time)
    user: Link[User]
    machine: Link[Machine]

    class Settings:
        name = "machine_missing_logs"
        timeseries = TimeSeriesConfig(
            time_field="ts",
            granularity=Granularity.seconds,
        )
