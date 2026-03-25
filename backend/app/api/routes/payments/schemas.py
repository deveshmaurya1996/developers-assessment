import uuid
from datetime import date

from pydantic import field_validator
from sqlmodel import Field, SQLModel


class PaymentBatchRequest(SQLModel):
    date_from: date
    date_to: date
    excluded_worklog_ids: list[uuid.UUID] = Field(default_factory=list)
    excluded_freelancer_ids: list[uuid.UUID] = Field(default_factory=list)

    @field_validator("date_from")
    @classmethod
    def validate_date_from(cls, value: date) -> date:
        if value is None:
            raise ValueError("date_from is required")
        if not isinstance(value, date):
            raise ValueError("date_from must be a date")
        return value

    @field_validator("date_to")
    @classmethod
    def validate_date_to(cls, value: date) -> date:
        if value is None:
            raise ValueError("date_to is required")
        if not isinstance(value, date):
            raise ValueError("date_to must be a date")
        return value

    @field_validator("excluded_worklog_ids", mode="before")
    @classmethod
    def validate_excluded_worklog_ids(cls, value: object) -> list:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("excluded_worklog_ids must be a list")
        out: list[uuid.UUID] = []
        for item in value:
            if isinstance(item, uuid.UUID):
                out.append(item)
            elif isinstance(item, str):
                try:
                    out.append(uuid.UUID(item))
                except ValueError as e:
                    raise ValueError(
                        "excluded_worklog_ids must contain only UUID values"
                    ) from e
            else:
                raise ValueError("excluded_worklog_ids must contain only UUID values")
        return out

    @field_validator("excluded_freelancer_ids", mode="before")
    @classmethod
    def validate_excluded_freelancer_ids(cls, value: object) -> list:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("excluded_freelancer_ids must be a list")
        out: list[uuid.UUID] = []
        for item in value:
            if isinstance(item, uuid.UUID):
                out.append(item)
            elif isinstance(item, str):
                try:
                    out.append(uuid.UUID(item))
                except ValueError as e:
                    raise ValueError(
                        "excluded_freelancer_ids must contain only UUID values"
                    ) from e
            else:
                raise ValueError(
                    "excluded_freelancer_ids must contain only UUID values"
                )
        return out
