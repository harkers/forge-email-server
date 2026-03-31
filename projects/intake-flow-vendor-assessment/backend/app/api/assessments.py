"""
Assessment API routes.
"""

import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session
from app.models.domain import Assessment, Vendor, AssessmentStatus
from app.schemas import AssessmentOut, AssessmentDetailOut, AssessmentTriggerIn, ReviewDecisionIn
from app.agents.dpm import DPM

router = APIRouter()


async def _run_pipeline_background(assessment_id: uuid.UUID):
    """Background pipeline runner — called after assessment creation."""
    async with async_session() as db:
        dpm = DPM(db)
        try:
            await dpm.run(assessment_id)
        except Exception as e:
            print(f"Pipeline failed for {assessment_id}: {e}")


@router.post("/", response_model=AssessmentOut, status_code=201)
async def create_assessment(
    trigger_in: AssessmentTriggerIn,
    background: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a new vendor assessment.

    Creates or links a vendor record, creates the assessment record,
    and kicks off the pipeline in the background.
    """
    # Find or create vendor
    result = await db.execute(
        select(Vendor).where(Vendor.name == trigger_in.vendor_name)
    )
    vendor = result.scalar_one_or_none()

    if not vendor:
        vendor = Vendor(
            name=trigger_in.vendor_name,
            registered_jurisdiction=trigger_in.registered_jurisdiction,
            services_in_scope=trigger_in.services_in_scope,
            data_categories=trigger_in.data_categories,
            has_special_category=trigger_in.has_special_category,
            has_cross_border_transfers=trigger_in.has_cross_border_transfers,
        )
        db.add(vendor)
        await db.flush()

    # Create assessment
    count_result = await db.execute(select(Assessment))
    seq = len(count_result.scalars().all()) + 1
    ref = f"IFV-{datetime.utcnow().year}-{seq:04d}"

    assessment = Assessment(
        vendor_id=vendor.id,
        reference=ref,
        initiated_by=trigger_in.initiated_by,
        trigger_type=trigger_in.trigger_type,
        status=AssessmentStatus.DRAFT,
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)

    # Kick off pipeline in background
    background.add_task(_run_pipeline_background, assessment.id)

    return assessment


@router.get("/", response_model=list[AssessmentOut])
async def list_assessments(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all assessments, optionally filtered by status."""
    query = select(Assessment).order_by(Assessment.created_at.desc())
    if status:
        query = query.where(Assessment.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{assessment_id}", response_model=AssessmentDetailOut)
async def get_assessment(assessment_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get full assessment detail including all step outputs."""
    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@router.post("/{assessment_id}/review", response_model=AssessmentOut)
async def submit_review_decision(
    assessment_id: uuid.UUID,
    decision_in: ReviewDecisionIn,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a human review decision (approved / rejected).

    On approval: status → APPROVED, completed_at set.
    On rejection: status → REJECTED, rework loop is triggered (Step 9b).
    """
    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if assessment.status != AssessmentStatus.PENDING_REVIEW.value:
        raise HTTPException(
            status_code=400,
            detail=f"Assessment is not pending review (status: {assessment.status})"
        )

    assessment.review_decision = decision_in.decision
    assessment.review_notes = decision_in.notes
    assessment.updated_at = datetime.utcnow()

    if decision_in.decision == "approved":
        assessment.status = AssessmentStatus.APPROVED.value
        assessment.completed_at = datetime.utcnow()
    else:
        assessment.status = AssessmentStatus.REJECTED.value
        # TODO: trigger Step 9b rework loop

    await db.commit()
    await db.refresh(assessment)
    return assessment
