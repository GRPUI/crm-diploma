from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from core.db.models import Exam, ExamType
from core.db.crud import (
    create_exam as crud_create_exam,
    get_exam as crud_get_exam,
    update_exam as crud_update_exam,
    delete_exam as crud_delete_exam,
)


class ExamService:

    @staticmethod
    async def create_exam(
        session: AsyncSession,
        name: str,
        type_: ExamType,
        min_score: Optional[int] = None,
    ) -> Exam:

        existing = await session.scalar(
            select(Exam).where((Exam.name == name) & (Exam.type == type_))
        )
        if existing:
            raise HTTPException(409, "Exam with this name and type already exists")

        return await crud_create_exam(
            session=session, name=name, type_=type_, min_score=min_score
        )

    @staticmethod
    async def get_exam(session: AsyncSession, exam_id: int) -> Exam:
        return await crud_get_exam(session, exam_id)

    @staticmethod
    async def update_exam(session: AsyncSession, exam_id: int, updates: dict) -> Exam:

        allowed_fields = {"name", "type", "min_score"}

        for field in updates:
            if field not in allowed_fields:
                raise HTTPException(400, f"Field '{field}' cannot be updated")

        return await crud_update_exam(session=session, exam_id=exam_id, updates=updates)

    @staticmethod
    async def delete_exam(session: AsyncSession, exam_id: int):
        return await crud_delete_exam(session, exam_id)

    @staticmethod
    async def get_exams_paginated(
        session: AsyncSession, page: int = 1, page_size: int = 20
    ) -> dict:

        if page < 1:
            raise HTTPException(400, "Page number must be 1 or higher")

        stmt = select(Exam).offset((page - 1) * page_size).limit(page_size + 1)
        result = await session.execute(stmt)
        exams = result.scalars().all()

        next_page = len(exams) > page_size

        return {"page": page, "next_page": next_page, "items": exams[:page_size]}
