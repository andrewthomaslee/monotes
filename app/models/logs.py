# Standard Imports
from typing import Literal
from datetime import datetime
from enum import StrEnum

# Third Party Imports
from pydantic import BaseModel, Field
from beanie import Document, Link, TimeSeriesConfig, Granularity

# My Imports
from ..utils import current_time
from .users import User
from .machines import Machine


class Task(StrEnum):
    WAKE_UP = "wake_up"
    SLEEP = "sleep"
    WORK = "work"
    PLAY = "play"
    DRINK = "drink"
    EAT = "eat"
    SIT = "sit"
    STAND = "stand"


class Prompt(BaseModel):
    condition: int = Field(ge=0, le=5)
    battery: int = Field(ge=0, le=100)
    task: Task
    special_note: str | None = None


class Log(Document):
    ts: datetime = Field(default_factory=current_time)
    user: Link[User]
    machine: Link[Machine]
    active: bool
    prompt: Prompt

    class Settings:
        name = "logs"
        timeseries = TimeSeriesConfig(
            time_field="ts",
            granularity=Granularity.seconds,
        )


class LogQuery(BaseModel):
    operator: Literal["gte", "lte", "eq", "ne", "lt", "gt"] = Field(default="eq")
    ts: datetime | None = None
    user: Link[User] | None = None
    machine: Link[Machine] | None = None
    active: bool | None = None
    prompt: Prompt | None = None


class LogByDate(BaseModel):
    ascending: bool = Field(default=True)
    start_date: datetime
    end_date: datetime


class LogCreate(BaseModel):
    user: Link[User]
    machine: Link[Machine]
    active: bool
    prompt: Prompt


class LogUpdate(BaseModel):
    user: Link[User] | None = None
    machine: Link[Machine] | None = None
    active: bool | None = None
    prompt: Prompt | None = None


class PromptCheckOut(BaseModel):
    machine_name: str = Field(alias="prompt_machine_name")
    condition: int = Field(ge=0, le=5, alias="prompt_condition")
    battery: int = Field(ge=0, le=100, alias="prompt_battery")
    task: Task = Field(alias="prompt_task")
    special_note: str | None = Field(alias="prompt_special_note")


class PromptCheckIn(BaseModel):
    machine_name: str = Field(alias="prompt_machine_name")
    condition: int = Field(ge=0, le=5, alias="prompt_condition")
    battery: int = Field(ge=0, le=100, alias="prompt_battery")
    special_note: str | None = Field(alias="prompt_special_note")
