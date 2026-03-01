"""
CokeGPT Client — integration with Coca-Cola's internal AI.

In development mode, returns mock responses.
In production, forwards to the real CokeGPT API.
"""

import httpx
from config.settings import settings
from shared.exceptions import CokeGPTError


# Mock responses for development
MOCK_RESPONSES = [
    "Based on the information provided, here is a summary of the key points...",
    "I've analyzed your request and prepared the following response...",
    "Here are the results of your query. Please note this is generated content...",
    "I'd be happy to help with that. Here's what I found...",
]

_mock_counter = 0


async def send_to_cokegpt(prompt: str, user_id: str) -> str:
    """
    Send a prompt to CokeGPT and return the response.

    In development (mock mode), returns a canned response.
    In production, calls the real CokeGPT API.
    """
    if settings.is_mock_cokegpt:
        return _get_mock_response(prompt)

    return await _call_real_cokegpt(prompt, user_id)


def _get_mock_response(prompt: str) -> str:
    """Return a mock CokeGPT response for development."""
    global _mock_counter
    response = MOCK_RESPONSES[_mock_counter % len(MOCK_RESPONSES)]
    _mock_counter += 1
    return f"[MOCK CokeGPT Response] {response}\n\nOriginal prompt length: {len(prompt)} characters."


async def _call_real_cokegpt(prompt: str, user_id: str) -> str:
    """Call the real CokeGPT API."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://cokegpt-internal.coca-cola.com/api/v1/chat",  # Placeholder URL
                headers={
                    "Authorization": f"Bearer {settings.COKEGPT_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "prompt": prompt,
                    "user_id": user_id,
                    "max_tokens": 2000,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

    except httpx.HTTPStatusError as e:
        raise CokeGPTError(f"API returned status {e.response.status_code}")
    except httpx.RequestError as e:
        raise CokeGPTError(f"Request failed: {str(e)}")
