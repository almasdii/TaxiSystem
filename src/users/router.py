from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import select
from src.errors.customErrors import UserNotFoundByEmail,AccessForbidden

from src.db.models import User
from src.dependencies import AsyncSessionDep,  pagination_params,allow_admin,allow_driver,allow_driver_or_passenger,allow_passenger
from src.users.schema import UserCreateModel, UserRead, UserUpdate
from src.users.service import UserService
from src.auth.utils import AccessTokenBearer, RefreshTokenBearer, get_current_user
router = APIRouter(prefix="/users", tags=["users"])

user_service = (UserService())
access_token = (AccessTokenBearer())
refresh_token = (RefreshTokenBearer())


@router.get("", response_model=list[UserRead], dependencies=[Depends(access_token), Depends(allow_admin)])
async def list_all(
    session: AsyncSessionDep,
    pag: tuple[int, int] = Depends(pagination_params),
):
    limit, offset = pag
    stmt = select(User).limit(limit).offset(offset)
    res = await session.execute(stmt)
    return list(res.scalars().all())

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(access_token)])
async def remove_me(
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    await user_service.delete_user(session, current_user)
    return None

@router.patch("/me", response_model=UserRead, dependencies=[Depends(access_token)])
async def patch_me(
    data: UserUpdate,
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
):
    return await user_service.update_user(session, current_user, data)

from src.auth.utils import get_current_user

@router.get("/me", response_model=UserRead, dependencies=[Depends(access_token)])
async def me(current_user: User = Depends(get_current_user)):
    print(current_user.email)
    return current_user

@router.get("/search", response_model=list[UserRead])
async def search(
    fullname: str = Query(..., min_length=1),
    details = Depends(access_token),
    session: AsyncSessionDep = None,  
):
    like = f"%{fullname}%"
    stmt = select(User).where((User.username.ilike(like)) | (User.surname.ilike(like)))
    res = await session.execute(stmt)
    return list(res.scalars().all())


@router.get("/{user_email}", response_model=UserRead,dependencies=[Depends(allow_driver_or_passenger),Depends(access_token)])
async def read(user_email: str,  session: AsyncSessionDep):
    user = await user_service.get_user_by_email(session,user_email)
    if not user:
        raise UserNotFoundByEmail()
    return user

@router.patch("/{user_email}", response_model=UserRead,dependencies=[Depends(allow_admin)])
async def patch(user_email: str, data: UserUpdate, session: AsyncSessionDep,current_user :User = Depends(get_current_user)):

    

    user = await user_service.get_user_by_email(session,user_email)

    if not user:
        raise UserNotFoundByEmail()
    if current_user.email != user_email and current_user.role != "admin":
        raise AccessForbidden
    
    return await user_service.update_user(session, user, data)


@router.delete("/{user_email}", status_code=status.HTTP_204_NO_CONTENT,dependencies=[Depends(access_token),Depends(allow_admin)])
async def remove(user_email: str, session: AsyncSessionDep):
    user = await user_service.get_user_by_email(session,user_email)
    if not user:
        raise UserNotFoundByEmail()
    await user_service.delete_user(session, user)
    return None

