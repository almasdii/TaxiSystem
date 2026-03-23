from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel, Field


class ReviewBase(SQLModel):
    message: str = Field(
        min_length=1,
        max_length=1000
    )

    rate: int = Field(
        ge=1,
        le=5
    )


class ReviewCreate(ReviewBase):
    trip_id: int
    reviewee_id: UUID


class ReviewUpdate(SQLModel):
    message: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    rate: Optional[int] = Field(default=None, ge=1, le=5)


class ReviewRead(ReviewBase):
    id: int
    trip_id: int
    reviewer_id: UUID
    reviewee_id: UUID
    created_at: datetime