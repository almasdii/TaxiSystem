from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from uuid import UUID

from src.db.models import (
    Booking,
    BookingStatus,
    Review,
    Trip,
    TripStatus,
    User,
)

from src.reviews.schema import ReviewCreate, ReviewUpdate
async def _is_passenger_in_trip(
    session: AsyncSession,
    trip_id: int,
    user_id: UUID,
) -> bool:

    res = await session.execute(
        select(Booking).where(
            Booking.trip_id == trip_id,
            Booking.passenger_id == user_id,
            Booking.status != BookingStatus.cancelled,
        )
    )

    return res.scalar_one_or_none() is not None
async def create_review(
    session: AsyncSession,
    data: ReviewCreate,
) -> Review:

    if data.reviewer_id == data.reviewee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviewer and reviewee must be different",
        )

    trip = await session.get(Trip, data.trip_id)

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    if trip.status != TripStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip must be completed to leave a review",
        )

    reviewer = await session.get(User, data.reviewer_id)
    reviewee = await session.get(User, data.reviewee_id)

    if not reviewer or not reviewee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    reviewer_is_driver = trip.driver_id == data.reviewer_id
    reviewer_is_passenger = await _is_passenger_in_trip(
        session, trip.id, data.reviewer_id
    )

    if not (reviewer_is_driver or reviewer_is_passenger):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviewer did not participate in this trip",
        )

    reviewee_is_driver = trip.driver_id == data.reviewee_id
    reviewee_is_passenger = await _is_passenger_in_trip(
        session, trip.id, data.reviewee_id
    )

    if not (reviewee_is_driver or reviewee_is_passenger):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviewee did not participate in this trip",
        )
    if reviewer_is_driver and reviewee_is_driver:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver cannot review himself",
        )
    if reviewer_is_passenger and reviewee_is_passenger:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passenger cannot review another passenger",
        )
    res = await session.execute(
        select(Review).where(
            Review.trip_id == data.trip_id,
            Review.reviewer_id == data.reviewer_id,
            Review.reviewee_id == data.reviewee_id,
        )
    )

    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Review already exists",
        )

    review = Review(**data.model_dump())

    session.add(review)

    await session.commit()
    await session.refresh(review)

    return review

async def get_review(
    session: AsyncSession,
    review_id: int,
) -> Review | None:

    return await session.get(Review, review_id)

async def list_reviews_about_user(
    session: AsyncSession,
    user_id: UUID,
) -> list[Review]:

    res = await session.execute(
        select(Review).where(Review.reviewee_id == user_id)
    )

    return res.scalars().all()

async def update_review(
    session: AsyncSession,
    review: Review,
    data: ReviewUpdate,
    editor_id: UUID,
) -> Review:

    if editor_id != review.reviewer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only reviewer can update this review",
        )

    payload = data.model_dump(exclude_unset=True)

    for key, value in payload.items():
        setattr(review, key, value)

    await session.commit()
    await session.refresh(review)

    return review

async def delete_review(
    session: AsyncSession,
    review: Review,
    deleter_id: UUID,
) -> None:

    if deleter_id != review.reviewer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only reviewer can delete this review",
        )

    await session.delete(review)

    await session.commit()