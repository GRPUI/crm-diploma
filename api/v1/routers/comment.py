from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.services.auth import check_access_token
from api.v1.services.comment import CommentService
from api.v1.services.user import UserService
from core.db import DatabaseHandler
from core.db.models import User
from core.request_models.comment import CommentCreateRequest
from core.responce_models.comment import CommentResponse, CommentPaginatedResponse
from deps import DatabaseMarker

router = APIRouter(tags=["Comments"])

# ---------- Helper ----------


async def get_user_obj(user_id: int, session: AsyncSession) -> User:
    user = await UserService.get_user(session, user_id)
    if not user.is_active:
        raise HTTPException(403, "User is not active")
    return user


# ---------- Create comment ----------


@router.post("/", response_model=CommentResponse)
async def create_comment(
    data: CommentCreateRequest,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        await get_user_obj(requester_id, session)
        return await CommentService.create_comment(
            session=session,
            applicant_id=data.applicant_id,
            user_id=requester_id,
            text=data.text,
        )


# ---------- Get comment by ID ----------


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        await get_user_obj(requester_id, session)
        return await CommentService.get_comment(session, comment_id)


# ---------- Delete comment ----------


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        user = await get_user_obj(requester_id, session)
        await CommentService.delete_comment(
            session=session, comment_id=comment_id, current_user=user
        )
        return {"detail": "Comment deleted"}


# ---------- List comments by applicant_id ----------


@router.get("/", response_model=CommentPaginatedResponse)
async def list_comments_by_applicant(
    applicant_id: int,
    page: int = 1,
    page_size: int = 20,
    db: DatabaseHandler = Depends(DatabaseMarker),
    requester_id: int = Depends(check_access_token),
):
    async with db.sessionmaker() as session:
        await get_user_obj(requester_id, session)
        return await CommentService.get_comments_paginated(
            session=session, applicant_id=applicant_id, page=page, page_size=page_size
        )
