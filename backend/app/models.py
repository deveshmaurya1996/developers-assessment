import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from pydantic import EmailStr
from sqlalchemy import Column, Numeric
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class Task(SQLModel, table=True):
    __tablename__ = "task"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255, index=True)
    description: str | None = Field(default=None, max_length=2000)
    hourly_rate: Decimal = Field(
        sa_column=Column(Numeric(12, 2), nullable=False),
        default=Decimal("0.00"),
    )
    worklogs: list["WorkLog"] = Relationship(back_populates="task")


class WorkLog(SQLModel, table=True):
    __tablename__ = "worklog"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    task_id: uuid.UUID = Field(foreign_key="task.id", ondelete="CASCADE", index=True)
    freelancer_id: uuid.UUID = Field(
        foreign_key="user.id", ondelete="CASCADE", index=True
    )
    status: str = Field(default="pending", max_length=32, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), index=True
    )
    task: Task | None = Relationship(back_populates="worklogs")
    freelancer: User | None = Relationship()
    entries: list["TimeEntry"] = Relationship(
        back_populates="worklog", cascade_delete=True
    )


class TimeEntry(SQLModel, table=True):
    __tablename__ = "time_entry"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    worklog_id: uuid.UUID = Field(
        foreign_key="worklog.id", ondelete="CASCADE", index=True
    )
    worked_at: datetime = Field(index=True)
    hours: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    notes: str | None = Field(default=None, max_length=2000)
    worklog: WorkLog | None = Relationship(back_populates="entries")


class PaymentBatch(SQLModel, table=True):
    __tablename__ = "payment_batch"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_from: date
    date_to: date
    total_amount: Decimal = Field(sa_column=Column(Numeric(14, 2), nullable=False))
    worklog_count: int = Field(default=0)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), index=True
    )
    created_by_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )


class PaymentBatchWorklog(SQLModel, table=True):
    __tablename__ = "payment_batch_worklog"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    batch_id: uuid.UUID = Field(
        foreign_key="payment_batch.id", ondelete="CASCADE", index=True
    )
    worklog_id: uuid.UUID = Field(foreign_key="worklog.id", ondelete="CASCADE")
    amount: Decimal = Field(sa_column=Column(Numeric(14, 2), nullable=False))


class TimeEntryPublic(SQLModel):
    id: uuid.UUID
    worklog_id: uuid.UUID
    worked_at: datetime
    hours: float
    notes: str | None


class WorklogSummaryPublic(SQLModel):
    id: uuid.UUID
    task_id: uuid.UUID
    task_title: str
    freelancer_id: uuid.UUID
    freelancer_email: str
    period_hours: float
    period_earned: float
    status: str
    time_entry_count: int


class WorklogsPublic(SQLModel):
    data: list[WorklogSummaryPublic]
    count: int


class WorklogDetailPublic(SQLModel):
    id: uuid.UUID
    task_id: uuid.UUID
    task_title: str
    freelancer_id: uuid.UUID
    freelancer_email: str
    status: str
    created_at: datetime
    period_hours: float
    period_earned: float
    entries: list[TimeEntryPublic]


class PaymentPreviewPublic(SQLModel):
    data: list[WorklogSummaryPublic]
    count: int
    total_amount: float


class PaymentBatchCreatedPublic(SQLModel):
    batch_id: uuid.UUID
    total_amount: float
    worklog_count: int
