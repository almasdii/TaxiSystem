from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db.models import Trip, Car, User
from src.db.models import TripStatus
from src.trips.schema import TripCreate, TripUpdate

from src.errors.customErrors import (
    DriverWithoutCarException,
    DriverCarOwnershipException,
    InvalidTripSeatsException,
    TripAlreadyStartedException,
    InvalidTripRouteException,
    DriverTripOwnershipException,
    TripAlreadyCompletedException,
)



async def create_trip(session: AsyncSession, current_user: User, data: TripCreate) -> Trip:

    stmt = select(Car).where(Car.driver_id == current_user.uid)
    result = await session.execute(stmt)
    driver_car = result.scalars().first()

    if not driver_car:
        raise DriverWithoutCarException()

    if driver_car.id != data.car_id:
        raise DriverCarOwnershipException()

    if data.available_seats > driver_car.total_seats:
        raise InvalidTripSeatsException()

    if data.start_time <= datetime.utcnow():
        raise TripAlreadyStartedException()

    if data.origin.lower() == data.destination.lower():
        raise InvalidTripRouteException()

    new_trip = Trip(
        driver_id=current_user.uid,
        car_id=data.car_id,
        origin=data.origin,
        destination=data.destination,
        price_per_seat=data.price_per_seat,
        start_time=data.start_time,
        available_seats=data.available_seats,
        status=TripStatus.planned,
    )

    session.add(new_trip)
    await session.commit()
    await session.refresh(new_trip)

    return new_trip


async def get_trip(session: AsyncSession, trip_id: int) -> Trip | None:
    return await session.get(Trip, trip_id)



async def list_trips(session: AsyncSession, limit: int, offset: int):
    stmt = select(Trip).limit(limit).offset(offset)
    result = await session.execute(stmt)
    return result.scalars().all()


async def list_available_trips(session: AsyncSession, limit: int, offset: int):
    stmt = select(Trip).where(
        Trip.status == TripStatus.planned,
        Trip.available_seats > 0
    ).limit(limit).offset(offset)

    result = await session.execute(stmt)
    return result.scalars().all()



async def update_trip(session: AsyncSession, current_user: User, trip: Trip, data: TripUpdate) -> Trip:

    if trip.driver_id != current_user.uid:
        raise DriverTripOwnershipException()

    if trip.status == TripStatus.completed:
        raise TripAlreadyCompletedException()

    payload = data.model_dump(exclude_unset=True)

    if "origin" in payload and "destination" in payload:
        if payload["origin"].lower() == payload["destination"].lower():
            raise InvalidTripRouteException()

    if "start_time" in payload:
        if payload["start_time"] <= datetime.utcnow():
            raise TripAlreadyStartedException()

    if "available_seats" in payload:
        car = await session.get(Car, trip.car_id)

        if payload["available_seats"] > car.total_seats:
            raise InvalidTripSeatsException()

    for key, value in payload.items():
        setattr(trip, key, value)

    await session.commit()
    await session.refresh(trip)

    return trip



async def delete_trip(session: AsyncSession, current_user: User, trip: Trip):

    if trip.driver_id != current_user.uid:
        raise DriverTripOwnershipException()

    if trip.status == TripStatus.completed:
        raise TripAlreadyCompletedException()

    await session.delete(trip)
    await session.commit()



async def mark_trip_completed(session: AsyncSession, current_user: User, trip: Trip) -> Trip:

    if trip.driver_id != current_user.uid:
        raise DriverTripOwnershipException()

    if trip.status == TripStatus.completed:
        raise TripAlreadyCompletedException()

    trip.status = TripStatus.completed

    await session.commit()
    await session.refresh(trip)

    return trip


async def search_trips_by_routepoints(session: AsyncSession, from_location: str, to_location: str):

    from src.db.models import RoutePoint

    stmt = (
        select(Trip)
        .join(RoutePoint)
        .where(RoutePoint.location.ilike(f"%{from_location}%"))
        .where(RoutePoint.location.ilike(f"%{to_location}%"))
        .where(Trip.status == TripStatus.planned)
    )

    result = await session.execute(stmt)
    return result.scalars().all()