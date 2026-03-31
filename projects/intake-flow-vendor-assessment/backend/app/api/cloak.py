"""
CloakLLM API — for testing redaction and tier classification.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.cloakllm import classify_and_redact, is_restricted

router = APIRouter()


class CloakRequest(BaseModel):
    text: str
    tier: str  # public | internal | sensitive | restricted


class CloakResponse(BaseModel):
    original_length: int
    redacted_length: int
    redacted_text: str
    routing: str
    tier_confirmed: str
    warnings: list[str]


@router.post("/redact", response_model=CloakResponse)
async def redact_text(request: CloakRequest):
    """
    Test CloakLLM redaction on a single text input.

    RESTRICTED tier will raise HTTP 422 — this is intentional.
    """
    try:
        result = classify_and_redact(request.text, request.tier)
        return CloakResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/restricted-check")
async def check_restricted(text: str):
    """Fast pre-check: does text contain RESTRICTED-tier indicators?"""
    return {"is_restricted": is_restricted(text)}
