from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.services.auth import check_access_token
from api.v1.services.speciality import SpecialtyService
from api.v1.services.user import UserService
from core.db import DatabaseHandler
from core.db.models import User, UserRole
from core.request_models.specialty import SpecialtyCreateRequest, SpecialtyUpdateRequest
from core.responce_models.specialty import SpecialtyResponse, SpecialtyPaginatedResponse
from deps import DatabaseMarker

router = APIRouter(tags=["Specialties"])

# ---------- Helper ----------


async def get_user_obj(user_id: int, session: AsyncSession) -> User:
    user = await UserService.get_user(session, user_id)
    if not user.is_active:
        raise HTTPException(403, "User is not active")
    return user


# ---------- Create specialty (Admin only) ----------


@router.post("/", response_model=SpecialtyResponse)
async def create_specialty(
    data: SpecialtyCreateRequest,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        requester = await get_user_obj(requester_id, session)
        if requester.role != UserRole.admin:
            raise HTTPException(403, "Only admins can create specialties")

        return await SpecialtyService.create_specialty(
            session=session,
            name=data.name,
            code=data.code,
            faculty=data.faculty,
            degree_level=data.degree_level,
        )


# ---------- Get single specialty ----------


@router.get("/{specialty_id}", response_model=SpecialtyResponse)
async def get_specialty(
    specialty_id: int,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        await get_user_obj(requester_id, session)
        return await SpecialtyService.get_specialty(session, specialty_id)


# ---------- Update specialty (Admin only) ----------


@router.patch("/{specialty_id}", response_model=SpecialtyResponse)
async def update_specialty(
    specialty_id: int,
    updates: SpecialtyUpdateRequest,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        requester = await get_user_obj(requester_id, session)
        if requester.role != UserRole.admin:
            raise HTTPException(403, "Only admins can update specialties")

        return await SpecialtyService.update_specialty(
            session=session,
            specialty_id=specialty_id,
            updates=updates.dict(exclude_unset=True),
        )


# ---------- Delete specialty (Admin only) ----------


@router.delete("/{specialty_id}")
async def delete_specialty(
    specialty_id: int,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        requester = await get_user_obj(requester_id, session)
        if requester.role != UserRole.admin:
            raise HTTPException(403, "Only admins can delete specialties")

        await SpecialtyService.delete_specialty(session, specialty_id)
        return {"detail": "Specialty deleted"}


# ---------- List specialties with pagination ----------


@router.get("/", response_model=SpecialtyPaginatedResponse)
async def list_specialties(
    page: int = 1,
    page_size: int = 20,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        await get_user_obj(requester_id, session)
        return await SpecialtyService.get_specialties_paginated(
            session, page, page_size
        )
