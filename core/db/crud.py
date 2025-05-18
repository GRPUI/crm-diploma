from datetime import date
from typing import Optional

from sqlalchemy import select, or_
from passlib.hash import argon2
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from core.db.models import (
    User,
    UserRole,
    ApplicantStatus,
    Applicant,
    Specialty,
    ExamType,
    Exam,
    Comment,
    ChangeType,
    ActionType,
    AuditLog,
)


async def create_user(
    session: AsyncSession, username: str, password: str, role: UserRole
) -> User:
    if role not in UserRole.__dict__:
        raise HTTPException(400, "Invalid role")

    existing = await session.scalar(select(User).where(User.username == username))
    if existing:
        raise HTTPException(409, "Username already exists")

    user = User(username=username, password_hash=argon2.hash(password), role=role)
    session.add(user)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(500, "Database error occurred")

    await session.refresh(user)
    return user


async def get_user(session: AsyncSession, user_id: int) -> User:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


async def update_user_role(
    session: AsyncSession, user_id: int, new_role: UserRole, current_user: User
) -> User:
    if user_id == current_user.id:
        raise HTTPException(400, "You cannot change your own role")
    if current_user.role != UserRole.admin:
        raise HTTPException(403, "Only admins can change roles")

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    if new_role not in UserRole.__dict__:
        raise HTTPException(400, "Invalid role")

    user.role = new_role
    await session.commit()
    await session.refresh(user)
    return user


async def deactivate_user(session: AsyncSession, user_id: int, current_user: User):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    if user.id == current_user.id:
        raise HTTPException(400, "You cannot deactivate yourself")

    if current_user.role != UserRole.admin:
        raise HTTPException(403, "Only admins can deactivate users")

    user.is_active = False
    await session.commit()


async def create_applicant(
    session: AsyncSession,
    first_name: str,
    last_name: Optional[str],
    middle_name: Optional[str],
    phone_number: Optional[str],
    email: Optional[str],
    national_id: Optional[str],
    passport_number: Optional[str],
    citizenship: Optional[str],
    birth_date: Optional[date],
    gender: Optional[str],
    intake_period: Optional[str],
    status: ApplicantStatus = ApplicantStatus.new,
) -> Applicant:

    # Проверка уникальности national_id и passport_number
    if national_id or passport_number:
        stmt = select(Applicant).where(
            or_(
                Applicant.national_id == national_id,
                Applicant.passport_number == passport_number,
            )
        )
        existing = await session.scalar(stmt)
        if existing:
            raise HTTPException(
                409, "Applicant with provided national ID or passport already exists"
            )

    applicant = Applicant(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        phone_number=phone_number,
        email=email,
        national_id=national_id,
        passport_number=passport_number,
        citizenship=citizenship,
        birth_date=birth_date,
        gender=gender,
        intake_period=intake_period,
        status=status,
    )
    session.add(applicant)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(500, "Database error occurred")

    await session.refresh(applicant)
    return applicant


async def get_applicant(session: AsyncSession, applicant_id: int) -> Applicant:
    applicant = await session.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(404, "Applicant not found")
    return applicant


async def update_applicant(
    session: AsyncSession, applicant_id: int, updates: dict
) -> Applicant:
    applicant = await session.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(404, "Applicant not found")

    allowed_fields = {
        "first_name",
        "last_name",
        "middle_name",
        "phone_number",
        "email",
        "national_id",
        "passport_number",
        "citizenship",
        "birth_date",
        "gender",
        "intake_period",
        "status",
    }

    for field, value in updates.items():
        if field not in allowed_fields:
            raise HTTPException(400, f"Field '{field}' cannot be updated")
        setattr(applicant, field, value)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(500, "Database error occurred")

    await session.refresh(applicant)
    return applicant


async def delete_applicant(session: AsyncSession, applicant_id: int):
    applicant = await session.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(404, "Applicant not found")

    # Защита: если есть комментарии или связанная история — запрет
    if applicant.comments:
        raise HTTPException(400, "Cannot delete applicant with existing comments")

    if applicant.applicant_specialties:
        raise HTTPException(400, "Cannot delete applicant linked to specialties")

    session.delete(applicant)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(500, "Database error occurred")


async def create_specialty(
    session: AsyncSession,
    name: str,
    code: str,
    faculty: Optional[str],
    degree_level: Optional[str],
) -> Specialty:

    existing = await session.scalar(
        select(Specialty).where((Specialty.name == name) | (Specialty.code == code))
    )
    if existing:
        raise HTTPException(409, "Specialty with this name or code already exists")

    specialty = Specialty(
        name=name, code=code, faculty=faculty, degree_level=degree_level
    )
    session.add(specialty)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(500, "Database error occurred")

    await session.refresh(specialty)
    return specialty


async def get_specialty(session: AsyncSession, specialty_id: int) -> Specialty:
    specialty = await session.get(Specialty, specialty_id)
    if not specialty:
        raise HTTPException(404, "Specialty not found")
    return specialty


async def update_specialty(
    session: AsyncSession, specialty_id: int, updates: dict
) -> Specialty:
    specialty = await session.get(Specialty, specialty_id)
    if not specialty:
        raise HTTPException(404, "Specialty not found")

    allowed_fields = {"name", "code", "faculty", "degree_level"}

    for field, value in updates.items():
        if field not in allowed_fields:
            raise HTTPException(400, f"Field '{field}' cannot be updated")
        setattr(specialty, field, value)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(500, "Database error occurred")

    await session.refresh(specialty)
    return specialty


async def delete_specialty(session: AsyncSession, specialty_id: int):
    specialty = await session.get(Specialty, specialty_id)
    if not specialty:
        raise HTTPException(404, "Specialty not found")

    if specialty.applicant_specialties:
        raise HTTPException(400, "Cannot delete specialty linked to applicants")

    if specialty.specialty_exams:
        raise HTTPException(400, "Cannot delete specialty linked to exams")

    session.delete(specialty)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(500, "Database error occurred")


async def create_exam(
    session: AsyncSession, name: str, type_: ExamType, min_score: Optional[int] = None
) -> Exam:

    existing = await session.scalar(
        select(Exam).where((Exam.name == name) & (Exam.type == type_))
    )
    if existing:
        raise HTTPException(409, "Exam with this name and type already exists")

    exam = Exam(name=name, type=type_, min_score=min_score)
    session.add(exam)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(500, "Database error occurred")

    await session.refresh(exam)
    return exam


async def get_exam(session: AsyncSession, exam_id: int) -> Exam:
    exam = await session.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    return exam


async def update_exam(session: AsyncSession, exam_id: int, updates: dict) -> Exam:
    exam = await session.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")

    allowed_fields = {"name", "type", "min_score"}

    for field, value in updates.items():
        if field not in allowed_fields:
            raise HTTPException(400, f"Field '{field}' cannot be updated")
        setattr(exam, field, value)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(500, "Database error occurred")

    await session.refresh(exam)
    return exam


async def delete_exam(session: AsyncSession, exam_id: int):
    exam = await session.get(Exam, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")

    if exam.specialty_exams:
        raise HTTPException(400, "Cannot delete exam linked to specialties")

    session.delete(exam)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(500, "Database error occurred")


async def create_comment(
    session: AsyncSession, applicant_id: int, user_id: int, text: str
) -> Comment:

    applicant = await session.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(404, "Applicant not found")

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    comment = Comment(applicant_id=applicant_id, user_id=user_id, text=text)
    session.add(comment)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(500, "Database error occurred")

    await session.refresh(comment)
    return comment


async def get_comment(session: AsyncSession, comment_id: int) -> Comment:
    comment = await session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(404, "Comment not found")
    return comment


async def delete_comment(session: AsyncSession, comment_id: int, current_user: User):
    comment = await session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(404, "Comment not found")

    # Право удалять: либо сам автор, либо admin
    if comment.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            403, "Only the comment author or admins can delete this comment"
        )

    session.delete(comment)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(500, "Database error occurred")


async def create_audit_log(
    session: AsyncSession,
    applicant_id: int,
    changed_by_user_id: int,
    change_type: ChangeType,
    action: ActionType,
    before_data: Optional[dict],
    after_data: Optional[dict],
) -> AuditLog:

    applicant = await session.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(404, "Applicant not found")

    user = await session.get(User, changed_by_user_id)
    if not user:
        raise HTTPException(404, "User not found")

    audit = AuditLog(
        applicant_id=applicant_id,
        changed_by_user_id=changed_by_user_id,
        change_type=change_type,
        action=action,
        before_data=before_data,
        after_data=after_data,
    )
    session.add(audit)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(500, "Database error occurred")

    await session.refresh(audit)
    return audit


async def get_audit_log(session: AsyncSession, audit_id: int) -> AuditLog:
    audit = await session.get(AuditLog, audit_id)
    if not audit:
        raise HTTPException(404, "Audit log entry not found")
    return audit
