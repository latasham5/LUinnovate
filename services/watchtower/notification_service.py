from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db_models.notification_preference import NotificationPreference
from app.shared.models import NotificationPreferenceUpdate
from app.shared.enums import NotificationChannel


async def get_notification_preferences(
    db: AsyncSession, user_id: str,
) -> Optional[NotificationPreference]:
    """Retrieves a user's notification settings."""
    q = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def update_notification_preferences(
    db: AsyncSession, user_id: str, data: NotificationPreferenceUpdate,
) -> NotificationPreference:
    """Creates or updates a user's notification preferences."""
    q = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    result = await db.execute(q)
    prefs = result.scalar_one_or_none()

    if prefs:
        prefs.channel = data.channel
        prefs.real_time_severity = data.real_time_severity
        prefs.digest_enabled = data.digest_enabled
        prefs.digest_day = data.digest_day
        prefs.digest_time = data.digest_time
        prefs.updated_at = datetime.now(timezone.utc)
    else:
        prefs = NotificationPreference(
            user_id=user_id,
            channel=data.channel,
            real_time_severity=data.real_time_severity,
            digest_enabled=data.digest_enabled,
            digest_day=data.digest_day,
            digest_time=data.digest_time,
        )
        db.add(prefs)

    await db.flush()
    return prefs


async def route_notification(
    db: AsyncSession, recipient_id: str, severity: str, message: str,
) -> dict:
    """Checks preferences and routes through the right channel."""
    prefs = await get_notification_preferences(db, recipient_id)

    if not prefs:
        from app.services.alert_service import send_notification
        await send_notification(recipient_id, "BOTH", message)
        return {"routed": True, "channel": "BOTH", "used_defaults": True}

    rt_severities = [s.strip() for s in prefs.real_time_severity.split(",")]

    if severity in rt_severities:
        from app.services.alert_service import send_notification
        await send_notification(recipient_id, prefs.channel.value, message)
        return {"routed": True, "channel": prefs.channel.value, "real_time": True}

    return {"routed": False, "channel": "digest", "reason": "Severity below real-time threshold."}


async def generate_weekly_digest(
    db: AsyncSession, supervisor_id: str,
) -> dict:
    """Wraps alert_service digest with preference-aware delivery."""
    prefs = await get_notification_preferences(db, supervisor_id)

    if prefs and not prefs.digest_enabled:
        return {"sent": False, "reason": "Digest disabled by user preference."}

    from app.services.alert_service import send_weekly_digest
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)

    return await send_weekly_digest(db, supervisor_id, start, now)


async def schedule_digest_delivery(
    db: AsyncSession, supervisor_id: str, preferred_day: str, preferred_time: str,
) -> dict:
    """Updates the digest schedule in preferences."""
    prefs = await get_notification_preferences(db, supervisor_id)

    if prefs:
        prefs.digest_day = preferred_day
        prefs.digest_time = preferred_time
        prefs.updated_at = datetime.now(timezone.utc)
        await db.flush()
        return {"updated": True, "day": preferred_day, "time": preferred_time}

    new_prefs = NotificationPreference(
        user_id=supervisor_id,
        channel=NotificationChannel.BOTH,
        real_time_severity="ORANGE,RED",
        digest_enabled=True,
        digest_day=preferred_day,
        digest_time=preferred_time,
    )
    db.add(new_prefs)
    await db.flush()
    return {"created": True, "day": preferred_day, "time": preferred_time}