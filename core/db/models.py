from sqlalchemy import (
    ForeignKey,
    Enum,
    JSON,
    Integer,
    String,
    Date,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from datetime import datetime, date
from typing import List, Optional

# --- База ---


class Base(DeclarativeBase):
    pass


# --- Enum'ы ---


class UserRole(PyEnum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class ApplicantStatus(PyEnum):
    new = "new"
    in_progress = "in_progress"
    admitted = "admitted"
    rejected = "rejected"


class ExamType(PyEnum):
    utbk = "utbk"
    tes_mandiri = "tes_mandiri"
    interview = "interview"
    portfolio = "portfolio"
    international = "international"


class ChangeType(PyEnum):
    status = "status"
    comment = "comment"
    specialty = "specialty"
    exam = "exam"
    applicant_data = "applicant_data"


class ActionType(PyEnum):
    create = "create"
    update = "update"
    delete = "delete"


# --- User ---


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password_hash: Mapped[str]
    role: Mapped[UserRole]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


# --- Applicant ---


class Applicant(Base):
    __tablename__ = "applicants"

    id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str]
    last_name: Mapped[Optional[str]]
    middle_name: Mapped[Optional[str]]

    phone_number: Mapped[Optional[str]]
    email: Mapped[Optional[str]]

    national_id: Mapped[Optional[str]]
    passport_number: Mapped[Optional[str]]
    citizenship: Mapped[Optional[str]]

    birth_date: Mapped[Optional[date]]
    gender: Mapped[Optional[str]]

    registration_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    intake_period: Mapped[Optional[str]]

    status: Mapped[ApplicantStatus] = mapped_column(default=ApplicantStatus.new)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    comments: Mapped[List["Comment"]] = relationship(
        back_populates="applicant", cascade="all, delete-orphan"
    )
    applicant_specialties: Mapped[List["ApplicantSpecialty"]] = relationship(
        back_populates="applicant", cascade="all, delete-orphan"
    )


# --- Specialty ---


class Specialty(Base):
    __tablename__ = "specialties"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    code: Mapped[str]

    faculty: Mapped[Optional[str]]
    degree_level: Mapped[Optional[str]]

    applicant_specialties: Mapped[List["ApplicantSpecialty"]] = relationship(
        back_populates="specialty", cascade="all, delete-orphan"
    )
    specialty_exams: Mapped[List["SpecialtyExam"]] = relationship(
        back_populates="specialty", cascade="all, delete-orphan"
    )


# --- Exam ---


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    type: Mapped[ExamType]
    min_score: Mapped[Optional[int]]

    specialty_exams: Mapped[List["SpecialtyExam"]] = relationship(
        back_populates="exam", cascade="all, delete-orphan"
    )


# --- Applicant ↔ Specialty связь ---


class ApplicantSpecialty(Base):
    __tablename__ = "applicant_specialties"

    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("applicants.id"), primary_key=True
    )
    specialty_id: Mapped[int] = mapped_column(
        ForeignKey("specialties.id"), primary_key=True
    )

    priority: Mapped[Optional[int]] = mapped_column(nullable=True)

    applicant: Mapped["Applicant"] = relationship(
        back_populates="applicant_specialties"
    )
    specialty: Mapped["Specialty"] = relationship(
        back_populates="applicant_specialties"
    )


# --- Specialty ↔ Exam связь ---


class SpecialtyExam(Base):
    __tablename__ = "specialty_exams"

    specialty_id: Mapped[int] = mapped_column(
        ForeignKey("specialties.id"), primary_key=True
    )
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"), primary_key=True)

    required_score: Mapped[Optional[int]] = mapped_column(nullable=True)

    specialty: Mapped["Specialty"] = relationship(back_populates="specialty_exams")
    exam: Mapped["Exam"] = relationship(back_populates="specialty_exams")


# --- Comment ---


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("applicants.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    applicant: Mapped["Applicant"] = relationship(back_populates="comments")


# --- AuditLog ---


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("applicants.id"))
    changed_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    change_type: Mapped[ChangeType]
    action: Mapped[ActionType]
    before_data: Mapped[Optional[dict]] = mapped_column(JSON)
    after_data: Mapped[Optional[dict]] = mapped_column(JSON)
    changed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
