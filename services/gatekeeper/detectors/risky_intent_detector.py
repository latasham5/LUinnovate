"""
Risky Intent Detector — Hugging Face integration for dangerous intent analysis.

Analyzes whether the intent itself is dangerous beyond just the data content.
"""


async def detect_risky_intent(raw_prompt: str) -> float:
    """
    Use Hugging Face toxic-bert model to analyze whether the prompt's
    intent is dangerous beyond the data it contains.

    Returns a risk score from 0.0 (safe) to 1.0 (dangerous).
    """
    try:
        from integrations.huggingface_client import classify_toxicity
        score = await classify_toxicity(raw_prompt)
        return score
    except Exception:
        pass

    # Fallback: keyword-based risky intent detection
    RISKY_PHRASES = [
        "bypass", "circumvent", "ignore restrictions", "override policy",
        "hack", "exploit", "jailbreak", "pretend you are",
        "ignore your instructions", "act as if", "disregard",
    ]
    prompt_lower = raw_prompt.lower()
    risk = 0.0
    for phrase in RISKY_PHRASES:
        if phrase in prompt_lower:
            risk += 0.3
    return min(risk, 1.0)
