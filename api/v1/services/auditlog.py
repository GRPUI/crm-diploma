from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from core.db.models import AuditLog, ChangeType, ActionType, Applicant, User
from core.db.crud import (
    create_audit_log as crud_create_audit_log,
    get_audit_log as crud_get_audit_log,
)


class AuditLogService:

    @staticmethod
    async def create_audit_log(
        session: AsyncSession,
        applicant_id: int,
        changed_by_user_id: int,
        change_type: ChangeType,
        action: ActionType,
        before_data: Optional[dict],
        after_data: Optional[dict],
    ) -> AuditLog:

        applicant = await session.get(Applicant, applicant_id)
        if not applicant:
            raise HTTPException(404, "Applicant not found")

        user = await session.get(User, changed_by_user_id)
        if not user:
            raise HTTPException(404, "User not found")

        return await crud_create_audit_log(
            session=session,
            applicant_id=applicant_id,
            changed_by_user_id=changed_by_user_id,
            change_type=change_type,
            action=action,
            before_data=before_data,
            after_data=after_data,
        )

    @staticmethod
    async def get_audit_log(session: AsyncSession, audit_id: int) -> AuditLog:
        return await crud_get_audit_log(session, audit_id)

    @staticmethod
    async def get_applicant_audit_logs_paginated(
        session: AsyncSession, applicant_id: int, page: int = 1, page_size: int = 20
    ) -> dict:

        if page < 1:
            raise HTTPException(400, "Page number must be 1 or higher")

        stmt = (
            select(AuditLog)
            .where(AuditLog.applicant_id == applicant_id)
            .order_by(AuditLog.changed_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size + 1)
        )

        result = await session.execute(stmt)
        logs = result.scalars().all()

        next_page = len(logs) > page_size

        return {"page": page, "next_page": next_page, "items": logs[:page_size]}
