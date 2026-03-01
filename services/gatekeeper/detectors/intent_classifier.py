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
    # TODO: Call integrations.huggingface_client.classify_zero_shot
    # TODO: Map the top label to IntentType
    # TODO: Return the classified intent

    # Placeholder — returns UNKNOWN until HF integration is wired
    return IntentType.UNKNOWN
