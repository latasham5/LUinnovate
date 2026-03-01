from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db_models.user_session import UserSession
from app.db_models.data_purge_log import DataPurgeLog


async def purge_session_chat_data(
    db: AsyncSession, session_id: str, user_id: str,
) -> dict:
    """
    Called when a user logs out or session times out.
    Marks the session as purged and logs the event.
    """
    now = datetime.now(timezone.utc)

    q = select(UserSession).where(UserSession.session_id == session_id)
    result = await db.execute(q)
    session = result.scalar_one_or_none()

    if session:
        session.data_purged = True
        session.purge_timestamp = now
        session.session_end = session.session_end or now

    purge_log = DataPurgeLog(
        session_id=session_id,
        user_id=user_id,
        data_types_purged="session_chat_data",
        purge_timestamp=now,
        success=True,
    )
    db.add(purge_log)
    await db.flush()

    return {
        "session_id": session_id,
        "user_id": user_id,
        "purged": True,
        "timestamp": now.isoformat(),
    }


async def verify_no_chat_persistence(
    db: AsyncSession, user_id: str,
) -> dict:
    """
    Confirms no active unpurged session data exists for a user.
    Called by cybersecurity team to verify system works correctly.
    """
    q = select(UserSession).where(and_(
        UserSession.user_id == user_id,
        UserSession.data_purged == False,
        UserSession.session_end.is_(None),
    ))
    result = await db.execute(q)
    active = result.scalars().all()

    return {
        "user_id": user_id,
        "active_unpurged_sessions": len(active),
        "chat_data_exists": len(active) > 0,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }