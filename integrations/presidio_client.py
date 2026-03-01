"""
Microsoft Presidio Client — PII detection and anonymization.

Used by Developer 1 for detecting names, SSNs, addresses, phone numbers, emails.
"""

from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine

# Lazy-loaded engines
_analyzer = None
_anonymizer = None


def get_analyzer() -> AnalyzerEngine:
    """Load and cache the Presidio analyzer engine."""
    global _analyzer
    if _analyzer is None:
        _analyzer = AnalyzerEngine()
    return _analyzer


def get_anonymizer() -> AnonymizerEngine:
    """Load and cache the Presidio anonymizer engine."""
    global _anonymizer
    if _anonymizer is None:
        _anonymizer = AnonymizerEngine()
    return _anonymizer


def analyze_text(text: str, language: str = "en") -> list[dict]:
    """
    Analyze text for PII entities using Presidio.

    Returns list of detected entities with type, start, end, and score.
    """
    analyzer = get_analyzer()

    results: list[RecognizerResult] = analyzer.analyze(
        text=text,
        language=language,
        entities=[
            "PERSON",
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "US_SSN",
            "CREDIT_CARD",
            "IP_ADDRESS",
            "US_DRIVER_LICENSE",
            "LOCATION",
        ],
    )

    return [
        {
            "entity_type": result.entity_type,
            "start": result.start,
            "end": result.end,
            "score": result.score,
            "text": text[result.start:result.end],
        }
        for result in results
    ]


def anonymize_text(text: str, language: str = "en") -> str:
    """
    Anonymize detected PII in text, replacing with placeholder tokens.
    """
    analyzer = get_analyzer()
    anonymizer = get_anonymizer()

    results = analyzer.analyze(text=text, language=language)
    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)

    return anonymized.text
