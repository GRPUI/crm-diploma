from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from core.db.models import Comment, Applicant, User, UserRole
from core.db.crud import (
    create_comment as crud_create_comment,
    get_comment as crud_get_comment,
    delete_comment as crud_delete_comment,
)


class CommentService:

    @staticmethod
    async def create_comment(
        session: AsyncSession, applicant_id: int, user_id: int, text: str
    ) -> Comment:

        applicant = await session.get(Applicant, applicant_id)
        if not applicant:
            raise HTTPException(404, "Applicant not found")

        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(404, "User not found")

        return await crud_create_comment(
            session=session, applicant_id=applicant_id, user_id=user_id, text=text
        )

    @staticmethod
    async def get_comment(session: AsyncSession, comment_id: int) -> Comment:
        return await crud_get_comment(session, comment_id)

    @staticmethod
    async def delete_comment(
        session: AsyncSession, comment_id: int, current_user: User
    ):
        comment = await crud_get_comment(session, comment_id)

        if comment.user_id != current_user.id and current_user.role != UserRole.admin:
            raise HTTPException(
                403, "Only the comment author or admins can delete this comment"
            )

        await crud_delete_comment(session, comment_id)

    @staticmethod
    async def get_comments_paginated(
        session: AsyncSession, applicant_id: int, page: int = 1, page_size: int = 20
    ) -> dict:

        if page < 1:
            raise HTTPException(400, "Page number must be 1 or higher")

        stmt = (
            select(Comment)
            .where(Comment.applicant_id == applicant_id)
            .order_by(Comment.created_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size + 1)
        )

        result = await session.execute(stmt)
        comments = result.scalars().all()

        next_page = len(comments) > page_size

        return {"page": page, "next_page": next_page, "items": comments[:page_size]}
