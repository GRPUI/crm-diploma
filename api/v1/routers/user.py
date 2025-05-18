from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from api.v1.services.auth import check_access_token
from core.db import DatabaseHandler
from core.db.models import User, UserRole

from api.v1.services.user import UserService
from core.request_models.user import UserCreateRequest, UserUpdateRoleRequest
from core.responce_models.user import UserResponse, UserPaginatedResponse
from deps import DatabaseMarker

router = APIRouter(tags=["Users"])

# ---------- Helper для загрузки User ----------


async def get_user_obj(user_id: int, session: AsyncSession) -> User:
    user = await UserService.get_user(session, user_id)
    if not user.is_active:
        raise HTTPException(403, "User is not active")
    return user


# ---------- Create user ----------


@router.post("/", response_model=UserResponse)
async def create_user(
    data: UserCreateRequest,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        requester = await get_user_obj(requester_id, session)
        if requester.role != UserRole.admin:
            raise HTTPException(403, "Only admins can create users")

        user = await UserService.create_user(
            session=session,
            username=data.username,
            password=data.password,
            role=data.role,
        )
        return user


# ---------- Get single user ----------


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        await get_user_obj(requester_id, session)
        return await UserService.get_user(session, user_id)


# ---------- Get users with pagination ----------


@router.get("/", response_model=UserPaginatedResponse)
async def get_users(
    page: int = 1,
    page_size: int = 20,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        await get_user_obj(requester_id, session)
        return await UserService.get_users_paginated(session, page, page_size)


# ---------- Update user role ----------


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    data: UserUpdateRoleRequest,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        requester = await get_user_obj(requester_id, session)
        return await UserService.update_role(session, user_id, data.new_role, requester)


# ---------- Deactivate user ----------


@router.delete("/{user_id}")
async def deactivate_user(
    user_id: int,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        requester = await get_user_obj(requester_id, session)
        await UserService.deactivate(session, user_id, requester)
        return {"detail": "User deactivated"}
