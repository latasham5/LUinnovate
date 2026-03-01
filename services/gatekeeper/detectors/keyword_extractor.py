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

    # TODO: Load spaCy model from integrations.spacy_client
    # TODO: Run NER pipeline on raw_prompt
    # TODO: Match entities against flagged keyword lists
    # TODO: Return DetectedElement for each match

    return detected
