"""
Intake Agent — Step 1.

Receives a raw vendor assessment trigger (manual, scheduled, or automated).
Parses the vendor brief, extracts key fields, classifies the data tier,
and produces a structured brief for the DPM.

No assessment logic runs here.
"""

import re
from app.agents.base import BaseAgent


PROPHARMA_SERVICE_LINES = [
    "Regulatory Affairs",
    "Pharmacovigilance",
    "Quality Assurance",
    "Clinical Operations",
    "Data Annotation and AI",
    "Medical Writing",
    "Biostatistics",
    "IT and Data Management",
]

SPECIAL_CATEGORY_KEYWORDS = [
    "health", "medical", "clinical", "pharmacovigilance", "adverse event",
    "patient", "diagnosis", "treatment", "biometric", "genetic",
    "racial", "ethnic", "political", "religious", "sexual orientation",
    "disability", "sae", "ae ", "serious adverse",
]

CROSS_BORDER_KEYWORDS = [
    "transfer", "eu", "uk", "us", "india", "philippines", "offshore",
    "sub-processor", "third country", "cross-border",
]


class IntakeAgent(BaseAgent):

    @property
    def step_name(self) -> str:
        return "intake"

    async def run(self, input: dict, context: dict) -> dict:
        trigger = input.get("trigger", {})
        vendor_name = trigger.get("vendor_name", "").strip()
        jurisdiction = trigger.get("registered_jurisdiction", "").strip()
        services = trigger.get("services_in_scope", [])
        data_categories = trigger.get("data_categories", [])
        has_special_category = trigger.get("has_special_category", False)
        has_cross_border = trigger.get("has_cross_border_transfers", False)
        initiated_by = trigger.get("initiated_by", "unknown")

        # ── 1. Classify data tier ──────────────────────────────────────────
        tier = self._classify_tier(
            has_special_category=has_special_category,
            has_cross_border=has_cross_border,
            data_categories=data_categories,
        )

        # ── 2. Match service lines ─────────────────────────────────────────
        matched_services = self._match_service_lines(services)

        # ── 3. Extract data categories from raw text ──────────────────────
        extracted_categories = self._extract_categories(data_categories)

        # ── 4. Build structured brief ─────────────────────────────────────
        brief = {
            "vendor_name": vendor_name,
            "registered_jurisdiction": jurisdiction,
            "service_lines_in_scope": matched_services,
            "data_categories": extracted_categories,
            "has_special_category_data": has_special_category or self._flag_special_category(data_categories),
            "has_cross_border_transfers": has_cross_border or self._flag_cross_border(data_categories),
            "intake_tier": tier.value,
            "intake_trigger": trigger.get("trigger_type", "manual"),
            "initiated_by": initiated_by,
            "vendor_brief_raw": trigger.get("vendor_brief_raw", ""),
            "notes": [],
            "flags": [],
        }

        # ── 5. Validation checks ───────────────────────────────────────────
        if not vendor_name:
            brief["flags"].append("WARNING: vendor_name is empty")
        if not jurisdiction:
            brief["flags"].append("WARNING: registered_jurisdiction is empty")
        if not services:
            brief["flags"].append("WARNING: no service lines provided — using PUBLIC tier")

        return brief

    def _classify_tier(
        self,
        has_special_category: bool,
        has_cross_border: bool,
        data_categories: list[str],
    ) -> "DataTier":  # noqa: F821
        from app.models.domain import DataTier

        text = " ".join(data_categories).lower()
        for kw in SPECIAL_CATEGORY_KEYWORDS:
            if kw.lower() in text and has_special_category:
                return DataTier.RESTRICTED

        if has_special_category or has_cross_border:
            return DataTier.SENSITIVE
        return DataTier.INTERNAL

    def _match_service_lines(self, services: list[str]) -> list[dict]:
        matched = []
        for svc in services:
            svc_lower = svc.lower()
            for line in PROPHARMA_SERVICE_LINES:
                if line.lower() in svc_lower or svc_lower in line.lower():
                    matched.append({"service_line": line, "matched": True})
                    break
            else:
                matched.append({"service_line": svc, "matched": False, "flag": "unrecognised service line"})
        return matched

    def _extract_categories(self, data_categories: list[str]) -> list[str]:
        # Deduplicate and strip
        seen, out = set(), []
        for cat in data_categories:
            cat = cat.strip()
            if cat and cat not in seen:
                seen.add(cat)
                out.append(cat)
        return out

    def _flag_special_category(self, data_categories: list[str]) -> bool:
        text = " ".join(data_categories).lower()
        return any(kw.lower() in text for kw in SPECIAL_CATEGORY_KEYWORDS)

    def _flag_cross_border(self, data_categories: list[str]) -> bool:
        text = " ".join(data_categories).lower()
        return any(kw.lower() in text for kw in CROSS_BORDER_KEYWORDS)
