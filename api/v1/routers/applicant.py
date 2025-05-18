from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.services.auth import check_access_token
from api.v1.services.user import UserService
from core.db import DatabaseHandler
from core.db.models import User
from api.v1.services.applicant import ApplicantService
from core.request_models.applicant import ApplicantCreateRequest, ApplicantUpdateRequest
from core.responce_models.applicant import ApplicantResponse, ApplicantPaginatedResponse
from deps import DatabaseMarker

router = APIRouter(tags=["Applicants"])

# ---------- Helper ----------


async def get_user_obj(user_id: int, session: AsyncSession) -> User:
    user = await UserService.get_user(session, user_id)
    if not user.is_active:
        raise HTTPException(403, "User is not active")
    return user


# ---------- Create applicant ----------


@router.post("/", response_model=ApplicantResponse)
async def create_applicant(
    data: ApplicantCreateRequest,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        requester = await get_user_obj(requester_id, session)
        applicant = await ApplicantService.create_applicant(
            session=session,
            first_name=data.first_name,
            last_name=data.last_name,
            middle_name=data.middle_name,
            phone_number=data.phone_number,
            email=data.email,
            national_id=data.national_id,
            passport_number=data.passport_number,
            citizenship=data.citizenship,
            birth_date=data.birth_date,
            gender=data.gender,
            intake_period=data.intake_period,
            status=data.status,
            created_by=requester,
        )
        return applicant


# ---------- Get single applicant ----------


@router.get("/{applicant_id}", response_model=ApplicantResponse)
async def get_applicant(
    applicant_id: int,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        await get_user_obj(requester_id, session)
        return await ApplicantService.get_applicant(session, applicant_id)


# ---------- Update applicant ----------


@router.patch("/{applicant_id}", response_model=ApplicantResponse)
async def update_applicant(
    applicant_id: int,
    updates: ApplicantUpdateRequest,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        requester = await get_user_obj(requester_id, session)
        return await ApplicantService.update_applicant(
            session=session,
            applicant_id=applicant_id,
            updates=updates.dict(exclude_unset=True),
            updated_by=requester,
        )


# ---------- Delete applicant ----------


@router.delete("/{applicant_id}")
async def delete_applicant(
    applicant_id: int,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        requester = await get_user_obj(requester_id, session)
        await ApplicantService.delete_applicant(
            session=session, applicant_id=applicant_id, deleted_by=requester
        )
        return {"detail": "Applicant deleted"}


# ---------- Get applicants with pagination ----------


@router.get("/", response_model=ApplicantPaginatedResponse)
async def get_applicants(
    page: int = 1,
    page_size: int = 20,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        await get_user_obj(requester_id, session)
        return await ApplicantService.get_applicants_paginated(session, page, page_size)
