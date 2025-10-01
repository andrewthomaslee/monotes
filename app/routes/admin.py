# Standard Imports
from typing import Any
import logging
from logging import Logger

# Third Party Imports
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from starlette.templating import _TemplateResponse
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode
from datastar_py.fastapi import DatastarResponse, read_signals
from beanie.operators import Set, RegEx, GTE, LTE, Eq, NE, LT, GT, NotIn  # noqa: F401
from jinja2 import Template
from pydantic import BaseModel
import pymongo

# My Imports
from ..utils import current_time
from ..config import templates
from ..models import (
    Machine,
    Log,
    Task,
    LogCreate,
    PromptCheckOut,
    PromptCheckIn,
    Prompt,
    MissingMachine,
    ActiveUsers,
    ActiveUsersMachinesProjection,
    MachineMissingLog,
    User,
)

logging.basicConfig(level=logging.INFO)
logger: Logger = logging.getLogger(__name__)


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


# ------------------Routes-------------------#
@router.get("/dashboard/")
async def dashboard(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/activity-logs/")
async def activity_logs(request: Request) -> DatastarResponse:
    activity_logs: list[ActiveUsers] = await ActiveUsers.find_all().to_list()
    rows: list[str] = []
    for log in activity_logs:
        rows.append(
            f"""
<tr class="table-row">
    <td class="td-cell whitespace-nowrap">{log.ts}</td>
    <td class="td-cell font-mono text-xs">{log.user_id}</td>
    <td class="td-cell">{log.machine_name}</td>
    <td class="td-cell">{log.username}</td>
    <td class="td-cell">{log.task}</td>
</tr>
"""
        )
    html: str = f"""
<div class="table-container" id="table-container" data-on-interval__duration.6s="@get('/admin/activity-logs/')">
    <table class="data-table">
        <!-- Table Header -->
        <thead class="table-header">
            <tr>
                <th class="th-cell">Time</th>
                <th class="th-cell">User Id</th>
                <th class="th-cell">Machine Name</th>
                <th class="th-cell">Username</th>
                <th class="th-cell">Task</th>
            </tr>
        </thead>
        <!-- Table Body -->
        <tbody>
            {"".join(rows)}
        </tbody>
    </table>
</div>
"""
    return DatastarResponse(
        [
            SSE.patch_elements(html),
            SSE.patch_signals({"table": "activity-logs"}),
        ]
    )


@router.get("/follow-logs/")
async def follow_logs(request: Request) -> DatastarResponse:
    follow_logs: dict[str, Any] | None = await read_signals(request)
    print(follow_logs)
    if follow_logs:
        page: int = int(follow_logs.get("follow_page"))  # pyrefly: ignore
        ascending = bool(follow_logs.get("follow_acsending"))
        prev_table: str = str(follow_logs.get("table"))
    else:
        page = 0
        ascending = True

    if prev_table != "follow-logs":
        page = 0
        ascending = True

    if page < 0:
        page = 0

    if ascending:
        sort_ts: str = "+ts"
    else:
        sort_ts: str = "-ts"

    logs: list = await Log.find(limit=20, skip=page * 20, fetch_links=True).sort(sort_ts).to_list()
    if len(logs) < 20:
        disable_paging_right = True
    else:
        disable_paging_right = False
    if page <= 0:
        disable_paging_left = True
    else:
        disable_paging_left = False

    rows: list[str] = []
    for log in logs:
        rows.append(
            f"""
<tr class="table-row">
    <td class="td-cell whitespace-nowrap">{log.ts}</td>
    <td class="td-cell font-mono text-xs">{log.user.name}</td>
    <td class="td-cell">{log.machine.name}</td>
    <td class="td-cell">{log.active}</td>
    <td class="td-cell">{log.prompt.task}</td>
</tr>
"""
        )
    data_star_loader: str = (
        """data-on-interval__duration.6s="@get('/admin/follow-logs/')"""
        if page == 0
        else """data-on-load="@get('/admin/follow-logs/')"""
    )

    html: str = f"""
<div class="table-container" id="table-container" {data_star_loader}">
    <table class="data-table">
        <!-- Table Header -->
        <thead class="table-header">
            <tr>
                <th class="th-cell">Time</th>
                <th class="th-cell">User Name</th>
                <th class="th-cell">Machine Name</th>
                <th class="th-cell">Active</th>
                <th class="th-cell">Task</th>
            </tr>
        </thead>
        <!-- Table Body -->
        <tbody>
            {"".join(rows)}
        </tbody>
    </table>
</div>
"""
    return DatastarResponse(
        [
            SSE.patch_elements(html),
            SSE.patch_signals(
                {
                    "follow_page": page,
                    "follow_acsending": ascending,
                    "disable_paging_left": disable_paging_left,
                    "disable_paging_right": disable_paging_right,
                    "table": "follow-logs",
                }
            ),
        ]
    )


@router.get("/missing-logs/")
async def missing_logs(request: Request) -> DatastarResponse:
    follow_logs: dict[str, Any] | None = await read_signals(request)
    print(follow_logs)
    if follow_logs:
        page: int = int(follow_logs.get("follow_page"))  # pyrefly: ignore
        ascending = bool(follow_logs.get("follow_acsending"))
        prev_table: str = str(follow_logs.get("table"))
        follow_logs.get("follow_ascending")
    else:
        page = 0
        ascending = True
        prev_table = "activity-logs"

    if prev_table != "missing-logs":
        page = 0
        ascending = True

    if page < 0:
        page = 0

    if ascending:
        sort_ts: str = "+ts"
    else:
        sort_ts: str = "-ts"

    logs: list = (
        await MachineMissingLog.find(limit=20, skip=page * 20, fetch_links=True)
        .sort(sort_ts)
        .to_list()
    )
    if len(logs) < 20:
        disable_paging_right = True
    else:
        disable_paging_right = False
    if page <= 0:
        disable_paging_left = True
    else:
        disable_paging_left = False

    rows: list[str] = []
    for log in logs:
        rows.append(
            f"""
<tr class="table-row">
    <td class="td-cell whitespace-nowrap">{log.ts}</td>
    <td class="td-cell font-mono text-xs">{log.user.name}</td>
    <td class="td-cell">{log.machine.name}</td>
</tr>
"""
        )
    data_star_loader: str = (
        """data-on-interval__duration.6s="@get('/admin/missing-logs/')"""
        if page == 0
        else """data-on-load="@get('/admin/missing-logs/')"""
    )

    html: str = f"""
<div class="table-container" id="table-container" {data_star_loader}">
    <table class="data-table">
        <!-- Table Header -->
        <thead class="table-header">
            <tr>
                <th class="th-cell">Time</th>
                <th class="th-cell">User Name</th>
                <th class="th-cell">Machine Name</th>
            </tr>
        </thead>
        <!-- Table Body -->
        <tbody>
            {"".join(rows)}
        </tbody>
    </table>
</div>
"""
    return DatastarResponse(
        [
            SSE.patch_elements(html),
            SSE.patch_signals(
                {
                    "follow_page": page,
                    "follow_acsending": ascending,
                    "disable_paging_left": disable_paging_left,
                    "disable_paging_right": disable_paging_right,
                    "table": "missing-logs",
                }
            ),
        ]
    )
