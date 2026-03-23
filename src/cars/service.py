from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db.models import Car,User
from src.cars.schema import CarCreate, CarUpdate
from src.errors.customErrors import PassengerCannotManageCarException,InactiveOrBannedDriverException,DuplicatePlateNumberException,DriverCarOwnershipException,InvalidCarSeatsException



async def create_car(session: AsyncSession, current_user: User, data: CarCreate) -> Car:
    if current_user.role not in ["driver","admin"]:
        raise PassengerCannotManageCarException()

    stmt = select(Car).where(Car.plate_number == data.plate_number)
    result = await session.execute(stmt)
    existing_car = result.scalar_one_or_none()
    if existing_car:
        raise DuplicatePlateNumberException()

    stmt = select(Car).where(Car.driver_id == current_user.uid, Car.is_active == True)
    result = await session.execute(stmt)
    active_car = result.scalar_one_or_none()

    if active_car:
        active_car.is_active = False

    new_car = Car(
        driver_id=current_user.uid,
        model=data.model,
        plate_number=data.plate_number,
        total_seats=data.total_seats,
        is_active=True,
    )

    session.add(new_car)
    await session.commit()
    await session.refresh(new_car)

    return new_car


async def get_car(session: AsyncSession, car_id: int) -> Car | None:
    return await session.get(Car, car_id)


async def get_active_car(session: AsyncSession, current_user: User) -> Car | None:
    if current_user.role not in ["driver", "admin"]:
        raise PassengerCannotManageCarException()

    stmt = select(Car).where(
        Car.driver_id == current_user.uid,
        Car.is_active == True,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def update_car(session: AsyncSession, current_user: User, car: Car, data: CarUpdate) -> Car:
    if current_user.role != "admin" and car.driver_id != current_user.uid:
        raise DriverCarOwnershipException()

    payload = data.model_dump(exclude_unset=True)

    if "plate_number" in payload:
        stmt = select(Car).where(
            Car.plate_number == payload["plate_number"],
            Car.id != car.id,
        )
        result = await session.execute(stmt)
        duplicate_car = result.scalar_one_or_none()
        if duplicate_car:
            raise DuplicatePlateNumberException()

    if "is_active" in payload and payload["is_active"] is True:
        stmt = select(Car).where(
            Car.driver_id == car.driver_id,
            Car.id != car.id,
            Car.is_active == True,
        )
        result = await session.execute(stmt)
        for other in result.scalars():
            other.is_active = False

    if "total_seats" in payload:
        new_total_seats = payload["total_seats"]
        if new_total_seats < 1:
            raise InvalidCarSeatsException()


    for key, value in payload.items():
        setattr(car, key, value)

    await session.commit()
    await session.refresh(car)

    return car


async def delete_car(session: AsyncSession, current_user: User, car: Car) -> None:
    if current_user.role != "admin" and car.driver_id != current_user.uid:
        raise DriverCarOwnershipException()

    await session.delete(car)
    await session.commit()