from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import CurrentSuperuser, SessionDep, get_current_active_superuser
from app.api.routes.payments.schemas import PaymentBatchRequest
from app.api.routes.payments.service import PaymentService
from app.models import PaymentBatchCreatedPublic, PaymentPreviewPublic

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    dependencies=[Depends(get_current_active_superuser)],
)


@router.post("/preview", response_model=PaymentPreviewPublic)
def preview_payment_batch(session: SessionDep, body: PaymentBatchRequest) -> Any:
    return PaymentService.preview_payment(session, body)


@router.post("/confirm", response_model=PaymentBatchCreatedPublic)
def confirm_payment_batch(
    session: SessionDep, current_user: CurrentSuperuser, body: PaymentBatchRequest
) -> Any:
    return PaymentService.confirm_payment(session, body, current_user.id)
