import uuid
from decimal import Decimal

from fastapi import HTTPException
from sqlmodel import Session

from app.api.routes.payments.schemas import PaymentBatchRequest
from app.api.routes.worklogs.service import build_summaries
from app.models import (
    PaymentBatch,
    PaymentBatchCreatedPublic,
    PaymentBatchWorklog,
    PaymentPreviewPublic,
    WorkLog,
    WorklogSummaryPublic,
)


def _apply_exclusions(
    summaries: list[WorklogSummaryPublic],
    excluded_worklog_ids: list[uuid.UUID],
    excluded_freelancer_ids: list[uuid.UUID],
) -> list[WorklogSummaryPublic]:
    ex_w = set(excluded_worklog_ids)
    ex_f = set(excluded_freelancer_ids)
    return [s for s in summaries if s.id not in ex_w and s.freelancer_id not in ex_f]


class PaymentService:
    @staticmethod
    def preview_payment(
        session: Session, body: PaymentBatchRequest
    ) -> PaymentPreviewPublic:
        if body.date_from > body.date_to:
            raise HTTPException(
                status_code=400, detail="date_from must be on or before date_to"
            )
        summaries = build_summaries(
            session,
            date_from=body.date_from,
            date_to=body.date_to,
            only_pending=True,
            require_entries_in_range_when_filtered=True,
        )
        sel = _apply_exclusions(
            summaries, body.excluded_worklog_ids, body.excluded_freelancer_ids
        )
        total = sum(s.period_earned for s in sel)
        return PaymentPreviewPublic(data=sel, count=len(sel), total_amount=total)

    @staticmethod
    def confirm_payment(
        session: Session, body: PaymentBatchRequest, actor_id: uuid.UUID
    ) -> PaymentBatchCreatedPublic:
        if body.date_from > body.date_to:
            raise HTTPException(
                status_code=400, detail="date_from must be on or before date_to"
            )
        summaries = build_summaries(
            session,
            date_from=body.date_from,
            date_to=body.date_to,
            only_pending=True,
            require_entries_in_range_when_filtered=True,
        )
        sel = _apply_exclusions(
            summaries, body.excluded_worklog_ids, body.excluded_freelancer_ids
        )
        if not sel:
            raise HTTPException(
                status_code=400, detail="No worklogs selected for payment"
            )
        for s in sel:
            wl = session.get(WorkLog, s.id)
            if not wl or wl.status != "pending":
                raise HTTPException(
                    status_code=409, detail="One or more worklogs are no longer payable"
                )

        line_amounts: list[Decimal] = []
        for s in sel:
            amt = Decimal(str(round(s.period_earned, 2)))
            line_amounts.append(amt)
        batch_total = sum(line_amounts, start=Decimal("0"))

        batch = PaymentBatch(
            date_from=body.date_from,
            date_to=body.date_to,
            total_amount=batch_total,
            worklog_count=len(sel),
            created_by_id=actor_id,
        )
        session.add(batch)
        session.flush()
        for s, amt in zip(sel, line_amounts, strict=True):
            wl = session.get(WorkLog, s.id)
            if wl:
                wl.status = "paid"
                session.add(wl)
            session.add(
                PaymentBatchWorklog(batch_id=batch.id, worklog_id=s.id, amount=amt)
            )
        session.commit()
        session.refresh(batch)
        return PaymentBatchCreatedPublic(
            batch_id=batch.id,
            total_amount=float(batch_total),
            worklog_count=len(sel),
        )
