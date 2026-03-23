from datetime import datetime
from sqlmodel import SQLModel

from src.db.models import PaymentStatus
from pydantic import BaseModel


class PaymentBase(BaseModel):
    booking_id: int
    amount: float

class PaymentCreate(PaymentBase):
    pass

class PaymentRead(PaymentBase):
    id: int
    status: PaymentStatus
    created_at: datetime