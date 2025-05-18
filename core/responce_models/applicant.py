# ---------- Response схемы ----------
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, EmailStr

from core.request_models.applicant import ApplicantStatus


class ApplicantResponse(BaseModel):
    id: int

    first_name: str
    last_name: Optional[str]
    middle_name: Optional[str]

    phone_number: Optional[str]
    email: Optional[EmailStr]

    national_id: Optional[str]
    passport_number: Optional[str]
    citizenship: Optional[str]

    birth_date: Optional[date]
    gender: Optional[str]

    registration_date: datetime
    intake_period: Optional[str]

    status: ApplicantStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ---------- Пагинированный ответ ----------


class ApplicantPaginatedResponse(BaseModel):
    page: int
    next_page: bool
    items: list[ApplicantResponse]
