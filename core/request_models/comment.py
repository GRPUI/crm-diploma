from pydantic import BaseModel, constr
from datetime import datetime

# ---------- Request схемы ----------


class CommentCreateRequest(BaseModel):
    applicant_id: int
    text: constr(min_length=1)
