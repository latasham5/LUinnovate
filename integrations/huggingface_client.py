"""
Hugging Face Inference API Client.

Used by Developer 1 for:
- Intent classification (zero-shot via facebook/bart-large-mnli)
- Risky intent detection (toxicity via unitary/toxic-bert)
"""

import httpx
from config.settings import settings
from config.constants import HF_INTENT_MODEL, HF_RISKY_INTENT_MODEL

HF_API_URL = "https://api-inference.huggingface.co/models"


async def classify_zero_shot(text: str, candidate_labels: list[str]) -> dict:
    """
    Call Hugging Face zero-shot classification API.

    Uses facebook/bart-large-mnli for intent classification.
    Returns: {labels: [...], scores: [...], sequence: "..."}
    """
    url = f"{HF_API_URL}/{HF_INTENT_MODEL}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"},
            json={
                "inputs": text,
                "parameters": {"candidate_labels": candidate_labels},
            },
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}


async def classify_toxicity(text: str) -> float:
    """
    Call Hugging Face text classification API for toxicity detection.

    Uses unitary/toxic-bert to determine if intent is dangerous.
    Returns a risk score from 0.0 (safe) to 1.0 (toxic/dangerous).
    """
    url = f"{HF_API_URL}/{HF_RISKY_INTENT_MODEL}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"},
            json={"inputs": text},
        )

        if response.status_code == 200:
            result = response.json()
            # Extract the toxicity score from the response
            if isinstance(result, list) and len(result) > 0:
                classifications = result[0] if isinstance(result[0], list) else result
                for item in classifications:
                    if item.get("label", "").lower() == "toxic":
                        return item.get("score", 0.0)
            return 0.0
        else:
            # On error, return 0.0 (safe) to avoid blocking on API failures
            return 0.0
