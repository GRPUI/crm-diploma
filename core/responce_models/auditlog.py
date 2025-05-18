# ---------- Response схема ----------
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from core.db.models import ChangeType, ActionType


class AuditLogResponse(BaseModel):
    id: int
    applicant_id: int
    changed_by_user_id: int
    change_type: ChangeType
    action: ActionType
    before_data: Optional[dict]
    after_data: Optional[dict]
    changed_at: datetime

    class Config:
        orm_mode = True


# ---------- Пагинированный ответ ----------


class AuditLogPaginatedResponse(BaseModel):
    page: int
    next_page: bool
    items: list[AuditLogResponse]
