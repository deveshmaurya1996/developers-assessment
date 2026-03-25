import uuid
from collections import defaultdict
from datetime import date, datetime, time, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import (
    Task,
    TimeEntry,
    TimeEntryPublic,
    User,
    WorkLog,
    WorklogDetailPublic,
    WorklogsPublic,
    WorklogSummaryPublic,
)


def _range_bounds(
    date_from: date | None, date_to: date | None
) -> tuple[datetime | None, datetime | None]:
    if date_from is None and date_to is None:
        return None, None
    if date_from is None or date_to is None:
        raise HTTPException(
            status_code=400,
            detail="date_from and date_to are both required when filtering",
        )
    if date_from > date_to:
        raise HTTPException(
            status_code=400, detail="date_from must be on or before date_to"
        )
    start = datetime.combine(date_from, time.min, tzinfo=timezone.utc)
    end = datetime.combine(date_to, time.max, tzinfo=timezone.utc)
    return start, end


def _as_utc(w: datetime) -> datetime:
    if w.tzinfo is None:
        return w.replace(tzinfo=timezone.utc)
    return w


def _entry_in_range(
    worked_at: datetime, start: datetime | None, end: datetime | None
) -> bool:
    if start is None or end is None:
        return True
    w = _as_utc(worked_at)
    return start <= w <= end


def build_summaries(
    session: Session,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    only_pending: bool = False,
    require_entries_in_range_when_filtered: bool = True,
) -> list[WorklogSummaryPublic]:
    start, end = _range_bounds(date_from, date_to)
    tasks = {t.id: t for t in session.exec(select(Task)).all()}
    users = {u.id: u for u in session.exec(select(User)).all()}
    wls = list(session.exec(select(WorkLog)).all())
    entries = list(session.exec(select(TimeEntry)).all())
    by_wl: dict[uuid.UUID, list[TimeEntry]] = defaultdict(list)
    for e in entries:
        by_wl[e.worklog_id].append(e)

    out: list[WorklogSummaryPublic] = []
    for wl in wls:
        if only_pending and wl.status != "pending":
            continue
        task = tasks.get(wl.task_id)
        usr = users.get(wl.freelancer_id)
        if not task or not usr:
            continue
        wl_entries = by_wl.get(wl.id, [])
        if start is not None and end is not None:
            filtered = [
                e for e in wl_entries if _entry_in_range(e.worked_at, start, end)
            ]
            if require_entries_in_range_when_filtered and not filtered:
                continue
        else:
            filtered = wl_entries

        hours = sum(float(e.hours) for e in filtered)
        rate = float(task.hourly_rate)
        earned = hours * rate
        out.append(
            WorklogSummaryPublic(
                id=wl.id,
                task_id=task.id,
                task_title=task.title,
                freelancer_id=usr.id,
                freelancer_email=str(usr.email),
                period_hours=hours,
                period_earned=earned,
                status=wl.status,
                time_entry_count=len(filtered),
            )
        )
    return out


class WorklogService:
    @staticmethod
    def list_worklogs(
        session: Session,
        *,
        date_from: date | None,
        date_to: date | None,
    ) -> WorklogsPublic:
        if (date_from is None) ^ (date_to is None):
            raise HTTPException(
                status_code=400,
                detail="date_from and date_to are both required when filtering",
            )
        start, _ = _range_bounds(date_from, date_to)
        summaries = build_summaries(
            session,
            date_from=date_from,
            date_to=date_to,
            only_pending=False,
            require_entries_in_range_when_filtered=start is not None,
        )
        return WorklogsPublic(data=summaries, count=len(summaries))

    @staticmethod
    def get_worklog(
        session: Session,
        worklog_id: uuid.UUID,
        date_from: date | None,
        date_to: date | None,
    ) -> WorklogDetailPublic:
        if (date_from is None) ^ (date_to is None):
            raise HTTPException(
                status_code=400,
                detail="date_from and date_to are both required when filtering",
            )
        wl = session.get(WorkLog, worklog_id)
        if not wl:
            raise HTTPException(status_code=404, detail="Worklog not found")
        task = session.get(Task, wl.task_id)
        usr = session.get(User, wl.freelancer_id)
        if not task or not usr:
            raise HTTPException(status_code=404, detail="Worklog not found")
        start, end = _range_bounds(date_from, date_to)
        q = select(TimeEntry).where(TimeEntry.worklog_id == worklog_id)
        raw_entries = list(session.exec(q).all())
        if start is not None and end is not None:
            entries = [
                e for e in raw_entries if _entry_in_range(e.worked_at, start, end)
            ]
        else:
            entries = raw_entries
        hours = sum(float(e.hours) for e in entries)
        rate = float(task.hourly_rate)
        pub_entries = [
            TimeEntryPublic(
                id=e.id,
                worklog_id=e.worklog_id,
                worked_at=_as_utc(e.worked_at),
                hours=float(e.hours),
                notes=e.notes,
            )
            for e in sorted(entries, key=lambda x: _as_utc(x.worked_at))
        ]
        return WorklogDetailPublic(
            id=wl.id,
            task_id=task.id,
            task_title=task.title,
            freelancer_id=usr.id,
            freelancer_email=str(usr.email),
            status=wl.status,
            created_at=wl.created_at,
            period_hours=hours,
            period_earned=hours * rate,
            entries=pub_entries,
        )
