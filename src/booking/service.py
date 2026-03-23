from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db.models import (
    Booking,
    BookingStatus,
    RoutePoint,
    Trip,
    TripStatus,
    User,
)

from src.booking.schema import BookingCreate

from src.errors.customErrors import (
    TripNotFoundException,
    RoutePointNotFoundException,
    InvalidRoutePointsException,
    PickupAfterDropoffException,
    TripAlreadyCompletedException,
    NoSeatsAvailableException,
    PassengerOwnTripException,
    DuplicateBookingException,
    BookingOwnershipException,
    BookingAlreadyCancelledException,
)



async def create_booking(
    session: AsyncSession,
    current_user: User,
    data: BookingCreate,
) -> Booking:

    async with session.begin():

        pickup = await session.get(RoutePoint, data.pickup_route_id)
        dropoff = await session.get(RoutePoint, data.dropoff_route_id)

        if not pickup or not dropoff:
            raise RoutePointNotFoundException()

        if pickup.trip_id != data.trip_id or dropoff.trip_id != data.trip_id:
            raise InvalidRoutePointsException()

        if pickup.order >= dropoff.order:
            raise PickupAfterDropoffException()

        res = await session.execute(
            select(Trip)
            .where(Trip.id == data.trip_id)
            .with_for_update()
        )

        trip = res.scalar_one_or_none()

        if not trip:
            raise TripNotFoundException()

        if trip.status != TripStatus.planned:
            raise TripAlreadyCompletedException()

        if trip.driver_id == current_user.uid:
            raise PassengerOwnTripException()

        if trip.available_seats <= 0:
            raise NoSeatsAvailableException()

        res = await session.execute(
            select(Booking).where(
                Booking.trip_id == data.trip_id,
                Booking.passenger_id == current_user.uid,
                Booking.status == BookingStatus.confirmed,
            )
        )

        existing = res.scalar_one_or_none()

        if existing:
            raise DuplicateBookingException()

        trip.available_seats -= 1

        booking = Booking(
            passenger_id=current_user.uid,
            trip_id=data.trip_id,
            pickup_route_id=data.pickup_route_id,
            dropoff_route_id=data.dropoff_route_id,
            status=BookingStatus.confirmed,
        )

        session.add(booking)

        await session.flush()

    await session.refresh(booking)

    return booking


async def get_booking(
    session: AsyncSession,
    booking_id: int,
) -> Booking | None:

    return await session.get(Booking, booking_id)


async def list_my_bookings(
    session: AsyncSession,
    current_user: User,
):

    res = await session.execute(
        select(Booking).where(
            Booking.passenger_id == current_user.uid
        )
    )

    return res.scalars().all()


async def list_trip_bookings(
    session: AsyncSession,
    current_user: User,
    trip_id: int,
):

    trip = await session.get(Trip, trip_id)

    if not trip:
        raise TripNotFoundException()

    if trip.driver_id != current_user.uid:
        raise BookingOwnershipException()

    res = await session.execute(
        select(Booking).where(Booking.trip_id == trip_id)
    )

    return res.scalars().all()

async def cancel_booking(
    session: AsyncSession,
    current_user: User,
    booking: Booking,
) -> Booking:

    if booking.status == BookingStatus.cancelled:
        raise BookingAlreadyCancelledException()

    if booking.passenger_id != current_user.uid:
        raise BookingOwnershipException()

    async def _do_cancel():

        res = await session.execute(
            select(Trip)
            .where(Trip.id == booking.trip_id)
            .with_for_update()
        )

        trip = res.scalar_one_or_none()

        if not trip:
            raise TripNotFoundException()

        booking.status = BookingStatus.cancelled
        trip.available_seats += 1

        session.add(booking)
        session.add(trip)

        await session.flush()

    if session.in_transaction():
        await _do_cancel()
    else:
        async with session.begin():
            await _do_cancel()

    await session.refresh(booking)

    return booking