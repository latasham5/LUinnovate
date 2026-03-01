"""
spaCy Client — model loading and NER pipeline.

Used by Developer 1 for keyword extraction and named entity recognition.
"""

import spacy
from config.constants import SPACY_MODEL

# Lazy-loaded spaCy model
_nlp = None


def get_nlp():
    """Load and cache the spaCy model."""
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load(SPACY_MODEL)
        except OSError:
            # Model not installed — download it
            from spacy.cli import download
            download(SPACY_MODEL)
            _nlp = spacy.load(SPACY_MODEL)
    return _nlp


def extract_entities(text: str) -> list[dict]:
    """
    Run spaCy NER on text and return detected entities.

    Returns list of dicts with: text, label, start, end
    """
    nlp = get_nlp()
    doc = nlp(text)

    entities = []
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
        })

    return entities


def extract_tokens(text: str) -> list[dict]:
    """
    Tokenize text and return tokens with POS tags.
    Useful for identifying sensitive terms in context.
    """
    nlp = get_nlp()
    doc = nlp(text)

    return [
        {"text": token.text, "pos": token.pos_, "is_stop": token.is_stop}
        for token in doc
    ]
