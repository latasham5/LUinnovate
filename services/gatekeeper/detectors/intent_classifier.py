"""
Intent Classifier — Hugging Face integration for determining user goal.

Classifies: question, data paste, content generation, data extraction, summarization.
"""

from shared.enums import IntentType


# Mapping from Hugging Face zero-shot labels to our IntentType enum
LABEL_TO_INTENT = {
    "question": IntentType.QUESTION,
    "asking a question": IntentType.QUESTION,
    "pasting data": IntentType.DATA_PASTE,
    "sharing data": IntentType.DATA_PASTE,
    "generating content": IntentType.CONTENT_GENERATION,
    "writing": IntentType.CONTENT_GENERATION,
    "extracting data": IntentType.DATA_EXTRACTION,
    "data extraction": IntentType.DATA_EXTRACTION,
    "summarizing": IntentType.SUMMARIZATION,
    "summarization": IntentType.SUMMARIZATION,
}

CANDIDATE_LABELS = [
    "asking a question",
    "pasting data",
    "generating content",
    "extracting data",
    "summarizing",
]


async def classify_intent(raw_prompt: str) -> IntentType:
    """
    Use Hugging Face zero-shot classification to determine user intent.

    Uses facebook/bart-large-mnli for zero-shot classification.
    """
    try:
        from integrations.huggingface_client import classify_zero_shot
        result = await classify_zero_shot(raw_prompt, CANDIDATE_LABELS)

        if "error" not in result and "labels" in result:
            top_label = result["labels"][0]
            return LABEL_TO_INTENT.get(top_label, IntentType.UNKNOWN)
    except Exception:
        pass

    # Fallback: simple keyword-based classification
    prompt_lower = raw_prompt.lower()
    if any(q in prompt_lower for q in ["?", "what is", "how do", "why", "when", "where", "who"]):
        return IntentType.QUESTION
    elif any(d in prompt_lower for d in ["summarize", "summary", "tldr", "recap"]):
        return IntentType.SUMMARIZATION
    elif any(g in prompt_lower for g in ["write", "draft", "create", "generate", "compose"]):
        return IntentType.CONTENT_GENERATION
    elif any(e in prompt_lower for e in ["extract", "pull out", "find all", "list all"]):
        return IntentType.DATA_EXTRACTION
    elif len(raw_prompt) > 500:
        return IntentType.DATA_PASTE

    return IntentType.UNKNOWN
