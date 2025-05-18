from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select, or_
from core.db.models import (
    Applicant,
    ApplicantStatus,
    AuditLog,
    ChangeType,
    ActionType,
    User,
)
from core.db.crud import (
    create_applicant as crud_create_applicant,
    get_applicant as crud_get_applicant,
    update_applicant as crud_update_applicant,
    delete_applicant as crud_delete_applicant,
)
from core.db.crud import create_audit_log
from datetime import date


class ApplicantService:

    @staticmethod
    async def create_applicant(
        session: AsyncSession,
        first_name: str,
        last_name: Optional[str],
        middle_name: Optional[str],
        phone_number: Optional[str],
        email: Optional[str],
        national_id: Optional[str],
        passport_number: Optional[str],
        citizenship: Optional[str],
        birth_date: Optional[date],
        gender: Optional[str],
        intake_period: Optional[str],
        status: ApplicantStatus,
        created_by: User,  # Кто создаёт
    ) -> Applicant:

        # Проверка уникальности national_id/passport_number
        if national_id or passport_number:
            stmt = select(Applicant).where(
                or_(
                    Applicant.national_id == national_id,
                    Applicant.passport_number == passport_number,
                )
            )
            existing = await session.scalar(stmt)
            if existing:
                raise HTTPException(
                    409,
                    "Applicant with provided national ID or passport already exists",
                )

        applicant = await crud_create_applicant(
            session=session,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            phone_number=phone_number,
            email=email,
            national_id=national_id,
            passport_number=passport_number,
            citizenship=citizenship,
            birth_date=birth_date,
            gender=gender,
            intake_period=intake_period,
            status=status,
        )

        # Логируем создание
        await create_audit_log(
            session=session,
            applicant_id=applicant.id,
            changed_by_user_id=created_by.id,
            change_type=ChangeType.applicant_data,
            action=ActionType.create,
            before_data=None,
            after_data={"first_name": first_name, "last_name": last_name},
        )

        return applicant

    @staticmethod
    async def get_applicant(session: AsyncSession, applicant_id: int) -> Applicant:
        return await crud_get_applicant(session, applicant_id)

    @staticmethod
    async def update_applicant(
        session: AsyncSession, applicant_id: int, updates: dict, updated_by: User
    ) -> Applicant:

        applicant = await crud_get_applicant(session, applicant_id)

        # before_data для аудита
        before = {field: getattr(applicant, field) for field in updates}

        updated_applicant = await crud_update_applicant(
            session=session, applicant_id=applicant_id, updates=updates
        )

        # after_data для аудита
        after = {field: getattr(updated_applicant, field) for field in updates}

        await create_audit_log(
            session=session,
            applicant_id=applicant_id,
            changed_by_user_id=updated_by.id,
            change_type=ChangeType.applicant_data,
            action=ActionType.update,
            before_data=before,
            after_data=after,
        )

        return updated_applicant

    @staticmethod
    async def delete_applicant(
        session: AsyncSession, applicant_id: int, deleted_by: User
    ):

        applicant = await crud_get_applicant(session, applicant_id)

        before_data = {
            "first_name": applicant.first_name,
            "last_name": applicant.last_name,
        }

        await crud_delete_applicant(session, applicant_id)

        await create_audit_log(
            session=session,
            applicant_id=applicant_id,
            changed_by_user_id=deleted_by.id,
            change_type=ChangeType.applicant_data,
            action=ActionType.delete,
            before_data=before_data,
            after_data=None,
        )

    @staticmethod
    async def get_applicants_paginated(
        session: AsyncSession, page: int = 1, page_size: int = 20
    ) -> dict:

        if page < 1:
            raise HTTPException(400, "Page number must be 1 or higher")

        stmt = select(Applicant).offset((page - 1) * page_size).limit(page_size + 1)

        result = await session.execute(stmt)
        users: List[User] = result.scalars().all()

        next_page = len(users) > page_size

        return {
            "page": page,
            "next_page": next_page,
            "items": users[:page_size],  # Возвращаем ровно page_size пользователей
        }
