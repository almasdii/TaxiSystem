
from datetime import datetime
from enum import Enum
from typing import Optional,List
from uuid import UUID, uuid4
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Column, Field, Relationship, SQLModel
from sqlalchemy.dialects import postgresql as pg
from enum import Enum


class TripStatus(str, Enum):
    planned = "planned"
    completed = "completed"
    cancelled = "cancelled"



class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class PaymentStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class RoutePointType(str, Enum):
    pickup = "pickup"
    dropoff = "dropoff"
    stop = "stop"

class UserRole(str, Enum):
    admin = "admin"
    driver = "driver"
    passenger = "passenger"


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: UUID = Field(
        sa_column=Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    )
    email: str = Field(nullable=False, unique=True, index=True)
    username: str = Field(nullable=False)
    surname: str = Field(nullable=True)
    phone: str = Field(nullable=False)
    hashed_password: str = Field()
    role: UserRole = Field(
        sa_column=Column(
            pg.ENUM(UserRole, name="user_role"),
            nullable=False,
            server_default="passenger"
        )
    )

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    cars: list["Car"] = Relationship(
        back_populates="driver",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    trips_as_driver: list["Trip"] = Relationship(
        back_populates="driver",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    bookings_as_passenger: list["Booking"] = Relationship(
        back_populates="passenger",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    reviews_written: List["Review"] = Relationship(
        back_populates="reviewer",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "foreign_keys": "[Review.reviewer_id]",
        },
    )

    reviews_received: List["Review"] = Relationship(
        back_populates="reviewee",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "foreign_keys": "[Review.reviewee_id]",
        },
    )

class Car(SQLModel, table=True):
    __tablename__ = "cars"

    id: Optional[int] = Field(default=None, primary_key=True)

    driver_id: UUID = Field(foreign_key="users.uid", nullable=False, index=True)

    model: str = Field(min_length=1, max_length=100, nullable=False)

    plate_number: str = Field(
        min_length=3,
        max_length=30,
        nullable=False,
        unique=True,
        index=True,
    )

    total_seats: int = Field(nullable=False, ge=1, le=8)
    is_active: bool = Field(default=True, nullable=False)


    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    driver: Optional["User"] = Relationship(
        back_populates="cars",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    trips: list["Trip"] = Relationship(
        back_populates="car",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Trip(SQLModel, table=True):
    __tablename__ = "trips"

    id: Optional[int] = Field(default=None, primary_key=True)

    driver_id: UUID = Field(
        foreign_key="users.uid",
        nullable=False,
        index=True
    )

    car_id: int = Field(
        foreign_key="cars.id",
        nullable=False,
        index=True
    )

    origin: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        index=True
    )

    destination: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        index=True
    )

    price_per_seat: float = Field(
        nullable=False,
        ge=0
    )

    start_time: datetime = Field(
        nullable=False,
        index=True
    )

    available_seats: int = Field(
        nullable=False,
        ge=1
    )

    status: TripStatus = Field(
        default=TripStatus.planned,
        nullable=False
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    driver: Optional["User"] = Relationship(
        back_populates="trips_as_driver",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    car: Optional["Car"] = Relationship(
        back_populates="trips",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    route_points: list["RoutePoint"] = Relationship(
        back_populates="trip",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    bookings: list["Booking"] = Relationship(
        back_populates="trip",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    reviews: list["Review"] = Relationship(
        back_populates="trip",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

class RoutePoint(SQLModel, table=True):
    __tablename__ = "route_points"

    id: Optional[int] = Field(default=None, primary_key=True)

    trip_id: int = Field(
        foreign_key="trips.id",
        nullable=False,
        index=True
    )

    location: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        index=True
    )

    time: datetime = Field(nullable=False)

    order: int = Field(
        nullable=False,
        ge=1
    )

    type: RoutePointType = Field(
        default=RoutePointType.stop,
        nullable=False
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    trip: Optional["Trip"] = Relationship(
        back_populates="route_points",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: Optional[int] = Field(default=None, primary_key=True)

    passenger_id: UUID = Field(
        foreign_key="users.uid",
        nullable=False,
        index=True
    )

    trip_id: int = Field(
        foreign_key="trips.id",
        nullable=False,
        index=True
    )

    pickup_route_id: int = Field(
        foreign_key="route_points.id",
        nullable=False
    )

    dropoff_route_id: int = Field(
        foreign_key="route_points.id",
        nullable=False
    )

    status: BookingStatus = Field(
        default=BookingStatus.confirmed,
        nullable=False
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    passenger: Optional["User"] = Relationship(
        back_populates="bookings_as_passenger",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    trip: Optional["Trip"] = Relationship(
        back_populates="bookings",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    payment: Optional["Payment"] = Relationship(
        back_populates="booking",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)

    booking_id: int = Field(
        foreign_key="bookings.id",
        nullable=False,
        index=True
    )

    amount: float = Field(
        nullable=False,
        gt=0
    )

    status: PaymentStatus = Field(
        default=PaymentStatus.pending,
        nullable=False
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    booking: Optional["Booking"] = Relationship(
        back_populates="payment",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: Optional[int] = Field(default=None, primary_key=True)

    trip_id: int = Field(
        foreign_key="trips.id",
        nullable=False,
        index=True
    )

    reviewer_id: UUID = Field(
        foreign_key="users.uid",
        nullable=False,
        index=True
    )

    reviewee_id: UUID = Field(
        foreign_key="users.uid",
        nullable=False,
        index=True
    )

    message: str = Field(
        min_length=1,
        max_length=500,
        nullable=False
    )

    rate: int = Field(
        nullable=False,
        ge=1,
        le=5
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    reviewer: Optional["User"] = Relationship(
        back_populates="reviews_written",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "foreign_keys": "[Review.reviewer_id]",
        },
    )

    reviewee: Optional["User"] = Relationship(
        back_populates="reviews_received",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "foreign_keys": "[Review.reviewee_id]",
        },
    )

    trip: Optional["Trip"] = Relationship(
        back_populates="reviews",
        sa_relationship_kwargs={"lazy": "selectin"},
    )