from pydantic import BaseModel, constr
from typing import Optional
from datetime import datetime

# ---------- Request схемы ----------


class SpecialtyCreateRequest(BaseModel):
    name: constr(min_length=1)
    code: constr(min_length=1)
    faculty: Optional[str]
    degree_level: Optional[str]


class SpecialtyUpdateRequest(BaseModel):
    name: Optional[str]
    code: Optional[str]
    faculty: Optional[str]
    degree_level: Optional[str]
