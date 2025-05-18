from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.services.auditlog import AuditLogService
from api.v1.services.auth import check_access_token
from api.v1.services.user import UserService
from core.db import DatabaseHandler
from core.db.models import User
from core.responce_models.auditlog import AuditLogResponse, AuditLogPaginatedResponse
from deps import DatabaseMarker

router = APIRouter(tags=["Audit Logs"])

# ---------- Helper ----------


async def get_user_obj(user_id: int, session: AsyncSession) -> User:
    user = await UserService.get_user(session, user_id)
    if not user.is_active:
        raise HTTPException(403, "User is not active")
    return user


# ---------- Get audit log by ID ----------


@router.get("/{audit_id}", response_model=AuditLogResponse)
async def get_audit_log(
    audit_id: int,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        await get_user_obj(requester_id, session)
        return await AuditLogService.get_audit_log(session, audit_id)


# ---------- Get audit logs by applicant ID (paginated) ----------


@router.get("/", response_model=AuditLogPaginatedResponse)
async def list_audit_logs_by_applicant(
    applicant_id: int,
    page: int = 1,
    page_size: int = 20,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        await get_user_obj(requester_id, session)
        return await AuditLogService.get_applicant_audit_logs_paginated(
            session=session, applicant_id=applicant_id, page=page, page_size=page_size
        )
