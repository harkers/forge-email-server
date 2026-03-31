# OQ-06 — spaCy NER Model Tier for CloakLLM

**Status:** RESOLVED  
**Resolved:** 2026-03-31  
**Resolution source:** Planning subagent (ollama/qwen3-coder-next:cloud)

---

## Decision

**MVP:** `en_core_web_sm` (small) — CPU-safe, fast, ~12MB, lower accuracy but acceptable for non-clinical SENSITIVE data.  
**Production target:** `en_core_web_trf` (transformer) — state-of-the-art NER, GPU required, ~500MB+.  
**Upgrade trigger:** CloakLLM validation test set (see below) shows materially better recall on clinical entities that `sm` misses.

A separate risk item is raised for the GPU/container runtime question — it must be resolved before `trf` can be deployed.

---

## Rationale

| Factor | `en_core_web_sm` | `en_core_web_trf` |
|--------|-----------------|-------------------|
| Size | ~12MB | ~500MB+ |
| Speed | Fast (CPU) | Slow on CPU; needs GPU for production speed |
| NER accuracy | Moderate | State-of-the art |
| GPU required | No | Yes (for acceptable latency) |
| Titan VRAM | Free | ~500MB+ (within headroom if SD stopped) |
| Titan container GPU passthrough | Not configured | Requires `nvidia-container-toolkit` setup |
| Clinical data recall | Baseline | Materially better on hard entities |
| MVP readiness | ✅ Ready now | ⏳ Blocked by GPU question |

The `sm` model handles standard entities (PERSON, ORG, GPE, DATE, MONEY) well. Gaps appear on domain-specific clinical entities. For MVP, `sm` is acceptable with the validation gate below.

---

## GPU / Container Runtime Risk Item

**Risk:** CloakLLM `trf` upgrade blocked because Titan Docker Compose stack uses host network mode and does not have `nvidia-container-toolkit` configured for GPU passthrough to containers.

**Current Titan GPU usage:**
- Stable Diffusion XL: ~7.1GB VRAM
- llama.cpp Phi-4-mini: ~2.4GB (VRAM)
- llama.cpp Coder-7B: ~4.4GB (VRAM)
- **Headroom:** ~1.1GB (tight)

**Options:**
1. **Stop SD when running CloakLLM `trf`** — reclaim ~7.1GB VRAM; feasible for batch pipeline runs
2. **Configure `nvidia-container-toolkit`** — allow Docker containers to access GPU; requires host package install + Docker daemon config
3. **Run `trf` on CPU** — viable for low-volume MVP; latency ~10–30s per document vs <1s on GPU

**Recommended:** Option 1 (stop SD during pipeline runs) as MVP path. Option 2 as Phase 2 hardening. Option 3 as fallback.

**Action owner:** Titan platform — must be resolved before `trf` deployment.

---

## Validation Test Set

Before OQ-06 is marked fully resolved (i.e., before accepting `trf` as production-default), run both models against a minimum 50-sentence test set and compare entity-level precision and recall.

### Test Set Composition

| Category | Sentences | Examples |
|----------|-----------|---------|
| Standard PII (names, emails, phones) | 10 | "Dr. Sarah Mitchell submitted the report on behalf of the organisation." |
| Organisation and location | 10 | "The CRO headquartered in Manchester processed the data under a CSA with Roche." |
| Dates and temporal references | 5 | "Patient follow-up scheduled for 14 days post-administration, per protocol PV-2024-007." |
| Adverse event descriptions | 10 | "Subject experienced Grade 3 neutropenia on Day 14; SAE reported to EMA within 24 hours." |
| Drug and compound names | 5 | "Concomitant remdesivir administered alongside study drug from Day 1 to Day 10." |
| Clinical measurements | 5 | "eGFR decline to 42 mL/min/1.73m² on Visit 3; dosing withheld pending renal consult." |
| Mixed PHI + clinical text | 5 | "Report dated 2026-01-15 from Dr. James O'Brien, PV Lead at [ORG], concerning patient ID: 123456789." |

### Validation Protocol

1. Run both models against all 50 sentences
2. Compute per-entity-type precision, recall, F1
3. Flag entities where `trf` recall > `sm` recall by ≥ 10 percentage points
4. If such entities exist in the clinical categories (adverse events, clinical measurements, drug names), `trf` is the production default
5. If `sm` performs acceptably (F1 > 0.85 on all categories), `sm` remains the default

### Minimum Passing Criteria (to mark OQ-06 resolved)

- [ ] Both models run on the 50-sentence test set without errors
- [ ] `sm` F1 ≥ 0.80 on standard PII and organisation/location categories
- [ ] Any clinical category where `sm` F1 < 0.70 is documented and escalated
- [ ] Decision on `trf` vs `sm` documented with test set results
- [ ] GPU/container runtime question is either resolved or a mitigation is in place

---

## Blocked Work

| Work Item | Status |
|-----------|--------|
| CloakLLM core redaction logic | ✅ Unblocked — implement with `sm` |
| CloakLLM `trf` upgrade | ⏳ Blocked — GPU/container runtime question |
| CloakLLM validation testing | ✅ Unblocked — can build test set now |
| CloakLLM production sign-off | ⏳ Blocked — validation results |

---

## Risks

| Risk | Mitigation |
|------|-----------|
| `sm` misses clinical entity types (drug names, AE descriptions) | Validation test set must catch this; `trf` upgrade if F1 < 0.70 on clinical categories |
| `trf` upgrade hits VRAM limit with SD running | Stop SD during pipeline batch runs; schedule CloakLLM runs outside SD usage hours |
| `trf` CPU inference too slow for pipeline throughput | Target GPU passthrough for Phase 2; CPU fallback for MVP with latency budget |
| RESTRICTED data misclassified as SENSITIVE | Default to RESTRICTED for any ambiguous special-category indicator; `sm` is irrelevant to this risk |
