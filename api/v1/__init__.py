from fastapi import APIRouter
from .routers import auth, user, applicant, auditlog, comment, exam, specialty

router = APIRouter(prefix="/v1")
router.include_router(applicant.router, prefix="/applicants")
router.include_router(auditlog.router, prefix="/auditlogs")
router.include_router(auth.router, prefix="/auth")
router.include_router(comment.router, prefix="/comments")
router.include_router(exam.router, prefix="/exams")
router.include_router(specialty.router, prefix="/specialities")
router.include_router(user.router, prefix="/users")
