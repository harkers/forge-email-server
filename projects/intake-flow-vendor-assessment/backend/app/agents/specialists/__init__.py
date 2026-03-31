"""Specialist agent stubs — implement each when the MVP build order reaches that step."""

from app.agents.base import BaseAgent


class DataProtectionAgent(BaseAgent):
    """Step 3 — GDPR / UK GDPR layer."""
    step_name = "data_protection"

    async def run(self, input: dict, context: dict) -> dict:
        return {
            "domain": "data_protection",
            "findings": [],
            "summary": "DataProtectionAgent stub — implement per OQ-04 MVP build order",
            "status": "pending_implementation",
        }


class RegulatoryAgent(BaseAgent):
    """Step 3 — GxP, FDA, EU GMP, ICH, pharmacovigilance."""
    step_name = "regulatory"

    async def run(self, input: dict, context: dict) -> dict:
        return {
            "domain": "regulatory",
            "findings": [],
            "summary": "RegulatoryAgent stub",
            "status": "pending_implementation",
        }


class InfoSecAgent(BaseAgent):
    """Step 3 — ISO 27001, SOC 2, Cyber Essentials, pen test."""
    step_name = "infosec"

    async def run(self, input: dict, context: dict) -> dict:
        return {
            "domain": "infosec",
            "findings": [],
            "summary": "InfoSecAgent stub",
            "status": "pending_implementation",
        }


class ContractualAgent(BaseAgent):
    """Step 3 — DPA review, liability, audit rights, breach SLA."""
    step_name = "contractual"

    async def run(self, input: dict, context: dict) -> dict:
        return {
            "domain": "contractual",
            "findings": [],
            "summary": "ContractualAgent stub",
            "status": "pending_implementation",
        }


class AIGovernanceAgent(BaseAgent):
    """Step 3 — EU AI Act risk classification, human oversight, training data."""
    step_name = "ai_governance"

    async def run(self, input: dict, context: dict) -> dict:
        return {
            "domain": "ai_governance",
            "findings": [],
            "summary": "AIGovernanceAgent stub",
            "status": "pending_implementation",
        }


class GapAnalysisAgent(BaseAgent):
    """Step 4 — Cross-domain contradiction detection."""
    step_name = "gap_analysis"

    async def run(self, input: dict, context: dict) -> dict:
        return {
            "domain": "gap_analysis",
            "contradictions": [],
            "clarification_queries": [],
            "summary": "GapAnalysisAgent stub",
            "status": "pending_implementation",
        }


class ScoringAgent(BaseAgent):
    """Step 5 — Weighted risk matrix, tier 1–4 roll-up."""
    step_name = "scoring"

    async def run(self, input: dict, context: dict) -> dict:
        # Placeholder: returns tier 2 until OQ-04 weights are validated
        return {
            "tier": 2,
            "total_score": 0.0,
            "domain_scores": {},
            "edge_rules_triggered": [],
            "decision": "approve_with_conditions",
            "summary": "ScoringAgent stub — placeholder equal weights; implement per OQ-04 spec",
            "status": "pending_implementation",
        }


class RemediationAgent(BaseAgent):
    """Step 6 — Prioritised action plan from scored findings."""
    step_name = "remediation"

    async def run(self, input: dict, context: dict) -> dict:
        return {
            "actions": [],
            "summary": "RemediationAgent stub",
            "status": "pending_implementation",
        }


class ReportSynthesisAgent(BaseAgent):
    """Step 7 — Full output package."""
    step_name = "report_synthesis"

    async def run(self, input: dict, context: dict) -> dict:
        return {
            "executive_summary": "",
            "full_report": "",
            "ropa_entry": {},
            "sub_processor_row": {},
            "remediation_plan": {},
            "summary": "ReportSynthesisAgent stub",
            "status": "pending_implementation",
        }
