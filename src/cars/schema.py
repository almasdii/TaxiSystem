from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID

from sqlmodel import SQLModel, Field


class CarBase(BaseModel):
    model: str = Field(
        min_length=1,
        max_length=50,
        description="Car model name",
    )
    plate_number: str = Field(
        min_length=3,
        max_length=12,
        description="Unique license plate number",
    )
    total_seats: int = Field(
        ge=1,
        le=8,
        description="Total number of seats in car",
    )


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    model: Optional[str] = Field(default=None, min_length=1, max_length=50)
    plate_number: Optional[str] = Field(default=None, min_length=3, max_length=12)
    total_seats: Optional[int] = Field(default=None, ge=1, le=8)
    is_active: Optional[bool] = None


class CarRead(CarBase):
    id: int
    driver_id: UUID
    is_active: bool
    created_at: datetime