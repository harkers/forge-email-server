"""
CloakLLM — PII redaction service.

Redacts PII from SENSITIVE-tier data before routing to cloud LLMs.
RESTRICTED-tier data is hard-blocked and never leaves Titan.

Uses spaCy NER for entity detection.
OQ-06: en_core_web_sm for MVP; en_core_web_trf for production.
"""

import re
import spacy
from typing import Literal
from app.config import get_settings
from app.models.domain import DataTier

settings = get_settings()

_nlp_cache: spacy.Language | None = None


def _load_model() -> spacy.Language:
    global _nlp_cache
    if _nlp_cache is None:
        try:
            _nlp_cache = spacy.load(settings.cloakllm_spacy_model)
        except OSError:
            raise RuntimeError(
                f"spaCy model '{settings.cloakllm_spacy_model}' not found. "
                "Run: python -m spacy download en_core_web_sm"
            )
    return _nlp_cache


# Entity types to redact — mapped from spaCy labels to replacement tokens
ENTITY_REDACTORS: dict[str, str] = {
    "PERSON": "[PERSON]",
    "ORG": "[ORG]",
    "GPE": "[LOCATION]",
    "LOC": "[LOCATION]",
    "DATE": "[DATE]",
    "TIME": "[TIME]",
    "MONEY": "[MONEY]",
    "EMAIL": "[EMAIL]",
    "PHONE": "[PHONE]",
    "URL": "[URL]",
    "PERCENT": "[PERCENT]",
    "CARDINAL": "[NUMBER]",
    "ORDINAL": "[ORDINAL]",
    # Additional clinical/legal entities (sm model)
    "NORP": "[NATIONALITY]",
    "FAC": "[FACILITY]",
    "PRODUCT": "[PRODUCT]",
    "EVENT": "[EVENT]",
    "LAW": "[LAW]",
    "WORK_OF_ART": "[TITLE]",
}

# Regex patterns for unstructured PII
REGEX_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "[EMAIL]"),
    (re.compile(r"\b\+?[\d\s\-\(\)]{10,15}\b"), "[PHONE]"),
    (re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"), "[CARD_NUMBER]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
    (re.compile(r"\b[A-Z]{1,2}\d{6,8}\b"), "[ID_NUMBER]"),
]


def cloak_text(
    text: str,
    tier: Literal["sensitive", "restricted"],
) -> str:
    """
    Redact PII entities from text according to the data tier.

    - SENSITIVE: redaction applied, cloud routing permitted after redaction
    - RESTRICTED: raises ValueError — must never reach cloud

    Returns the redacted text.
    """
    if tier == "restricted":
        raise ValueError(
            "RESTRICTED-tier data cannot be processed by CloakLLM. "
            "Hard-block: route to local model only."
        )

    nlp = _load_model()
    doc = nlp(text)
    redacted = text

    # SpaCy entity redaction (offset-based to preserve string positions)
    entities = [(e.text, e.label_, e.start_char, e.end_char) for e in doc.ents]
    for entity_text, label, start, end in reversed(entities):
        replacement = ENTITY_REDACTORS.get(label, f"[{label}]")
        redacted = redacted[:start] + replacement + redacted[end:]

    # Regex-based redaction for structured patterns spaCy might miss
    for pattern, replacement in REGEX_PATTERNS:
        redacted = pattern.sub(replacement, redacted)

    return redacted


def is_restricted(text: str) -> bool:
    """
    Fast pre-check: does text contain indicators of RESTRICTED-tier content?

    Used as a guard before even loading the NLP model.
    This is a heuristic — definitive classification happens at intake.
    """
    restricted_indicators = [
        "patient id", "subject id", "clinical trial id", "ct id",
        "eudract", "ctr number", "protocol number",
        "adverse event", "serious adverse", "sae ", "susar",
        "case id", "case number", "safety case",
        "unblinded", "blinded", "randomisation",
    ]
    text_lower = text.lower()
    return any(ind in text_lower for ind in restricted_indicators)


def classify_and_redact(
    text: str,
    tier: str,
) -> dict:
    """
    Main CloakLLM entry point.

    Classifies the text, applies redaction if appropriate,
    and returns the result with routing instruction.

    Returns:
        {
            "original_length": int,
            "redacted_length": int,
            "redacted_text": str,
            "routing": "local" | "cloud",
            "tier_confirmed": str,
            "warnings": list[str],
        }
    """
    tier = tier.lower()
    routing = "cloud" if tier in ("public", "internal", "sensitive") else "local"
    warnings = []

    if is_restricted(text) and tier != "restricted":
        warnings.append("Text contains RESTRICTED-tier indicators; recommend upgrading to RESTRICTED")

    if tier == "restricted":
        raise ValueError(
            "RESTRICTED data — hard block. "
            "Do not call CloakLLM for this text. Route to local model only."
        )

    redacted = cloak_text(text, tier=tier)  # type: ignore[arg-type]

    return {
        "original_length": len(text),
        "redacted_length": len(redacted),
        "redacted_text": redacted,
        "routing": routing,
        "tier_confirmed": tier,
        "warnings": warnings,
    }
