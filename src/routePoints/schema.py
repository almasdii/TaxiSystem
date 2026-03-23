from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from src.db.models import RoutePointType
from pydantic import BaseModel


class RoutePointBase(BaseModel):
    location: str
    time: datetime
    order: int
    type: RoutePointType = RoutePointType.stop



class RoutePointCreate(RoutePointBase):
    pass

class RoutePointUpdate(BaseModel):
    location: Optional[str] = None
    time: Optional[datetime] = None
    order: Optional[int] = None
    type: Optional[RoutePointType] = None

class RoutePointRead(RoutePointBase):
    id: int
    trip_id: int
    created_at: datetime