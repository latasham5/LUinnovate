"""
Notification Client — Slack/Teams webhook dispatcher.

Used by Developer 3 for all alert notifications.
"""

import httpx
from config.settings import settings


async def send_slack_message(message: str, channel: str = None) -> bool:
    """
    Send a message via Slack webhook.
    Returns True if successful, False otherwise.
    """
    webhook_url = settings.SLACK_WEBHOOK_URL

    if not webhook_url:
        # No webhook configured — log locally in development
        print(f"[NOTIFICATION - Slack] {message}")
        return True

    payload = {"text": message}
    if channel:
        payload["channel"] = channel

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(webhook_url, json=payload)
            return response.status_code == 200
    except httpx.RequestError:
        return False


async def send_teams_message(message: str, webhook_url: str = None) -> bool:
    """
    Send a message via Microsoft Teams webhook.
    Returns True if successful, False otherwise.
    """
    url = webhook_url or settings.SLACK_WEBHOOK_URL  # Reuse same env var for now

    if not url:
        print(f"[NOTIFICATION - Teams] {message}")
        return True

    payload = {
        "@type": "MessageCard",
        "summary": "Phantom App Alert",
        "sections": [
            {
                "activityTitle": "Phantom App Security Alert",
                "text": message,
            }
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            return response.status_code == 200
    except httpx.RequestError:
        return False


async def send_notification(recipient_id: str, channel: str, message: str) -> bool:
    """
    Dispatch notification via the appropriate channel.

    Args:
        recipient_id: The ID of the person to notify
        channel: "slack" or "teams"
        message: The notification message
    """
    formatted_message = f"[To: {recipient_id}] {message}"

    if channel.lower() == "slack":
        return await send_slack_message(formatted_message)
    elif channel.lower() == "teams":
        return await send_teams_message(formatted_message)
    else:
        print(f"[NOTIFICATION - {channel}] {formatted_message}")
        return True
