from pydantic import BaseModel, constr, EmailStr
from enum import Enum
from datetime import datetime, date
from typing import Optional


class ApplicantStatus(str, Enum):
    new = "new"
    in_progress = "in_progress"
    admitted = "admitted"
    rejected = "rejected"


# ---------- Request схемы ----------


class ApplicantCreateRequest(BaseModel):
    first_name: constr(min_length=1)
    last_name: Optional[str]
    middle_name: Optional[str]

    phone_number: Optional[str]
    email: Optional[EmailStr]

    national_id: Optional[str]
    passport_number: Optional[str]
    citizenship: Optional[str]

    birth_date: Optional[date]
    gender: Optional[str]

    intake_period: Optional[str]
    status: ApplicantStatus = ApplicantStatus.new


class ApplicantUpdateRequest(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str]

    phone_number: Optional[str]
    email: Optional[EmailStr]

    national_id: Optional[str]
    passport_number: Optional[str]
    citizenship: Optional[str]

    birth_date: Optional[date]
    gender: Optional[str]

    intake_period: Optional[str]
    status: Optional[ApplicantStatus]
