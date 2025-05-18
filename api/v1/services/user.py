from typing import Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from passlib.hash import argon2
from core.db.crud import (
    create_user as crud_create_user,
    get_user as crud_get_user,
    update_user_role as crud_update_user_role,
    deactivate_user as crud_deactivate_user,
)

from core.db.models import UserRole, User
from core.responce_models.user import UserResponse, UserPaginatedResponse


class UserService:

    @staticmethod
    async def create_user(
        session: AsyncSession, username: str, password: str, role: UserRole
    ) -> User:
        if len(password) < 8:
            raise HTTPException(400, "Password must be at least 8 characters long")
        return await crud_create_user(session, username, password, role)

    @staticmethod
    async def get_user(session: AsyncSession, user_id: int) -> User:
        return await crud_get_user(session, user_id)

    @staticmethod
    async def update_role(
        session: AsyncSession, user_id: int, new_role: UserRole, current_user: User
    ) -> User:
        if current_user.role != UserRole.admin:
            raise HTTPException(403, "Only admins can change user roles")
        return await crud_update_user_role(session, user_id, new_role, current_user)

    @staticmethod
    async def deactivate(session: AsyncSession, user_id: int, current_user: User):
        return await crud_deactivate_user(session, user_id, current_user)

    @staticmethod
    async def verify_password(user: User, password: str) -> bool:
        return argon2.verify(password, user.password_hash)

    @staticmethod
    async def get_users_paginated(
        session: AsyncSession, page: int, page_size: int
    ) -> UserPaginatedResponse:
        next_page = False
        offset = (page - 1) * page_size
        query = select(User).offset(offset).limit(page_size + 1)
        result = await session.execute(query)
        users = result.scalars().all()
        if len(users) > page_size:
            next_page = True
            users = users[:-1]
        return UserPaginatedResponse(
            items=[UserResponse(**user.__dict__) for user in users],
            next_page=next_page,
            page=page,
        )
