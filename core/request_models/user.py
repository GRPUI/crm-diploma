from pydantic import BaseModel, constr
from enum import Enum
from datetime import datetime


class UserRole(str, Enum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


# ---------- Request схемы ----------


class UserCreateRequest(BaseModel):
    username: constr(min_length=3, max_length=150)
    password: constr(min_length=8)
    role: UserRole


class UserUpdateRoleRequest(BaseModel):
    new_role: UserRole
