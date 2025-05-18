from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional


class ChangeType(str, Enum):
    status = "status"
    comment = "comment"
    specialty = "specialty"
    exam = "exam"
    applicant_data = "applicant_data"


class ActionType(str, Enum):
    create = "create"
    update = "update"
    delete = "delete"


# ---------- Request схема (в основном для internal use, не публичная API) ----------


class AuditLogCreateRequest(BaseModel):
    applicant_id: int
    changed_by_user_id: int
    change_type: ChangeType
    action: ActionType
    before_data: Optional[dict]
    after_data: Optional[dict]
