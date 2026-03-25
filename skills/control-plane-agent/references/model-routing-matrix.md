# Model Routing Matrix

Map agents to models based on task characteristics, complexity, and escalation needs.

## Model tier reference

### Tier 1: Premium reasoning (OAuth-budgeted)
- `openai-codex/gpt-5.4` — complex orchestration, high-stakes decisions, strategic synthesis

### Tier 2: Strong generalist cloud models
- `ollama/glm-5:cloud` — solid generalist, good default
- `ollama/qwen3.5:397b-cloud` — large reasoning, complex analysis
- `ollama/mistral-large-3:675b-cloud` — large model, strong reasoning
- `ollama/qwen3-coder-next:cloud` — coding-focused, complex implementation

### Tier 3: Capable local/cloud hybrid
- `ollama/glm-ocr:bf16` — vision/OCR tasks
- `ollama/kimi-k2.5:cloud` — general reasoning
- `ollama/minimax-m2.5:cloud` / `m2.7:cloud` — general tasks
- `ollama/gemma3:12b` — balanced local
- `ollama/qwen3:14b` — mid-size reasoning

### Tier 4: Efficient specialists
- `ollama/deepseek-r1:14b` — reasoning
- `ollama/phi4-reasoning:14b` — reasoning
- `ollama/deepseek-coder-v2:latest` — coding
- `ollama/codegemma:latest` — coding
- `ollama/qwen2.5-coder:7b` — light coding
- `ollama/devstral-small-2:24b` — coding
- `ollama/starcoder2:15b` — coding
- `ollama/llama3.1:8b` / `llama3.2:latest` — general light tasks
- `ollama/hermes3:8b` — general
- `ollama/granite3-dense:8b` — general

### Tier 5: Embeddings and utility
- `ollama/all-minilm:latest` — embeddings
- `ollama/mxbai-embed-large:latest` — embeddings
- `ollama/nomic-embed-text:latest` — embeddings

### Tier 6: Vision/multimodal
- `ollama/x/llama3.2-vision:latest` — vision
- `ollama/llava:13b` — vision
- `ollama/qwen3-vl:235b-cloud` — large vision

---

## Core orchestration

### control-plane-agent
**Default:** `ollama/gpt-oss:20b`

**Why:** Orchestration requires strong reasoning, verification judgment, and routing decisions. Handoff synthesis and escalation decisions need high reliability. Using a strong local/cloud model keeps cost manageable while maintaining capability.

**Escalation:** When orchestration faces strategic tradeoffs, production sign-offs, or high-stakes decisions → escalate to `openai-codex/gpt-5.4`

**Codex handoff:**
- Strategic tradeoff decisions
- Production deployment sign-off
- Multi-agent orchestration with complex dependencies
- High-stakes escalation decisions

---

### manager-agent
**Default:** `ollama/qwen3.5:397b-cloud` or `ollama/mistral-large-3:675b-cloud`

**Why:** Strong reasoning for classification, routing, and acceptance decisions without premium cost.

**Escalation:**
- When handoff verification is ambiguous after one tightening pass → escalate to `openai-codex/gpt-5.4`
- When multiple valid paths exist and tradeoffs are strategic → escalate to Codex

**Codex handoff:**
- Multi-agent orchestration with complex dependencies
- Strategic tradeoff decisions
- Production deployment sign-off

---

## Core specialists

### planner-agent
**Default:** `ollama/qwen3.5:397b-cloud`

**Why:** Decomposition and sequencing need solid reasoning. Large model helps with dependency analysis.

**Escalation:**
- When plan scope spans multiple projects/roadmaps → escalate to `openai-codex/gpt-5.4`

**Codex handoff:**
- Portfolio-level planning
- Architecture packs with significant risk

---

### coding-worker-agent
**Default:** `ollama/qwen3-coder-next:cloud`

**Why:** Coding-focused model with strong implementation capability.

**Fallbacks:**
- `ollama/deepseek-coder-v2:latest` — strong coding alternative
- `ollama/devstral-small-2:24b` — coding specialist
- `ollama/codegemma:latest` — coding

**Escalation:**
- Complex architectural changes → escalate to `openai-codex/gpt-5.4`
- Security-sensitive code paths → escalate to Codex

**Codex handoff:**
- Security-critical implementations
- Complex integration work
- Architectural refactors

---

### reviewer-agent
**Default:** `ollama/qwen3.5:397b-cloud`

**Why:** Review needs strong reasoning without needing to be a coding specialist.

**Escalation:**
- When review surfaces high-severity architecture or security risk → escalate to Codex

**Codex handoff:**
- Security reviews
- Architecture reviews for production-critical systems

---

### investigator-agent
**Default:** `ollama/deepseek-r1:14b` or `ollama/phi4-reasoning:14b`

**Why:** Reasoning-focused models for diagnosis and root-cause analysis.

**Escalation:**
- When diagnosis remains ambiguous after one pass → escalate to `ollama/qwen3.5:397b-cloud`
- When production incident requires rapid synthesis → escalate to `openai-codex/gpt-5.4`

**Codex handoff:**
- Production incidents
- Complex multi-system failures

---

### documentation-writer-agent
**Default:** `ollama/gemma3:12b` or `ollama/qwen3:14b`

**Why:** Documentation synthesis needs reasonable reasoning. Premium not required for most writing.

**Escalation:**
- When document is external-facing strategic content → escalate to larger model

**Codex handoff:**
- Rarely needed. Only for critical external documents.

---

### architecture-reviewer-agent
**Default:** `ollama/qwen3.5:397b-cloud`

**Why:** Architecture review needs strong reasoning for boundary and coupling analysis.

**Escalation:**
- When review surfaces significant risk → escalate to `openai-codex/gpt-5.4`

**Codex handoff:**
- Production architecture reviews
- Security-boundary reviews

---

### security-reviewer-agent
**Default:** `openai-codex/gpt-5.4`

**Why:** Security review is high-stakes. Premium tier justified.

**Escalation:** Already at premium.

**Codex handoff:** Always on Codex for security reviews.

---

### deployer-agent
**Default:** `ollama/qwen3-coder-next:cloud` or `ollama/glm-5:cloud`

**Why:** Deployment execution and verification. Strong generalist or coding model works.

**Escalation:**
- Production deployments → escalate to `openai-codex/gpt-5.4`

**Codex handoff:**
- Production deployments
- Rollback decisions

---

### researcher-agent
**Default:** `ollama/qwen3:14b` or `ollama/gemma3:12b`

**Why:** Source gathering and synthesis. Mid-tier model sufficient for most research.

**Escalation:**
- Complex multi-source synthesis → escalate to `ollama/qwen3.5:397b-cloud`

**Codex handoff:**
- Strategic research with external stakes

---

### drafting-agent
**Default:** `ollama/gemma3:12b` or `ollama/qwen3:14b`

**Why:** Polished writing from structured findings. Mid-tier sufficient.

**Escalation:**
- External strategic documents → escalate to larger model

**Codex handoff:**
- Rarely needed.

---

## Domain specialists

### privacy-incident-agent
**Default:** `ollama/qwen3.5:397b-cloud`

**Why:** Incident synthesis and risk framing need strong reasoning.

**Escalation:**
- High-impact incidents → escalate to `openai-codex/gpt-5.4`

**Codex handoff:**
- Notifiable incidents
- Regulatory involvement

---

### vendor-assessor-agent
**Default:** `ollama/qwen3.5:397b-cloud`

**Why:** Evidence extraction and risk synthesis need strong reasoning.

**Escalation:**
- Critical vendor assessment → escalate to `openai-codex/gpt-5.4`

**Codex handoff:**
- Critical vendor decisions
- Regulatory-required assessments

---

### forge-pipeline-operator-agent
**Default:** `ollama/glm-5:cloud`

**Why:** State reflection and record updates. Generalist sufficient.

**Escalation:**
- Portfolio-level updates → escalate to larger model

**Codex handoff:**
- Rarely needed.

---

### workspace-governor-agent
**Default:** `ollama/glm-5:cloud`

**Why:** Workspace rule updates. Generalist sufficient.

**Escalation:**
- Major governance changes → escalate to `ollama/qwen3.5:397b-cloud`

**Codex handoff:**
- Rarely needed.

---

### forge-wordpress-suite-agent
**Default:** `ollama/qwen3.5:397b-cloud`

**Why:** Suite governance and boundary analysis need strong reasoning.

**Escalation:**
- Major architectural changes → escalate to `openai-codex/gpt-5.4`

**Codex handoff:**
- Suite-wide architectural decisions

---

### deployment-diagnosis-agent
**Default:** `ollama/deepseek-r1:14b` or `ollama/phi4-reasoning:14b`

**Why:** Diagnosis benefits from reasoning-focused models.

**Escalation:**
- Complex multi-system diagnosis → escalate to `ollama/qwen3.5:397b-cloud`
- Production incident → escalate to `openai-codex/gpt-5.4`

**Codex handoff:**
- Production incidents
- Complex runtime failures

---

### portfolio-planning-agent
**Default:** `ollama/qwen3.5:397b-cloud` or `openai-codex/gpt-5.4`

**Why:** Portfolio strategy needs strong reasoning. Consider premium for significant planning.

**Escalation:**
- Strategic portfolio decisions → always escalate to Codex

**Codex handoff:**
- Roadmap decisions
- Strategic prioritization

---

## Escalation rules summary

### From Tier 3/4 to Tier 2
- Task complexity exceeds model capability
- Verification fails after one tightening pass
- Multiple stakeholders affected
- External document synthesis

### From Tier 2 to Tier 1 (Codex)
- Production deployment decisions
- Security reviews
- High-stakes architectural decisions
- Production incidents
- Regulatory or legal implications
- Strategic tradeoffs with no clear answer

### From any tier to Codex
- When asked to sign off on production changes
- When human escalation is being considered
- When the cost of being wrong is high

---

## Cost/budget guidance

### When to spend Codex budget
- Orchestration decisions (control-plane-agent)
- Security reviews
- Production deployments
- Production incidents
- Strategic planning
- High-stakes architectural decisions

### When to use Tier 2 cloud models
- Most specialist work
- Planning and decomposition
- Coding work (coding-specialist models)
- Reviews and diagnosis
- Domain specialist synthesis

### When to use Tier 3/4 local models
- Documentation writing
- Research gathering
- Drafting
- State updates
- Routine governance
- Low-stakes tasks

### Embeddings (Tier 5)
- Semantic search
- Memory indexing
- Similarity matching

### Vision (Tier 6)
- Image analysis
- OCR tasks
- Multimodal synthesis

---

## Quick routing table

| Role | Default | Escalate to | Codex when |
|------|---------|-------------|------------|
| control-plane-agent | `gpt-oss:20b` | Codex | Strategic decisions, production sign-off |
| manager-agent | `qwen3.5:397b-cloud` | Codex | Multi-agent orchestration, strategic decisions |
| planner-agent | `qwen3.5:397b-cloud` | Codex | Portfolio-level, architecture packs |
| coding-worker-agent | `qwen3-coder-next:cloud` | Codex | Security-critical, architectural refactors |
| reviewer-agent | `qwen3.5:397b-cloud` | Codex | High-severity findings, production reviews |
| investigator-agent | `deepseek-r1:14b` | `qwen3.5` | Production incidents, complex failures |
| documentation-writer-agent | `gemma3:12b` | `qwen3.5` | External strategic docs |
| architecture-reviewer-agent | `qwen3.5:397b-cloud` | Codex | Production architecture, security boundaries |
| security-reviewer-agent | `openai-codex/gpt-5.4` | — | Always |
| deployer-agent | `qwen3-coder-next:cloud` | Codex | Production deployments |
| researcher-agent | `qwen3:14b` | `qwen3.5` | Strategic research |
| drafting-agent | `gemma3:12b` | `qwen3.5` | External strategic docs |
| privacy-incident-agent | `qwen3.5:397b-cloud` | Codex | Notifiable incidents, regulatory |
| vendor-assessor-agent | `qwen3.5:397b-cloud` | Codex | Critical vendor decisions |
| forge-pipeline-operator-agent | `glm-5:cloud` | `qwen3.5` | Portfolio-level updates |
| workspace-governor-agent | `glm-5:cloud` | `qwen3.5` | Major governance changes |
| forge-wordpress-suite-agent | `qwen3.5:397b-cloud` | Codex | Suite-wide architectural decisions |
| deployment-diagnosis-agent | `deepseek-r1:14b` | `qwen3.5` / Codex | Production incidents |
| portfolio-planning-agent | `qwen3.5:397b-cloud` | Codex | Strategic roadmap decisions |

---

## Implementation notes

When implementing routing in OpenClaw:
- Store default model in agent skill metadata
- Escalation can be automatic (based on task markers) or manual (manager decision)
- Codex handoff should require explicit marker or high-stakes trigger
- Budget tracking: count Codex turns separately for cost awareness

For control-plane orchestration:
- Manager can override defaults per dispatch
- Include escalation budget in task packets
- Mark tasks as production/staging/dev to influence model choice