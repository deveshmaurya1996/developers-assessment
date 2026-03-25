from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlmodel import Session, select

from app import crud
from app.core.config import settings
from app.crud import get_user_by_email
from app.models import Task, TimeEntry, User, UserCreate, WorkLog


def seed_payment_demo(session: Session) -> None:
    if session.exec(select(Task).limit(1)).first():
        return
    fl_email = "freelancer@example.com"
    freelancer = get_user_by_email(session=session, email=fl_email)
    if not freelancer:
        freelancer = crud.create_user(
            session=session,
            user_create=UserCreate(
                email=fl_email,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                full_name="Demo Freelancer",
            ),
        )
    admin = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not admin:
        return

    t1 = Task(
        title="API integration",
        description="Payment dashboard APIs",
        hourly_rate=Decimal("85.00"),
    )
    t2 = Task(
        title="UI polish",
        description="Admin dashboard UX",
        hourly_rate=Decimal("70.00"),
    )
    session.add(t1)
    session.add(t2)
    session.commit()
    session.refresh(t1)
    session.refresh(t2)

    now = datetime.now(timezone.utc)
    wl1 = WorkLog(task_id=t1.id, freelancer_id=freelancer.id, status="pending")
    wl2 = WorkLog(task_id=t2.id, freelancer_id=admin.id, status="pending")
    wl3 = WorkLog(task_id=t1.id, freelancer_id=freelancer.id, status="paid")
    session.add(wl1)
    session.add(wl2)
    session.add(wl3)
    session.commit()
    session.refresh(wl1)
    session.refresh(wl2)
    session.refresh(wl3)

    to_add = [
        TimeEntry(
            worklog_id=wl1.id,
            worked_at=now - timedelta(days=5),
            hours=Decimal("4.00"),
            notes="Initial wiring",
        ),
        TimeEntry(
            worklog_id=wl1.id,
            worked_at=now - timedelta(days=2),
            hours=Decimal("3.50"),
            notes="Refinements",
        ),
        TimeEntry(
            worklog_id=wl2.id,
            worked_at=now - timedelta(days=1),
            hours=Decimal("6.00"),
        ),
        TimeEntry(
            worklog_id=wl3.id,
            worked_at=now - timedelta(days=20),
            hours=Decimal("2.00"),
        ),
    ]
    for row in to_add:
        session.add(row)
    session.commit()
