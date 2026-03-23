from fastapi import APIRouter, Depends
from src.users.service import UserService	
from src.users.schema import UserLoginModel,UserCreateModel
from src.auth.utils import RefreshTokenBearer,  create_access_token, decode_token,AccessTokenBearer, get_current_user
from src.auth.security import verify_password
from src.db.session import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from src.errors.customErrors import InvalidToken, UserAlreadyExists,InvalidCredentials
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from src.db.redis import add_jti_to_blocklist, token_in_blocklist
from src.dependencies import RoleChecker

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin"])

@auth_router.get("/me",dependencies=[Depends(role_checker)])
async def current_user(user=Depends(get_current_user)):
    return user

@auth_router.post("/register")
async def register(
    user_create: UserCreateModel,
    session: AsyncSession = Depends(get_session),
):
    email = user_create.email

    user = await user_service.get_user_by_email(session, email)
    if user:
        raise UserAlreadyExists()

    await user_service.create_user(session, user_create)

    return {"message": "User created successfully"}


@auth_router.post("/login")
async def login(
    user_login: UserLoginModel,
    session: AsyncSession = Depends(get_session),
):
    email = user_login.email
    password = user_login.password

    user = await user_service.get_user_by_email(session, email)

    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentials()

    user_data = {
        "email": user.email,
        "uid": str(user.uid),
    }

    access_token = create_access_token(user_data=user_data)

    refresh_token = create_access_token(
        user_data=user_data,
        expiry=timedelta(days=7),
        refresh=True,
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@auth_router.post("/refresh")
async def refresh_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) <= datetime.now():
        raise InvalidToken()

    user_data = token_details["user_data"]

    new_access_token = create_access_token(user_data=user_data)

    return JSONResponse(
        content={"access_token": new_access_token},
        status_code=200,
    )


@auth_router.post("/logout")
async def logout(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details.get("jti")

    if not jti:
        raise InvalidToken()

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logout successful"},
        status_code=200,
    )