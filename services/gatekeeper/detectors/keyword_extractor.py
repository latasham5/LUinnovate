"""
Keyword Extractor — spaCy integration for flagged terms.

Detects: trade secrets, competitor names, proprietary language, internal code names.
"""

from shared.schemas.analysis_result import DetectedElement
from shared.enums import RiskCategory


def extract_keywords(raw_prompt: str) -> list[DetectedElement]:
    """
    Use spaCy NER to extract flagged terms from the prompt.

    Identifies:
    - Trade secrets and proprietary terms
    - Competitor names
    - Internal code names
    - Proprietary language
    """
    detected = []

    # Proprietary / competitor keywords to flag
    PROPRIETARY_TERMS = [
        "trade secret", "proprietary", "confidential formula",
        "secret recipe", "intellectual property", "patent pending",
        "competitive advantage", "market strategy", "acquisition target",
    ]
    COMPETITOR_NAMES = [
        "pepsi", "pepsico", "dr pepper", "keurig", "monster energy",
        "red bull", "nestle", "danone", "unilever",
    ]

    prompt_lower = raw_prompt.lower()

    # Check proprietary terms
    for term in PROPRIETARY_TERMS:
        idx = prompt_lower.find(term)
        if idx != -1:
            detected.append(DetectedElement(
                text=raw_prompt[idx:idx + len(term)],
                category=RiskCategory.PROPRIETARY,
                start_index=idx, end_index=idx + len(term),
                confidence=0.8,
            ))

    # Check competitor names
    for name in COMPETITOR_NAMES:
        idx = prompt_lower.find(name)
        if idx != -1:
            detected.append(DetectedElement(
                text=raw_prompt[idx:idx + len(name)],
                category=RiskCategory.PROPRIETARY,
                start_index=idx, end_index=idx + len(name),
                confidence=0.7,
            ))

    # Use spaCy NER to find organizations and people that could be sensitive
    try:
        from integrations.spacy_client import extract_entities
        entities = extract_entities(raw_prompt)
        for ent in entities:
            if ent["label"] == "ORG":
                detected.append(DetectedElement(
                    text=ent["text"],
                    category=RiskCategory.PROPRIETARY,
                    start_index=ent["start"], end_index=ent["end"],
                    confidence=0.5,
                ))
    except Exception:
        pass  # spaCy not available, keyword matching still works

    return detected
