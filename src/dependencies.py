from __future__ import annotations

from typing import Annotated, Any, Type, TypeVar

from fastapi import Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel
from src.db.session import get_session
from src.auth.utils import get_current_user
from src.db.models import User
from typing import List

AsyncSessionDep = Annotated[AsyncSession, Depends(get_session)]

T = TypeVar("T", bound=SQLModel)


async def get_or_404(
    model: Type[T],
    obj_id: str,
    session: AsyncSession,
    *,
    detail: str | None = None,
) -> T:
    obj = await session.get(model, obj_id)
    if not obj:
        raise HTTPException(
            status_code=404,
            detail=detail or f"{model.__name__} not found",
        )
    return obj


def pagination_params(limit: int = 50, offset: int = 0) -> tuple[int, int]:
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    return limit, offset

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if current_user.role in self.allowed_roles:
            return True

        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to perform this action."
        )
    
allow_admin = RoleChecker(["admin"])
allow_driver = RoleChecker(["driver", "admin"])
allow_passenger = RoleChecker(["passenger", "admin"])
allow_driver_or_passenger = RoleChecker(["driver", "passenger", "admin"])