# OQ-04 — Scoring Methodology for the Risk Matrix

**Status:** RESOLVED  
**Resolved:** 2026-03-31  
**Resolution source:** Planning subagent (ollama/qwen3-coder-next:cloud)

---

## Decision

**Model:** Weighted sum scoring — severity score × domain weight per finding, rolled up to a 1–4 risk tier.  
**MVP placeholder:** Equal weights (all domains = 1.0) until the real weight matrix is validated with real ProPharma assessments.  
**Config format:** YAML — single file, hot-reloadable without redeploy.

---

## 1. Severity Scale

| Level | Score | Definition (Vendor Assessment Context) |
|-------|-------|---------------------------------------|
| **Critical** | 4 | Hard block. Violation of core legal obligation or mandatory requirement. Engagement is legally or financially untenable without remediation. *Examples:* No lawful basis for processing; no DPA in place; unresolved critical GxP gap affecting product safety. |
| **High** | 3 | Blocking remediation required. Material violation that must be resolved before engagement. Risk of regulatory action or material financial loss if unaddressed. *Examples:* Missing clinical data audit trail; unmitigated cross-border transfer risk; expired ISO 27001 for a vendor handling PHI. |
| **Medium** | 2 | Negotiable remediation. Significant gap that should be addressed but not an automatic dealbreaker. Resolvable via contractual amendment or action plan. *Examples:* Audit rights limited to annual reviews; breach notification SLA exceeds 48h; SOC 2 Type I only (Type II unavailable). |
| **Low** | 1 | Minor deviation. Small gap acceptable with minimal risk or addressed post-engagement. *Examples:* DPA liability cap 10% below standard; audit notice period 30 days vs 14; minor documentation inconsistency. |
| **Informational** | 0 | No risk. Observation without deficiency. Positive confirmations, context items. |

---

## 2. Domain Weights by Service Line

Derived directly from the ProPharma service line matrix in the project brief:
- `●●` (Elevated scrutiny) → **1.5**
- `●` (Standard scrutiny) → **1.0**
- `○` (Reduced scrutiny) → **0.5**

| Service Line | Data Protection | Regulatory | InfoSec | Contractual | AI Governance |
|-------------|:---:|:---:|:---:|:---:|:---:|
| Regulatory Affairs | 1.0 | 1.5 | 1.0 | 1.0 | 0.5 |
| Pharmacovigilance | 1.5 | 1.5 | 1.5 | 1.5 | 1.0 |
| Quality Assurance | 1.0 | 1.5 | 1.0 | 1.0 | 0.5 |
| Clinical Operations | 1.5 | 1.5 | 1.5 | 1.5 | 1.0 |
| Data Annotation and AI | 1.5 | 1.0 | 1.0 | 1.0 | 1.5 |
| Medical Writing | 1.0 | 1.0 | 0.5 | 1.0 | 1.0 |
| Biostatistics | 1.0 | 1.5 | 1.0 | 1.0 | 1.0 |
| IT and Data Management | 1.0 | 1.0 | 1.5 | 1.5 | 1.0 |

---

## 3. Finding Score Calculation

```
finding_score = severity_score × domain_weight_for_service_line
```

**Example — Clinical Operations, missing audit trail:**
- Severity: Critical = 4
- Domain: Regulatory (Clinical Ops has 1.5 weight)
- **Finding score = 4 × 1.5 = 6.0**

---

## 4. Risk Tier Roll-Up

1. Sum all finding scores
2. Apply tier thresholds

| Risk Tier | Total Score Threshold | Decision |
|-----------|----------------------|----------|
| **Tier 1** | < 2.0 | Approve — minimal risk, standard due diligence |
| **Tier 2** | 2.0 – 5.9 | Approve with conditions — negotiate remediation |
| **Tier 3** | 6.0 – 11.9 | Approve with oversight — DPO sign-off + action plan |
| **Tier 4** | ≥ 12.0 | Reject — unacceptably high risk, do not engage |

### Edge Rules

- **Any Critical finding** → minimum Tier 2 (Critical finding alone scores ≥ 4.0)
- **Two or more High-severity findings** → minimum Tier 3 regardless of total score
- **RESTRICTED data category involved** → hard block Tier 4; CloakLLM must hard-block from cloud routing

---

## 5. Config File

**`config/scoring_weights.yaml`** (MVP placeholder — equal weights):

```yaml
severity_scores:
  critical: 4
  high: 3
  medium: 2
  low: 1
  informational: 0

# MVP: equal weights; replace with service-line matrix post-validation
domain_weights:
  data_protection: 1.0
  regulatory: 1.0
  infosec: 1.0
  contractual: 1.0
  ai_governance: 1.0

# Populated from OQ-04 resolved matrix; used when validated
service_line_weights:
  pharmacovigilance:
    data_protection: 1.5
    regulatory: 1.5
    infosec: 1.5
    contractual: 1.5
    ai_governance: 1.0
  clinical_operations:
    data_protection: 1.5
    regulatory: 1.5
    infosec: 1.5
    contractual: 1.5
    ai_governance: 1.0
  # ... all 8 service lines
```

---

## 6. Python Implementation

**`src/scoring/engine.py`**:

```python
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class Finding:
    severity: str          # critical, high, medium, low, informational
    domain: str           # data_protection, regulatory, infosec, contractual, ai_governance
    description: str
    domain_weight_override: Optional[float] = None  # for MVP placeholder

@dataclass
class ScoringResult:
    tier: int             # 1-4
    total_score: float
    domain_scores: dict[str, float]
    edge_rules_triggered: list[str]
    decision: str         # approve / approve_with_conditions / approve_with_oversight / reject

def load_weights(config_path: str = "config/scoring_weights.yaml") -> dict:
    with open(Path(__file__).parent / f"../../{config_path}") as f:
        return yaml.safe_load(f)

def calculate_finding_score(
    finding: Finding,
    service_line: str,
    weights: dict
) -> float:
    sev_score = weights['severity_scores'][finding.severity.lower()]
    if finding.domain_weight_override is not None:
        domain_weight = finding.domain_weight_override
    elif service_line.lower() in weights.get('service_line_weights', {}):
        domain_weight = (
            weights['service_line_weights'][service_line.lower()]
            .get(finding.domain.lower(), 1.0)
        )
    else:
        domain_weight = weights['domain_weights'].get(finding.domain.lower(), 1.0)
    return sev_score * domain_weight

def calculate_risk_tier(
    findings: list[Finding],
    service_line: str,
    has_restricted_data: bool = False,
    config_path: str = "config/scoring_weights.yaml"
) -> ScoringResult:
    weights = load_weights(config_path)
    total_score = 0.0
    domain_scores: dict[str, float] = {}
    edge_rules_triggered = []

    for f in findings:
        score = calculate_finding_score(f, service_line, weights)
        total_score += score
        domain_scores[f.domain] = domain_scores.get(f.domain, 0.0) + score

    # Edge rules
    has_critical = any(f.severity.lower() == 'critical' for f in findings)
    high_count = sum(1 for f in findings if f.severity.lower() == 'high')

    if has_restricted_data:
        tier, decision = 4, "reject"
        edge_rules_triggered.append("RESTRICTED_data_block")
    elif has_critical and high_count >= 2:
        tier, decision = 4, "reject"
        edge_rules_triggered.append("critical_plus_multiple_high")
    elif has_critical:
        tier = max(2, min(4, int(total_score // 4) + 1))
        decision = {2: "approve_with_conditions", 3: "approve_with_oversight"}.get(tier, "reject")
        edge_rules_triggered.append("critical_present")
    elif high_count >= 2:
        tier, decision = 3, "approve_with_oversight"
        edge_rules_triggered.append("multiple_high")
    elif total_score >= 12.0:
        tier, decision = 4, "reject"
    elif total_score >= 6.0:
        tier, decision = 3, "approve_with_oversight"
    elif total_score >= 2.0:
        tier, decision = 2, "approve_with_conditions"
    else:
        tier, decision = 1, "approve"

    return ScoringResult(
        tier=tier,
        total_score=round(total_score, 2),
        domain_scores={k: round(v, 2) for k, v in domain_scores.items()},
        edge_rules_triggered=edge_rules_triggered,
        decision=decision
    )
```

---

## 7. Validation

Before OQ-04 is treated as fully resolved, the scoring model must be validated against:
- Minimum 3 historical vendor assessments with known outcomes
- Output must match manual expert classification in at least 2/3 cases; divergences documented and explained
- If divergence > 1 tier on any test case, weight matrix must be adjusted and re-tested

---

## Blocked Work

| Work Item | Status |
|-----------|--------|
| Scoring Agent (Step 5) implementation | ✅ Unblocked — implement against this spec |
| Remediation Agent (Step 6) | ✅ Unblocked — depends on scoring output |
| Report Synthesis Agent (Step 7) | ✅ Unblocked |
| Weight matrix validation | ⏳ Blocked — needs 3 historical ProPharma assessments |

---

## Risks

| Risk | Mitigation |
|------|-----------|
| MVP equal weights produce incorrect tiers | Document as placeholder; validate against real assessments before production |
| Domain weight matrix not calibrated | Run retrospective on 3 test assessments; tune weights if >1 tier off |
