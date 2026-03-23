from __future__ import annotations

from fastapi import APIRouter, status,Depends

from src.db.models import Car,User
from src.dependencies import AsyncSessionDep, get_or_404, allow_admin, allow_driver, allow_driver_or_passenger, allow_passenger
from src.cars.schema import CarCreate, CarRead, CarUpdate
from src.auth.utils import AccessTokenBearer,RefreshTokenBearer,get_current_user
from src.errors.customErrors import DriverCarOwnershipException,InvalidCarSeatsException,CarNotFoundException

from src.cars.service import (
    create_car,
    get_active_car,
    update_car,
    delete_car,
)

router = APIRouter(prefix="/cars", tags=["cars"])


access_token = AccessTokenBearer()


@router.post(
    "",
    response_model=CarRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(access_token), Depends(allow_driver)],
)
async def create(
    data: CarCreate,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    return await create_car(session, current_user, data)


@router.get(
    "/me/active",
    response_model=CarRead,
    dependencies=[Depends(access_token), Depends(allow_driver)],
)
async def active(
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    car = await get_active_car(session, current_user)
    if not car:
        raise CarNotFoundException()
    return car


@router.get(
    "/{car_id}",
    response_model=CarRead,
    dependencies=[Depends(access_token)],
)
async def read(
    car_id: int,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    car = await get_or_404(Car, car_id, session)

    if current_user.role != "admin" and car.driver_id != current_user.uid:
        raise DriverCarOwnershipException()

    return car


@router.patch(
    "/{car_id}",
    response_model=CarRead,
    dependencies=[Depends(access_token), Depends(allow_driver)],
)
async def patch(
    car_id: int,
    data: CarUpdate,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    car = await get_or_404(Car, car_id, session)
    return await update_car(session, current_user, car, data)


@router.delete(
    "/{car_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(access_token), Depends(allow_driver)],
)
async def remove(
    car_id: int,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    car = await get_or_404(Car, car_id, session)
    await delete_car(session, current_user, car)
    return None