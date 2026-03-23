from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db.models import User
from src.users.schema import UserCreateModel, UserUpdate
from src.auth.security import hash_password

class UserService:
    async def create_user(self, session: AsyncSession, data: UserCreateModel) -> User:
        passwordd = data.password
        hashPassword = hash_password(passwordd)
        user = User(
            email=data.email,
            username=data.username,
            surname=data.surname,
            phone=data.phone,
            hashed_password=hashPassword,
            role=data.role
        )
        session.add(user)

        await session.commit()
        await session.refresh(user)
        return user


    async def get_user(self, session: AsyncSession, uid: int) -> User | None:
        res = await session.execute(select(User).where(User.uid == uid))
        return res.scalar_one_or_none()


    async def list_users(self, session: AsyncSession) -> list[User]:
        res = await session.execute(select(User))
        return list(res.scalars().all())


    async def search_users_by_fullname(self, session: AsyncSession, fullname: str) -> list[User]:
        like = f"%{fullname}%"
        stmt = select(User).where((User.fullname.ilike(like)) | (User.surname.ilike(like)))
        res = await session.execute(stmt)
        return list(res.scalars().all())


    async def update_user(self, session: AsyncSession, user: User, data: UserUpdate) -> User:
        payload = data.model_dump(exclude_unset=True)
        for k, v in payload.items():
            setattr(user, k, v)

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


    async def delete_user(self, session: AsyncSession, user: User) -> None:
        await session.delete(user)
        await session.commit()

    async def get_user_by_email(self, session: AsyncSession, email: str) -> User | None:
        user = await session.execute(select(User).where(User.email == email))
        return user.scalar_one_or_none()