from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.auth.utils import AccessTokenBearer, get_current_user
from src.db.models import User
from src.dependencies import AsyncSessionDep
from src.reviews.schema import ReviewCreate, ReviewRead, ReviewUpdate
from src.reviews.service import (
    create_review,
    delete_review,
    get_review,
    list_reviews_about_user,
    update_review,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])

access_token = AccessTokenBearer()


@router.post(
    "",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(access_token)],
)
async def create(
    data: ReviewCreate,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    return await create_review(session, current_user, data)


@router.get(
    "/users/{user_id}",
    response_model=list[ReviewRead],
)
async def about_user(
    user_id: UUID,
    session: AsyncSessionDep,
):
    return await list_reviews_about_user(session, user_id)


@router.patch(
    "/{review_id}",
    response_model=ReviewRead,
    dependencies=[Depends(access_token)],
)
async def patch(
    review_id: int,
    data: ReviewUpdate,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    review = await get_review(session, review_id)

    return await update_review(session, current_user, review, data)



@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(access_token)],
)
async def remove(
    review_id: int,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    review = await get_review(session, review_id)

    await delete_review(session, current_user, review)