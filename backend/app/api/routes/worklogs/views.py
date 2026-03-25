import uuid
from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.deps import SessionDep, get_current_active_superuser
from app.api.routes.worklogs.service import WorklogService
from app.models import WorklogDetailPublic, WorklogsPublic

router = APIRouter(
    prefix="/worklogs",
    tags=["worklogs"],
    dependencies=[Depends(get_current_active_superuser)],
)


@router.get("/", response_model=WorklogsPublic)
def read_worklogs(
    session: SessionDep,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
) -> Any:
    return WorklogService.list_worklogs(session, date_from=date_from, date_to=date_to)


@router.get("/{worklog_id}", response_model=WorklogDetailPublic)
def read_worklog(
    session: SessionDep,
    worklog_id: uuid.UUID,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
) -> Any:
    return WorklogService.get_worklog(
        session, worklog_id, date_from=date_from, date_to=date_to
    )
