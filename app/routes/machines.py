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
    Machine,
    MachineQuery,
    MachineCreate,
    MachineUpdate,
)


# ------------------Helpers-------------------#
async def validate_machine(machine: Machine | None) -> Machine:
    if machine is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")
    return machine


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/machines",
    tags=["machines"],
)


# ------------------HTML-Routes-------------------#
@router.get("/", response_class=HTMLResponse)
async def read_index(
    request: Request,
) -> _TemplateResponse:
    return templates.TemplateResponse("create_machine.html", {"request": request})


# -------------------Machine-Routes-------------------#
@router.post("/create/", response_model=Machine, status_code=status.HTTP_201_CREATED)
async def create_machine(machine_request: MachineCreate) -> Machine:
    try:
        machine = Machine(**machine_request.model_dump())
        await machine.create()
    except Exception as e:
        raise e
    return machine


@router.get("/get_all/", response_model=list[Machine])
async def get_machines() -> list[Machine]:
    try:
        machines: list[Machine] = await Machine.find_all().to_list()
    except Exception as e:
        raise e
    return machines


@router.get("/query/", response_model=list[Machine])
async def query_machines(machine_query: Annotated[MachineQuery, Query()]) -> list[Machine]:
    query_params: list[GTE | LTE | RegEx | Eq | NE | LT | GT] = []
    try:
        operator: type[GTE] | type[LTE] | type[Eq] | type[NE] | type[LT] | type[GT] = Eq
        match machine_query.operator:
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

        query_params.extend(
            [
                operator(k, v)
                for k, v in machine_query.model_dump(exclude_unset=True).items()
                if "joined" in k
            ]
        )
        if machine_query.name is not None:
            query_params.append(RegEx("name", machine_query.name, "ixsm"))

        machines: list[Machine] = await Machine.find(*query_params).to_list()
    except Exception as e:
        raise e
    return machines


@router.get("/by_name/", response_model=list[Machine])
async def get_machines_by_name(machine_name: Annotated[str, Query(min_length=1)]) -> list[Machine]:
    try:
        machines: list[Machine] = await Machine.find(RegEx("name", machine_name, "ixsm")).to_list()
    except Exception as e:
        raise e
    return machines


@router.get("/by_id/{machine_id}", response_model=Machine)
async def get_machine(machine_id: str) -> Machine:
    try:
        machine: Machine = await validate_machine(await Machine.get(machine_id))
    except Exception as e:
        raise e
    return machine


@router.put("/by_id/{machine_id}", response_model=Machine, status_code=status.HTTP_202_ACCEPTED)
async def update_machine(machine_id: str, machine_request: MachineUpdate) -> Machine:
    try:
        machine: Machine = await validate_machine(await Machine.get(machine_id))
        await machine.update(Set(machine_request.model_dump(exclude_unset=True)))
        machine = await validate_machine(await Machine.get(machine_id))
    except Exception as e:
        raise e
    return machine


@router.delete("/by_id/{machine_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_machine(machine_id: str) -> str:
    try:
        machine: Machine = await validate_machine(await Machine.get(machine_id))
        await machine.delete()
    except Exception as e:
        raise e
    return f"Machine {machine_id} deleted"
