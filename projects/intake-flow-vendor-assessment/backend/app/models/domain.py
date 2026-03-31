import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Text, Enum, ForeignKey, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class DataTier(str, enum.Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"


class AssessmentStatus(str, enum.Enum):
    DRAFT = "draft"
    INTAKE_PARSING = "intake_parsing"
    SPECIALIST_ASSESSMENT = "specialist_assessment"
    GAP_ANALYSIS = "gap_analysis"
    SCORING = "scoring"
    REMEDIATION = "remediation"
    REPORT_SYNTHESIS = "report_synthesis"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class VendorRiskTier(int, enum.Enum):
    TIER_1 = 1  # Approve — minimal risk
    TIER_2 = 2  # Approve with conditions
    TIER_3 = 3  # Approve with oversight — DPO sign-off required
    TIER_4 = 4  # Reject — do not engage


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    registered_jurisdiction: Mapped[str] = mapped_column(String(100), nullable=False)
    services_in_scope: Mapped[list] = mapped_column(JSON, default=list)  # service line names
    data_categories: Mapped[list] = mapped_column(JSON, default=list)
    has_special_category: Mapped[bool] = mapped_column(default=False)
    has_cross_border_transfers: Mapped[bool] = mapped_column(default=False)
    intake_tier: Mapped[str] = mapped_column(String(20), default=DataTier.INTERNAL)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    assessments: Mapped[list["Assessment"]] = relationship(back_populates="vendor")


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)

    # Metadata
    reference: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # e.g. IFV-2026-001
    client_scope: Mapped[str] = mapped_column(String(100), default="ProPharma Group")
    initiated_by: Mapped[str] = mapped_column(String(255), nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(50), default="manual")  # manual | scheduled | automated

    # Pipeline state
    status: Mapped[str] = mapped_column(String(30), default=AssessmentStatus.DRAFT)
    current_step: Mapped[int] = mapped_column(default=1)  # 1-9+

    # Intake output (Step 1)
    intake_output: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Specialist outputs (Step 3) — keyed by domain
    specialist_outputs: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Gap analysis output (Step 4)
    gap_analysis_output: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Scoring output (Step 5)
    scoring_output: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    risk_tier: Mapped[int | None] = mapped_column(nullable=True)

    # Remediation (Step 6)
    remediation_output: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Report synthesis (Step 7)
    report_output: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Review gate (Step 8)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_decision: Mapped[str | None] = mapped_column(String(20), nullable=True)  # approved | rejected

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    __table_args__ = (
        Index("ix_assessments_status", "status"),
        Index("ix_assessments_vendor_id", "vendor_id"),
        Index("ix_assessments_reference", "reference"),
    )

    vendor: Mapped[Vendor] = relationship(back_populates="assessments")
    findings: Mapped[list["Finding"]] = relationship(back_populates="assessment")


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    domain: Mapped[str] = mapped_column(String(50), nullable=False)  # data_protection | regulatory | infosec | contractual | ai_governance
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # critical | high | medium | low | informational
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    assessment: Mapped[Assessment] = relationship(back_populates="findings")
