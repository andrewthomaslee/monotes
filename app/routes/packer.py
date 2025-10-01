# Standard Imports
from typing import Any
import logging
from logging import Logger

# Third Party Imports
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode
from datastar_py.fastapi import DatastarResponse, read_signals
from beanie.operators import Set, RegEx, GTE, LTE, Eq, NE, LT, GT, NotIn  # noqa: F401
from jinja2 import Template

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
)

logging.basicConfig(level=logging.INFO)
logger: Logger = logging.getLogger(__name__)


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/packer",
    tags=["packer"],
)


# ------------------Routes-------------------#
# @router.get("/check_out/")
# async def check_out_form(request: Request) -> DatastarResponse:
#     template: Template = templates.get_template("check_out.html")
#     html_content: str = template.render({"request": request, "tasks": Task})
#     return DatastarResponse([SSE.patch_elements(html_content, mode=ElementPatchMode.REPLACE)])


@router.get("/check_out/get_machine/")
async def check_out_get_machine(request: Request) -> DatastarResponse:
    try:
        signals: dict[str, str] = dict()
        active_machines_projection: list[ActiveUsersMachinesProjection] = (
            await ActiveUsers.find_all().project(ActiveUsersMachinesProjection).to_list()
        )
        active_machines: list[str] = [machine.machine_name for machine in active_machines_projection]
        print(active_machines)
        machine: Machine | None = await Machine.find_one(
            NotIn(Machine.name, active_machines),
            NotIn(Machine.name, request.session["missing_machines"]),
        )
        if machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

    except Exception as e:
        logger.error(f"Error during check out get machine: {e}")
        raise e

    signals["prompt_machine_name"] = machine.name
    return DatastarResponse([SSE.patch_signals(signals)])


@router.get("/check_out/report_missing_machine/")
async def check_out_report_missing_machine(request: Request) -> DatastarResponse:
    try:
        signals: dict[str, Any] | None = await read_signals(request)
        if signals is None:
            logger.error("Error during check out report missing machine: No signals")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No signals")

        valid_machine: Machine | None = await Machine.find_one(
            Machine.name == signals["prompt_machine_name"]
        )
        if valid_machine is None:
            logger.error(f"Missing Machine not found: {signals['prompt_machine_name']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Missing Machine not found"
            )

        request.session["missing_machines"].append(signals["prompt_machine_name"])
        await MachineMissingLog(
            user={"id": request.session["user_id"], "collection": "users"},
            machine={"id": valid_machine.id, "collection": "machines"},
        ).create()

        # Regenerate Machine Name
        active_machines_projection: list[ActiveUsersMachinesProjection] = (
            await ActiveUsers.find_all().project(ActiveUsersMachinesProjection).to_list()
        )
        active_machines: list[str] = [machine.machine_name for machine in active_machines_projection]
        new_machine: Machine | None = await Machine.find_one(
            NotIn(Machine.name, active_machines),
            NotIn(Machine.name, request.session["missing_machines"]),
        )
        if new_machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

    except Exception as e:
        logger.error(f"Error during report missing machine: {e}")
        raise e

    logger.warning(f"Reported missing machine: `{valid_machine.name}:{valid_machine.id}`")
    return DatastarResponse([SSE.patch_signals({"prompt_machine_name": new_machine.name})])


@router.post("/check_out/")
async def check_out(request: Request, prompt_check_out: PromptCheckOut) -> DatastarResponse:
    try:
        valid_machine: Machine | None = await Machine.find_one(
            Machine.name == prompt_check_out.machine_name
        )
        if valid_machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

        prompt_data: Prompt = Prompt(
            condition=prompt_check_out.condition,
            battery=prompt_check_out.battery,
            task=prompt_check_out.task,
            special_note=prompt_check_out.special_note,
        )
        log_create: LogCreate = LogCreate(
            user={"id": request.session["user_id"], "collection": "users"},
            machine={"id": valid_machine.id, "collection": "machines"},
            active=True,
            prompt=prompt_data,
        )

        create_activity: ActiveUsers = ActiveUsers(
            user_id=request.session["user_id"],
            username=request.session["username"],
            machine_name=valid_machine.name,
            task=prompt_check_out.task,
        )

        await create_activity.create()
        await Log(**log_create.model_dump(exclude_unset=True)).create()
        request.session["active"] = True

    except Exception as e:
        logger.error(f"Error durining check out: {e}")
        raise e

    logger.info(
        f"Check out successful for user `{request.session['username']}:{request.session['user_id']}` with machine `{prompt_check_out.machine_name}`"
    )
    return DatastarResponse([SSE.patch_signals({"redirect_after": True})])


# @router.get("/check_in/")
# async def check_in_form(request: Request) -> DatastarResponse:
#     template: Template = templates.get_template("check_in.html")
#     html_content: str = template.render({"request": request})
#     return DatastarResponse([SSE.patch_elements(html_content, mode=ElementPatchMode.REPLACE)])


@router.post("/check_in/")
async def check_in(request: Request, prompt_check_in: PromptCheckIn) -> DatastarResponse:
    try:
        try:
            valid_machine: Machine | None = await Machine.find_one(
                Machine.name == prompt_check_in.machine_name
            )
            if valid_machine is None:
                logger.error(f"Machine not found: {prompt_check_in.machine_name}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Machine not found"
                )
        except HTTPException:
            logger.warning(f"Machine not found: {prompt_check_in.machine_name}")
            return DatastarResponse([SSE.patch_signals({"bad_machine_input": True})])

        # Sanity check
        activity: ActiveUsers | None = await ActiveUsers.find_one(
            ActiveUsers.user_id == request.session["user_id"]
        )
        if activity is None:
            logger.error(f"Active user not found: {request.session['user_id']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Active user not found"
            )

        if activity.machine_name != valid_machine.name:
            logger.error(
                f"Machine name mismatch: {activity.machine_name=} != {valid_machine.name=} for user {request.session['user_id']} @ {current_time()}"
            )
            return DatastarResponse([SSE.patch_signals({"bad_machine_input": True})])

        if activity.user_id != request.session["user_id"]:
            logger.error(f"User ID mismatch: {activity.user_id=} != {request.session['user_id']=}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID mismatch")

        prompt_data: Prompt = Prompt(
            condition=prompt_check_in.condition,
            battery=prompt_check_in.battery,
            task=activity.task,
            special_note=prompt_check_in.special_note,
        )

        create_log = LogCreate(
            user={"id": request.session["user_id"], "collection": "users"},
            machine={"id": valid_machine.id, "collection": "machines"},
            active=False,
            prompt=prompt_data,
        )

        await Log(**create_log.model_dump(exclude_unset=True)).create()
        await activity.delete()
        request.session["active"] = False
    except Exception as e:
        logger.error(f"Error during check in: {e}")
        raise e

    logger.info(
        f"Check in successful for user `{request.session['username']}:{request.session['user_id']}` with machine `{valid_machine.name}`"
    )
    return DatastarResponse([SSE.patch_signals({"redirect_after": True})])
