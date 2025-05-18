from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.services.auth import check_access_token
from api.v1.services.exam import ExamService
from api.v1.services.user import UserService
from core.db import DatabaseHandler
from core.db.models import User, UserRole
from core.request_models.exam import ExamCreateRequest, ExamUpdateRequest
from core.responce_models.exam import ExamResponse, ExamPaginatedResponse
from deps import DatabaseMarker

router = APIRouter(tags=["Exams"])

# ---------- Helper ----------


async def get_user_obj(user_id: int, session: AsyncSession) -> User:
    user = await UserService.get_user(session, user_id)
    if not user.is_active:
        raise HTTPException(403, "User is not active")
    return user


# ---------- Create exam (Admin only) ----------


@router.post("/", response_model=ExamResponse)
async def create_exam(
    data: ExamCreateRequest,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        requester = await get_user_obj(requester_id, session)
        if requester.role != UserRole.admin:
            raise HTTPException(403, "Only admins can create exams")

        return await ExamService.create_exam(
            session=session, name=data.name, type_=data.type, min_score=data.min_score
        )


# ---------- Get exam by ID ----------


@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: int,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        await get_user_obj(requester_id, session)
        return await ExamService.get_exam(session, exam_id)


# ---------- Update exam (Admin only) ----------


@router.patch("/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: int,
    updates: ExamUpdateRequest,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        requester = await get_user_obj(requester_id, session)
        if requester.role != UserRole.admin:
            raise HTTPException(403, "Only admins can update exams")

        return await ExamService.update_exam(
            session=session, exam_id=exam_id, updates=updates.dict(exclude_unset=True)
        )


# ---------- Delete exam (Admin only) ----------


@router.delete("/{exam_id}")
async def delete_exam(
    exam_id: int,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        requester = await get_user_obj(requester_id, session)
        if requester.role != UserRole.admin:
            raise HTTPException(403, "Only admins can delete exams")

        await ExamService.delete_exam(session, exam_id)
        return {"detail": "Exam deleted"}


# ---------- List exams (paginated) ----------


@router.get("/", response_model=ExamPaginatedResponse)
async def list_exams(
    page: int = 1,
    page_size: int = 20,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        await get_user_obj(requester_id, session)
        return await ExamService.get_exams_paginated(session, page, page_size)
