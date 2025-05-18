from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from core.db.crud import create_audit_log
from core.db.models import ChangeType, ActionType


async def log_change(
    session: AsyncSession,
    applicant_id: int,
    changed_by_user_id: int,
    change_type: ChangeType,
    action: ActionType,
    before_data: Optional[dict],
    after_data: Optional[dict],
):
    await create_audit_log(
        session=session,
        applicant_id=applicant_id,
        changed_by_user_id=changed_by_user_id,
        change_type=change_type,
        action=action,
        before_data=before_data,
        after_data=after_data,
    )
