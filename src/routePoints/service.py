from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db.models import RoutePoint, Trip, User
from src.routePoints.schema import RoutePointCreate, RoutePointUpdate

from src.errors.customErrors import (
    TripNotFoundException,
    DriverTripOwnershipException,
    DuplicateRouteOrderException,
    InvalidRoutePointTimeException,
    RoutePointNotFoundException,
    RoutePointOrderConflictException,
    TripAlreadyStartedException,
)

async def add_route_point(
    session: AsyncSession,
    current_user: User,
    trip_id: int,
    data: RoutePointCreate,
) -> RoutePoint:

    trip = await session.get(Trip, trip_id)

    if not trip:
        raise TripNotFoundException()

    if trip.driver_id != current_user.uid:
        raise DriverTripOwnershipException()

    if trip.start_time <= datetime.utcnow():
        raise TripAlreadyStartedException()

    if data.time > trip.start_time:
        raise InvalidRoutePointTimeException()

    stmt = select(RoutePoint).where(
        RoutePoint.trip_id == trip_id,
        RoutePoint.order == data.order
    )

    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise DuplicateRouteOrderException()

    rp = RoutePoint(
        trip_id=trip_id,
        location=data.location,
        time=data.time,
        order=data.order,
        type=data.type,
    )

    session.add(rp)

    await session.commit()
    await session.refresh(rp)

    return rp


async def list_route_points(
    session: AsyncSession,
    trip_id: int,
):

    stmt = (
        select(RoutePoint)
        .where(RoutePoint.trip_id == trip_id)
        .order_by(RoutePoint.order)
    )

    result = await session.execute(stmt)

    return result.scalars().all()


async def get_route_point(
    session: AsyncSession,
    rp_id: int,
) -> RoutePoint | None:

    return await session.get(RoutePoint, rp_id)




async def update_route_point(
    session: AsyncSession,
    current_user: User,
    rp: RoutePoint,
    data: RoutePointUpdate,
) -> RoutePoint:

    trip = await session.get(Trip, rp.trip_id)

    if not trip:
        raise TripNotFoundException()

    if trip.driver_id != current_user.uid:
        raise DriverTripOwnershipException()

    if trip.start_time <= datetime.utcnow():
        raise TripAlreadyStartedException()

    payload = data.model_dump(exclude_unset=True)

    if "order" in payload:

        stmt = select(RoutePoint).where(
            RoutePoint.trip_id == trip.id,
            RoutePoint.order == payload["order"],
            RoutePoint.id != rp.id
        )

        result = await session.execute(stmt)
        conflict = result.scalar_one_or_none()

        if conflict:
            raise RoutePointOrderConflictException()

    if "time" in payload:

        if payload["time"] > trip.start_time:
            raise InvalidRoutePointTimeException()

    for key, value in payload.items():
        setattr(rp, key, value)

    await session.commit()
    await session.refresh(rp)

    return rp




async def delete_route_point(
    session: AsyncSession,
    current_user: User,
    rp: RoutePoint,
):

    trip = await session.get(Trip, rp.trip_id)

    if not trip:
        raise TripNotFoundException()

    if trip.driver_id != current_user.uid:
        raise DriverTripOwnershipException()

    if trip.start_time <= datetime.utcnow():
        raise TripAlreadyStartedException()

    await session.delete(rp)

    await session.commit()