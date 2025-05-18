from pydantic import BaseModel, constr
from enum import Enum
from typing import Optional
from datetime import datetime


class ExamType(str, Enum):
    utbk = "utbk"
    tes_mandiri = "tes_mandiri"
    interview = "interview"
    portfolio = "portfolio"
    international = "international"


# ---------- Request схемы ----------


class ExamCreateRequest(BaseModel):
    name: constr(min_length=1)
    type: ExamType
    min_score: Optional[int]


class ExamUpdateRequest(BaseModel):
    name: Optional[str]
    type: Optional[ExamType]
    min_score: Optional[int]
