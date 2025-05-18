# ---------- Response схемы ----------
from datetime import datetime

from pydantic import BaseModel

from core.request_models.user import UserRole


class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


# ---------- Пагинированный ответ ----------


class UserPaginatedResponse(BaseModel):
    page: int
    next_page: bool
    items: list[UserResponse]
