"""
Data Protection Manager — Orchestrator Agent (Step 2).

The DPM owns the pipeline state, dispatches specialist agents,
holds context across all steps, and controls sequencing.

It does NOT produce assessment content itself.
"""

import uuid
import json
from datetime import datetime
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import BaseAgent, AgentError
from app.agents.specialists.intake import IntakeAgent
from app.models.domain import Assessment, AssessmentStatus, DataTier
from app.redis import get_redis


class DPM:
    """
    Orchestrator for the vendor assessment pipeline.

    Call `run(assessment_id)` to execute a full pipeline run.
    The DPM holds state in Redis between steps and updates PostgreSQL on step completion.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Pipeline Execution ──────────────────────────────────────────────────

    async def run(self, assessment_id: uuid.UUID) -> dict:
        """
        Execute the full pipeline for an assessment.

        Returns a summary dict with all step outputs.
        """
        # Load assessment
        result = await self.db.execute(
            select(Assessment).where(Assessment.id == assessment_id)
        )
        assessment = result.scalar_one_or_none()
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # Shared pipeline context
        context = {
            "assessment_id": str(assessment_id),
            "vendor_id": str(assessment.vendor_id),
            "reference": assessment.reference,
            "intake_tier": assessment.vendor.intake_tier,
            "service_lines": assessment.vendor.services_in_scope,
            "steps_completed": [],
            "step_outputs": {},
        }

        redis = await get_redis()

        # ── Step 1: Intake Agent ─────────────────────────────────────────
        await self._update_status(assessment, AssessmentStatus.INTAKE_PARSING, step=1)
        intake_input = {"trigger": {
            "vendor_name": assessment.vendor.name,
            "registered_jurisdiction": assessment.vendor.registered_jurisdiction,
            "services_in_scope": assessment.vendor.services_in_scope,
            "data_categories": assessment.vendor.data_categories,
            "has_special_category": assessment.vendor.has_special_category,
            "has_cross_border_transfers": assessment.vendor.has_cross_border_transfers,
            "initiated_by": assessment.initiated_by,
            "trigger_type": assessment.trigger_type,
        }}
        intake_agent = IntakeAgent()
        intake_output = await self._execute_step(
            "step_1_intake", intake_agent, intake_input, context, redis
        )
        assessment.intake_output = intake_output
        assessment.vendor.intake_tier = intake_output.get("intake_tier", DataTier.INTERNAL)
        context["intake_tier"] = assessment.vendor.intake_tier
        context["steps_completed"].append(1)

        # ── Step 3: Specialist Agents (parallel) ───────────────────────────
        await self._update_status(assessment, AssessmentStatus.SPECIALIST_ASSESSMENT, step=3)
        specialist_outputs = await self._run_specialists(intake_output, context, redis)
        assessment.specialist_outputs = specialist_outputs
        context["specialist_outputs"] = specialist_outputs
        context["steps_completed"].append(3)

        # ── Step 4: Gap Analysis ───────────────────────────────────────────
        await self._update_status(assessment, AssessmentStatus.GAP_ANALYSIS, step=4)
        gap_output = await self._run_gap_analysis(specialist_outputs, context, redis)
        assessment.gap_analysis_output = gap_output
        context["gap_output"] = gap_output
        context["steps_completed"].append(4)

        # ── Step 5: Scoring ────────────────────────────────────────────────
        await self._update_status(assessment, AssessmentStatus.SCORING, step=5)
        scoring_output = await self._run_scoring(gap_output, context, redis)
        assessment.scoring_output = scoring_output
        assessment.risk_tier = scoring_output.get("tier")
        context["scoring_output"] = scoring_output
        context["steps_completed"].append(5)

        # ── Step 6: Remediation ───────────────────────────────────────────
        await self._update_status(assessment, AssessmentStatus.REMEDIATION, step=6)
        remediation_output = await self._run_remediation(scoring_output, context, redis)
        assessment.remediation_output = remediation_output
        context["remediation_output"] = remediation_output
        context["steps_completed"].append(6)

        # ── Step 7: Report Synthesis ───────────────────────────────────────
        await self._update_status(assessment, AssessmentStatus.REPORT_SYNTHESIS, step=7)
        report_output = await self._run_report_synthesis(context, redis)
        assessment.report_output = report_output
        context["report_output"] = report_output
        context["steps_completed"].append(7)

        # ── Step 8: Review Gate ───────────────────────────────────────────
        await self._update_status(assessment, AssessmentStatus.PENDING_REVIEW, step=8)
        context["steps_completed"].append(8)

        assessment.updated_at = datetime.utcnow()
        await self.db.commit()

        return {
            "assessment_id": str(assessment_id),
            "reference": assessment.reference,
            "status": assessment.status,
            "risk_tier": assessment.risk_tier,
            "steps_completed": context["steps_completed"],
            "pipeline_complete": True,
            "review_required": True,
        }

    # ── Specialist Dispatch ─────────────────────────────────────────────────

    async def _run_specialists(
        self, intake_output: dict, context: dict, redis
    ) -> dict[str, dict]:
        """
        Dispatch all five specialist agents in parallel.
        Each returns a dict keyed by domain.
        """
        specialist_map = {
            "data_protection": "DataProtectionAgent",
            "regulatory": "RegulatoryAgent",
            "infosec": "InfoSecAgent",
            "contractual": "ContractualAgent",
            "ai_governance": "AIGovernanceAgent",
        }

        # Lazy-load specialist agents to avoid circular imports
        from app.agents.specialists.data_protection import DataProtectionAgent
        from app.agents.specialists.regulatory import RegulatoryAgent
        from app.agents.specialists.infosec import InfoSecAgent
        from app.agents.specialists.contractual import ContractualAgent
        from app.agents.specialists.ai_governance import AIGovernanceAgent

        agent_map: dict[str, BaseAgent] = {
            "data_protection": DataProtectionAgent(),
            "regulatory": RegulatoryAgent(),
            "infosec": InfoSecAgent(),
            "contractual": ContractualAgent(),
            "ai_governance": AIGovernanceAgent(),
        }

        import asyncio
        tasks = {}
        for domain, agent in agent_map.items():
            specialist_input = {
                "intake_output": intake_output,
                "domain": domain,
                "service_lines": context["service_lines"],
            }
            tasks[domain] = self._execute_step(
                f"step_3_{domain}", agent, specialist_input, context, redis
            )

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        outputs = {}
        for domain, result in zip(specialist_map.keys(), results):
            if isinstance(result, Exception):
                outputs[domain] = {"error": str(result), "status": "failed"}
            else:
                outputs[domain] = result

        return outputs

    # ── Step Implementations (placeholder shells) ─────────────────────────

    async def _run_gap_analysis(
        self, specialist_outputs: dict, context: dict, redis
    ) -> dict:
        from app.agents.specialists.gap_analysis import GapAnalysisAgent
        agent = GapAnalysisAgent()
        return await self._execute_step(
            "step_4_gap_analysis", agent,
            {"specialist_outputs": specialist_outputs}, context, redis
        )

    async def _run_scoring(
        self, gap_output: dict, context: dict, redis
    ) -> dict:
        from app.agents.specialists.scoring import ScoringAgent
        agent = ScoringAgent()
        return await self._execute_step(
            "step_5_scoring", agent,
            {"gap_output": gap_output, "service_lines": context["service_lines"]}, context, redis
        )

    async def _run_remediation(
        self, scoring_output: dict, context: dict, redis
    ) -> dict:
        from app.agents.specialists.remediation import RemediationAgent
        agent = RemediationAgent()
        return await self._execute_step(
            "step_6_remediation", agent,
            {"scoring_output": scoring_output}, context, redis
        )

    async def _run_report_synthesis(
        self, context: dict, redis
    ) -> dict:
        from app.agents.specialists.report_synthesis import ReportSynthesisAgent
        agent = ReportSynthesisAgent()
        return await self._execute_step(
            "step_7_report_synthesis", agent,
            {"context": {k: v for k, v in context.items() if k != "redis"}}, context, redis
        )

    # ── Core Step Executor ─────────────────────────────────────────────────

    async def _execute_step(
        self,
        step_key: str,
        agent: BaseAgent,
        step_input: dict,
        context: dict,
        redis,
    ) -> dict:
        """
        Execute a single agent step with Redis state persistence.
        """
        # Store input in Redis
        await redis.set(
            f"ifv:{context['assessment_id']}:{step_key}:input",
            json.dumps(step_input),
            ex=86400,
        )

        try:
            output = await agent.execute(step_input, context)
            await redis.set(
                f"ifv:{context['assessment_id']}:{step_key}:output",
                json.dumps(output),
                ex=86400,
            )
            return output
        except Exception as e:
            await redis.set(
                f"ifv:{context['assessment_id']}:{step_key}:error",
                str(e),
                ex=86400,
            )
            raise AgentError(f"{step_key} failed: {e}") from e

    async def _update_status(
        self, assessment: Assessment, status: AssessmentStatus, step: int
    ):
        assessment.status = status.value
        assessment.current_step = step
        assessment.updated_at = datetime.utcnow()
        await self.db.commit()
