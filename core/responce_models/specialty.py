from typing import Optional

from pydantic import BaseModel


class SpecialtyResponse(BaseModel):
    id: int
    name: str
    code: str
    faculty: Optional[str]
    degree_level: Optional[str]

    class Config:
        orm_mode = True


# ---------- Пагинированный ответ ----------


class SpecialtyPaginatedResponse(BaseModel):
    page: int
    next_page: bool
    items: list[SpecialtyResponse]
