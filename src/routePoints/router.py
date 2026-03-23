from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.utils import AccessTokenBearer, get_current_user
from src.db.models import User
from src.db.session import get_session
from src.dependencies import allow_driver, allow_driver_or_passenger
from src.routePoints.schema import RoutePointCreate, RoutePointRead, RoutePointUpdate
from src.routePoints.service import (
    add_route_point,
    list_route_points,
    get_route_point,
    update_route_point,
    delete_route_point,
)
from src.errors.customErrors import RoutePointNotFoundException

router = APIRouter(prefix="/routepoints", tags=["routepoints"])

access_token = AccessTokenBearer()


@router.post(
    "/trips/{trip_id}",
    response_model=RoutePointRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(access_token), Depends(allow_driver)],
)
async def create(
    trip_id: int,
    data: RoutePointCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await add_route_point(session, current_user, trip_id, data)


@router.get(
    "/trips/{trip_id}",
    response_model=list[RoutePointRead],
    dependencies=[Depends(access_token), Depends(allow_driver_or_passenger)],
)
async def list_for_trip(
    trip_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await list_route_points(session, trip_id)


@router.patch(
    "/{rp_id}",
    response_model=RoutePointRead,
    dependencies=[Depends(access_token), Depends(allow_driver)],
)
async def patch(
    rp_id: int,
    data: RoutePointUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    rp = await get_route_point(session, rp_id)
    if not rp:
        raise RoutePointNotFoundException()

    return await update_route_point(session, current_user, rp, data)


@router.delete(
    "/{rp_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(access_token), Depends(allow_driver)],
)
async def remove(
    rp_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    rp = await get_route_point(session, rp_id)
    if not rp:
        raise RoutePointNotFoundException()

    await delete_route_point(session, current_user, rp)