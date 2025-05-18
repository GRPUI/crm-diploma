from pydantic import BaseModel


class DefaultResponseModel(BaseModel):
    status: str
    message: str


class DefaultPaginationModel(BaseModel):
    page: int
    next_page: bool
