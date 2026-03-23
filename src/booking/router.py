from fastapi import APIRouter, Depends, status

from src.auth.utils import AccessTokenBearer, get_current_user
from src.db.models import Booking, User
from src.dependencies import AsyncSessionDep, get_or_404, allow_passenger, allow_driver
from src.booking.schema import BookingCreate, BookingRead
from src.booking.service import (
    create_booking,
    list_my_bookings,
    list_trip_bookings,
    cancel_booking,
)

router = APIRouter(prefix="/bookings", tags=["bookings"])

access_token = AccessTokenBearer()



@router.post(
    "",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(access_token), Depends(allow_passenger)],
)
async def create(
    data: BookingCreate,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    return await create_booking(session, current_user, data)



@router.get(
    "/me",
    response_model=list[BookingRead],
    dependencies=[Depends(access_token)],
)
async def my_bookings(
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    return await list_my_bookings(session, current_user)



@router.get(
    "/trips/{trip_id}",
    response_model=list[BookingRead],
    dependencies=[Depends(access_token), Depends(allow_driver)],
)
async def trip_bookings(
    trip_id: int,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    return await list_trip_bookings(session, current_user, trip_id)



@router.post(
    "/{booking_id}/cancel",
    response_model=BookingRead,
    dependencies=[Depends(access_token)],
)
async def cancel(
    booking_id: int,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    booking = await get_or_404(Booking, booking_id, session)

    return await cancel_booking(session, current_user, booking)