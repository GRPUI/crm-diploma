from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from core.db.models import Specialty
from core.db.crud import (
    create_specialty as crud_create_specialty,
    get_specialty as crud_get_specialty,
    update_specialty as crud_update_specialty,
    delete_specialty as crud_delete_specialty,
)


class SpecialtyService:

    @staticmethod
    async def create_specialty(
        session: AsyncSession,
        name: str,
        code: str,
        faculty: Optional[str],
        degree_level: Optional[str],
    ) -> Specialty:

        existing = await session.scalar(
            select(Specialty).where((Specialty.name == name) | (Specialty.code == code))
        )
        if existing:
            raise HTTPException(409, "Specialty with this name or code already exists")

        return await crud_create_specialty(
            session=session,
            name=name,
            code=code,
            faculty=faculty,
            degree_level=degree_level,
        )

    @staticmethod
    async def get_specialty(session: AsyncSession, specialty_id: int) -> Specialty:
        return await crud_get_specialty(session, specialty_id)

    @staticmethod
    async def update_specialty(
        session: AsyncSession, specialty_id: int, updates: dict
    ) -> Specialty:

        allowed_fields = {"name", "code", "faculty", "degree_level"}

        for field in updates:
            if field not in allowed_fields:
                raise HTTPException(400, f"Field '{field}' cannot be updated")

        return await crud_update_specialty(
            session=session, specialty_id=specialty_id, updates=updates
        )

    @staticmethod
    async def delete_specialty(session: AsyncSession, specialty_id: int):
        return await crud_delete_specialty(session, specialty_id)

    @staticmethod
    async def get_specialties_paginated(
        session: AsyncSession, page: int = 1, page_size: int = 20
    ) -> dict:

        if page < 1:
            raise HTTPException(400, "Page number must be 1 or higher")

        stmt = select(Specialty).offset((page - 1) * page_size).limit(page_size + 1)
        result = await session.execute(stmt)
        specialties = result.scalars().all()

        next_page = len(specialties) > page_size

        return {"page": page, "next_page": next_page, "items": specialties[:page_size]}
