from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

from src.db.models import TripStatus
from uuid import UUID


class TripBase(SQLModel):

    origin: str = Field(
        min_length=1,
        max_length=200,
        description="Trip start location"
    )

    destination: str = Field(
        min_length=1,
        max_length=200,
        description="Trip destination"
    )

    price_per_seat: float = Field(
        ge=0,
        description="Price per seat"
    )

    start_time: datetime = Field(
        description="Trip departure time"
    )

class TripCreate(TripBase):

    car_id: int = Field(
        ge=1,
        description="Car used for the trip"
    )

    available_seats: int = Field(
        ge=1,
        le=8,
        description="Available seats at trip creation"
    )

class TripUpdate(SQLModel):

    origin: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    destination: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    price_per_seat: Optional[float] = Field(
        default=None,
        ge=0
    )

    start_time: Optional[datetime] = None

    available_seats: Optional[int] = Field(
        default=None,
        ge=1,
        le=8
    )


class TripRead(TripBase):

    id: int

    driver_id: UUID
    car_id: int

    available_seats: int

    status: TripStatus

    created_at: datetime