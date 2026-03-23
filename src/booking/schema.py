from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from pydantic import BaseModel
from src.db.models import BookingStatus


class BookingBase(BaseModel):
    trip_id: int
    pickup_route_id: int
    dropoff_route_id: int

class BookingCreate(BookingBase):
    pass

class BookingRead(BookingBase):
    id: int
    passenger_id: str
    status: BookingStatus
    created_at: datetime

class BookingUpdate(SQLModel):
    status: Optional[BookingStatus] = None