# ---------- Response схемы ----------
from typing import Optional

from pydantic import BaseModel

from core.request_models.exam import ExamType


class ExamResponse(BaseModel):
    id: int
    name: str
    type: ExamType
    min_score: Optional[int]

    class Config:
        orm_mode = True


# ---------- Пагинированный ответ ----------


class ExamPaginatedResponse(BaseModel):
    page: int
    next_page: bool
    items: list[ExamResponse]
