from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db.models import (
    Booking,
    BookingStatus,
    Payment,
    PaymentStatus,
    User,
)


async def create_payment(
    session: AsyncSession,
    current_user: User,
    data,
) -> Payment:

    booking = await session.get(Booking, data.booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.passenger_id != current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot pay for another user's booking",
        )

    if booking.status != BookingStatus.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is not active",
        )

    res = await session.execute(
        select(Payment).where(
            Payment.booking_id == data.booking_id,
            Payment.status == PaymentStatus.completed,
        )
    )

    existing = res.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking already paid",
        )

    if data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive",
        )

    payment = Payment(
        booking_id=data.booking_id,
        amount=data.amount,
        status=PaymentStatus.completed,
    )

    session.add(payment)

    await session.commit()
    await session.refresh(payment)

    return payment


async def get_payment(
    session: AsyncSession,
    current_user: User,
    payment_id: int,
) -> Payment:

    payment = await session.get(Payment, payment_id)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    booking = await session.get(Booking, payment.booking_id)

    if booking.passenger_id != current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access this payment",
        )

    return payment

async def list_payments(
    session: AsyncSession,
    current_user: User,
    booking_id: int,
):

    booking = await session.get(Booking, booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.passenger_id != current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access payments for this booking",
        )

    res = await session.execute(
        select(Payment).where(Payment.booking_id == booking_id)
    )

    return res.scalars().all()