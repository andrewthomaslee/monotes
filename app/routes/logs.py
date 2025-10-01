# Standard Imports
from typing import Annotated

# Third Party Imports
from fastapi import APIRouter, HTTPException, status, Query
from beanie.operators import Set, GTE, LTE, RegEx, Eq, NE, LT, GT

# My Imports
from ..models import (
    User,
    Machine,
    Log,
    LogQuery,
    LogCreate,
    LogByDate,
)


# ------------------Helpers-------------------#
async def validate_log(log: Log | None) -> Log:
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return log


# ------------------Setup-------------------#
router: APIRouter = APIRouter(
    prefix="/logs",
    tags=["logs"],
)


# -------------------Log-Routes-------------------#
@router.post("/", response_model=Log, status_code=status.HTTP_201_CREATED)
async def create_log(log_request: LogCreate) -> Log:
    try:
        user: User | None = await log_request.user.fetch()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {log_request.user} not found",
            )

        machine: Machine | None = await log_request.machine.fetch()
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Machine with id {log_request.machine} not found",
            )

        log = Log(**log_request.model_dump())
        await log.create()
    except Exception as e:
        raise e
    return log


@router.get("/", response_model=list[Log])
async def get_logs(
    limit: Annotated[int, Query()] = 1000, ascending: Annotated[bool, Query()] = True
) -> list[Log]:
    sort_ts: str = "+ts" if ascending else "-ts"
    try:
        logs: list[Log] = await Log.find_all().limit(limit).sort(sort_ts).to_list()
    except Exception as e:
        raise e
    return logs


@router.get("/query/", response_model=list[Log])
async def query_logs(log_query: Annotated[LogQuery, Query()]) -> list[Log]:
    query_params: list[GTE | LTE | RegEx | Eq | NE | LT | GT] = []
    try:
        operator: type[GTE] | type[LTE] | type[Eq] | type[NE] | type[LT] | type[GT] = Eq
        match log_query.operator:
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

        query_params.append(operator(Log.ts, log_query.ts))

        if log_query.user is not None:
            query_params.append(Eq(Log.user, log_query.user))
        if log_query.machine is not None:
            query_params.append(Eq(Log.machine, log_query.machine))
        if log_query.active is not None:
            query_params.append(Eq(Log.active, log_query.active))
        if log_query.prompt is not None:
            query_params.append(Eq(Log.prompt, log_query.prompt))

        logs: list[Log] = await Log.find(*query_params).to_list()
    except Exception as e:
        raise e
    return logs


@router.get("/by_date/", response_model=list[Log])
async def get_logs_by_date(log_by_date: Annotated[LogByDate, Query()]) -> list[Log]:
    sort_ts: str = "+ts" if log_by_date.ascending else "-ts"
    try:
        logs: list[Log] = (
            await Log.find(
                GTE(Log.ts, log_by_date.start_date),
                LTE(Log.ts, log_by_date.end_date),
            )
            .sort(sort_ts)
            .to_list()
        )
    except Exception as e:
        raise e
    return logs


@router.get("/by_name/", response_model=list[Log])
async def get_logs_by_name(
    machine_name: Annotated[str, Query(min_length=1)], user_name: Annotated[str, Query(min_length=1)]
) -> list[Log]:
    query_params: list = []
    try:
        if user_name:
            query_params.append(RegEx("user_name", user_name, "ixsm"))
        if machine_name:
            query_params.append(RegEx("machine_name", machine_name, "ixsm"))

        logs: list[Log] = await Log.find(*query_params).to_list()
    except Exception as e:
        raise e
    return logs


@router.get("/{log_id}", response_model=Log)
async def get_log(log_id: str) -> Log:
    try:
        log: Log = await validate_log(await Log.get(log_id))
    except Exception as e:
        raise e
    return log


@router.put("/{log_id}", response_model=Log, status_code=status.HTTP_202_ACCEPTED)
async def update_log(log_id: str, log_request: Log) -> Log:
    try:
        log: Log = await validate_log(await Log.get(log_id))
        await log.update(Set(log_request.model_dump(exclude_unset=True)))
        log = await validate_log(await Log.get(log_id))
    except Exception as e:
        raise e
    return log


@router.delete("/{log_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_log(log_id: str) -> str:
    try:
        log: Log = await validate_log(await Log.get(log_id))
        await log.delete()
    except Exception as e:
        raise e
    return f"Log {log_id} deleted"
