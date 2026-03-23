from fastapi import APIRouter, Depends, status

from src.auth.utils import AccessTokenBearer, get_current_user
from src.db.models import Payment, User
from src.dependencies import AsyncSessionDep
from src.payments.schema import PaymentCreate, PaymentRead
from src.payments.service import (
    create_payment,
    get_payment,
    list_payments,
)

router = APIRouter(prefix="/payments", tags=["payments"])

access_token = AccessTokenBearer()


@router.post(
    "",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(access_token)],
)
async def create(
    data: PaymentCreate,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    return await create_payment(session, current_user, data)

@router.get(
    "/{payment_id}",
    response_model=PaymentRead,
    dependencies=[Depends(access_token)],
)
async def read(
    payment_id: int,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    return await get_payment(session, current_user, payment_id)


@router.get(
    "/booking/{booking_id}",
    response_model=list[PaymentRead],
    dependencies=[Depends(access_token)],
)
async def list_for_booking(
    booking_id: int,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    return await list_payments(session, current_user, booking_id)