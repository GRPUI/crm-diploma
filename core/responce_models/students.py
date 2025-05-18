from typing import List

from pydantic import BaseModel

from core.responce_models.defaults import DefaultPaginationModel


class SingleStudentStatus(BaseModel):
    title: str
    color: str


class SingleStudentExam(BaseModel):
    name: str
    points: int


class SingleStudent(BaseModel):
    student_id: int
    name: str
    is_original: bool
    total_points: int
    total_points_with_achievements: int
    personal_achievements: int
    exam_type: str
    profile: str
    is_dormitory_needed: bool
    personal_id: int
    phone_number: str
    cellphone_number: str
    email: str
    status: SingleStudentStatus | None


class SingleStudentExtended(SingleStudent):
    exams: List[SingleStudentExam] | None = None


class StudentsList(DefaultPaginationModel):
    students: List[SingleStudent]


class StudentStats(BaseModel):
    total_students: int
    max_total_points: int
    min_total_points: int
    avg_total_points: float
