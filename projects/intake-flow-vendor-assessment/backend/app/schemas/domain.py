from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.domain import DataTier, AssessmentStatus, VendorRiskTier


# ─── Vendor ────────────────────────────────────────────────────────────────────

class VendorCreate(BaseModel):
    name: str = Field(max_length=255)
    registered_jurisdiction: str = Field(max_length=100)
    services_in_scope: list[str] = Field(default_factory=list)
    data_categories: list[str] = Field(default_factory=list)
    has_special_category: bool = False
    has_cross_border_transfers: bool = False


class VendorOut(BaseModel):
    id: UUID
    name: str
    registered_jurisdiction: str
    services_in_scope: list[str]
    data_categories: list[str]
    has_special_category: bool
    has_cross_border_transfers: bool
    intake_tier: DataTier
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Assessment ────────────────────────────────────────────────────────────────

class AssessmentCreate(BaseModel):
    vendor_id: UUID | None = None  # if not provided, a new vendor is created
    vendor: VendorCreate | None = None
    initiated_by: str = Field(max_length=255)
    trigger_type: str = "manual"


class AssessmentOut(BaseModel):
    id: UUID
    reference: str
    vendor_id: UUID
    client_scope: str
    initiated_by: str
    trigger_type: str
    status: AssessmentStatus
    current_step: int
    risk_tier: int | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class AssessmentDetailOut(AssessmentOut):
    intake_output: dict | None = None
    specialist_outputs: dict | None = None
    gap_analysis_output: dict | None = None
    scoring_output: dict | None = None
    remediation_output: dict | None = None
    report_output: dict | None = None
    review_notes: str | None = None
    review_decision: str | None = None


class AssessmentTriggerIn(BaseModel):
    vendor_name: str = Field(max_length=255)
    registered_jurisdiction: str = Field(max_length=100)
    services_in_scope: list[str]
    data_categories: list[str] = Field(default_factory=list)
    has_special_category: bool = False
    has_cross_border_transfers: bool = False
    initiated_by: str = Field(max_length=255)
    trigger_type: str = "manual"


# ─── Findings ─────────────────────────────────────────────────────────────────

class FindingOut(BaseModel):
    id: UUID
    domain: str
    severity: str
    description: str
    evidence_ref: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Review Gate ──────────────────────────────────────────────────────────────

class ReviewDecisionIn(BaseModel):
    decision: str = Field(pattern="^(approved|rejected)$")
    notes: str | None = None
