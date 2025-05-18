from datetime import datetime

from pydantic import BaseModel


# ---------- Response схемы ----------


class CommentResponse(BaseModel):
    id: int
    applicant_id: int
    user_id: int
    text: str
    created_at: datetime

    class Config:
        orm_mode = True


# ---------- Пагинированный ответ ----------


class CommentPaginatedResponse(BaseModel):
    page: int
    next_page: bool
    items: list[CommentResponse]
