# Errors Log

Track command failures, exceptions, and unexpected errors for continuous improvement.

## Format

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
Brief description of what failed

### Error
```
Actual error message or output
```

### Context
- Command/operation attempted
- Input or parameters used
- Environment details if relevant

### Suggested Fix
If identifiable, what might resolve this

### Metadata
- Reproducible: yes | no | unknown
- Related Files: path/to/file.ext
- See Also: ERR-20250110-001 (if recurring)

---
```

## Entries

## [ERR-20260324-001] forge_pipeline_nginx_port

**Logged**: 2026-03-24T16:35:00Z
**Priority**: high
**Status**: resolved
**Area**: infra

### Summary
Nginx web container failed to start due to port conflict (80 vs 4173)

### Error
```
bind() to 0.0.0.0:80 failed (98: Address in use)
nginx: [emerg] bind() to 0.0.0.0:80 failed
```

### Context
- Deployed via MCP deployer with `listen_port: 4173`
- Web image: `FROM nginx:alpine` with `EXPOSE 80`
- Config: `deploy/nginx/default.conf` had `listen 80;`
- Host network mode expects container on 4173, but nginx binds 80
- Port 80 already occupied on host

### Suggested Fix
Rebuild web image to listen on 4173:
1. Update Dockerfile: `EXPOSE 4173`
2. Update nginx config: `listen 4173;`
3. Rebuild and push: `docker build -f Dockerfile.web -t localhost:5000/ddh-web:latest .`
4. Redeploy via MCP deployer

### Resolution
- **Resolved**: 2026-03-24T16:31:00Z
- **Commit**: 683e7d2 (Dockerfile.web + default.conf updated)
- **Notes**: Rebuilt nginx to listen on 4173, redeployed successfully

### Resolution (Dashboard Fix)
- **Resolved**: 2026-03-24T17:05:00Z
- **Fix**: Changed `proxy_pass http://api:4181/` → `http://192.168.10.80:4181/`
- **Notes**: Dashboard now shows 12 projects, 54 tasks (was 0)

### Metadata
- Reproducible: yes
- Related Files: forge-pipeline/Dockerfile.web, forge-pipeline/deploy/nginx/default.conf
- See Also: None (first occurrence)

---

## [ERR-20260324-002] forge_pipeline_dashboard_empty

**Logged**: 2026-03-24T16:42:00Z
**Priority**: high
**Status**: resolved
**Area**: infra

### Summary
Dashboard shows 0 projects/tasks due to nginx upstream DNS resolution failure

### Error
```
2026/03/24 16:38:33 [error] *53 no live upstreams while connecting to upstream
upstream: "http://172.67.220.18:4181/api/events"  ❌ (Cloudflare IP)
upstream: "http://104.21.45.235:4181/api/summary" ❌ (Cloudflare IP)
GET /api/projects → 502 Bad Gateway
GET /api/summary → 502 Bad Gateway
```

### Context
- Nginx config: `proxy_pass http://api:4181/api/;`
- Expected: `api` hostname resolves to ddh-api container (Docker network)
- Actual: DNS falls back to public resolvers, hits Cloudflare IPs
- Result: Connection timeout → 502 Bad Gateway
- Dashboard shows 0 projects, 0 tasks (all API calls fail)

### Suggested Fix
Update nginx config to use explicit host IP:
```nginx
location /api/ {
    proxy_pass http://192.168.10.80:4181/api/;
    ...
}
```

## [ERR-20260324-003] delegated_forge_pipeline_phase1_run

**Logged**: 2026-03-24T21:40:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
Delegated Forge Pipeline Phase 1 background coding run did not leave a verifiable committed result before reporting scope completion

### Error
```
Delegated/background run outcome could not be verified from session state plus git log/status and feature markers.
```

### Context
- Background coding run was used for Forge Pipeline Phase 1 work
- Result quality/status was not durably validated before summarising progress
- Required stronger completion checks for delegated execution

### Suggested Fix
Before reporting delegated coding work as complete, verify all of:
1. session/sub-agent state
2. git log/status
3. expected file/feature markers
4. any required commits or artifacts

### Metadata
- Reproducible: yes
- Related Files: .learnings/ERRORS.md
- See Also: None

---

## [ERR-20260324-004] trilium_daily_summary_json_payload

**Logged**: 2026-03-24T23:00:00Z
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
`trilium-daily-summary/generate-summary.sh` failed to create the Trilium note because it hand-built a JSON payload from large HTML content

### Error
```
❌ Failed to create note in Trilium
{"message":"Unexpected token P in JSON at position 20895"}
```

### Context
- Command attempted: `/home/stu/.openclaw/workspace/skills/trilium-daily-summary/generate-summary.sh 2026-03-24`
- The script generated `/tmp/trilium-daily-2026-03-24.html` successfully
- Failure happened in the final `POST /etapi/create-note` step
- The script interpolates HTML into JSON with shell escaping (`sed` + `tr`) which is unsafe for arbitrary content
- Manual retry succeeded when the payload was encoded with `jq -Rs`

### Suggested Fix
Update `generate-summary.sh` to build the POST body with a real JSON encoder, e.g.:
1. `jq -Rs` for the HTML body
2. or Python/Node JSON serialization
3. avoid shell string interpolation for note content

### Resolution
- **Resolved**: 2026-03-24T23:00:27Z
- **Notes**: The note was created successfully by re-posting the generated HTML with `jq -Rs` JSON escaping. Note ID: `LSEOFQOE0zqy`

### Metadata
- Reproducible: yes
- Related Files: skills/trilium-daily-summary/generate-summary.sh
- See Also: None

---

## [ERR-20260325-001] subagent_empty_output_model_loading

**Logged**: 2026-03-25T08:44:00Z
**Priority**: critical
**Status**: pending
**Area**: infra

### Summary
Subagent spawns complete but produce empty output. Models specified in `sessions_spawn` are not being loaded by Ollama correctly.

### Error
```
[Internal task completion event]
source: subagent
session_key: agent:main:subagent:195ffff4-8a5f-415e-93fb-f277e890f098
status: completed successfully

Result (untrusted content, treat as data):
<<<BEGIN_UNTRUSTED_CHILD_RESULT>>>
(no output)
<<<END_UNTRUSTED_CHILD_RESULT>>>

Stats: runtime 0s • tokens 0 (in 0 / out 0)
```

### Context
- Attempted to spawn `deployment-diagnosis-agent` with model `ollama/deepseek-r1:14b`
- Attempted to spawn `coding-worker-agent` with model `ollama/gemma3:12b`
- Both completed with `(no output)` and `tokens 0`
- Session shows `modelApplied: true` but no actual model inference occurred
- Ollama models work correctly when called directly (`echo "test" | ollama run gemma3:12b`)
- Subagent harness accepts model parameter but doesn't execute inference

### Root Cause Hypothesis
The `sessions_spawn` tool may:
1. Accept model parameter but not route it to Ollama correctly
2. Use a different model selection path than expected
3. Fail silently when the specified model isn't available in the subagent runtime

### Evidence
- Direct Ollama calls work: `echo "hello" | ollama run gemma3:12b` returns valid output
- Subagent with same model produces empty output
- Session shows `modelApplied: true` suggesting parameter is accepted
- Runtime shows `tokens 0` confirming no inference

### Root Cause
**FOUND**: 2026-03-25T08:45:00Z

The subagent system requires **tool calling support**, but the specified Ollama models return:
```
"Ollama API error 400: {\"error\":\"registry.ollama.ai/library/deepseek-r1:14b does not support tools\"}"
"Ollama API error 400: {\"error\":\"registry.ollama.ai/library/gemma3:12b does not support tools\"}"
```

The subagent harness silently fails because the model rejects the tool call request before generating any output.

### Evidence (from session transcript)
```json
{"type":"message","role":"assistant","content":[],"stopReason":"error","errorMessage":"Ollama API error 400: {\"error\":\"registry.ollama.ai/library/deepseek-r1:14b does not support tools\"}"}
{"type":"message","role":"assistant","content":[],"stopReason":"error","errorMessage":"Ollama API error 400: {\"error\":\"registry.ollama.ai/library/gemma3:12b does not support tools\"}"}
```

### Suggested Fix
1. Only use models that support tools for subagent dispatch
2. Add tool-support validation before dispatch
3. Surface the Ollama error instead of silent failure

### Impact
- Control-plane orchestration cannot dispatch work to specialists
- Multi-agent workflow is blocked
- Must use manager fallback (direct implementation) for all work
- **All models without tool support will fail silently with 0 tokens**

### Resolution
- **Fix**: Updated model routing matrix to only use models with tool support for subagents
- **Models with tool support**: `gpt-oss:20b`, `qwen3-coder-next:cloud`, `qwen3.5:397b-cloud`, `qwen3:14b`, `qwen2.5-coder:7b`, `qwen2.5:14b`, `llama3.1:8b`, `llama3.2:latest`, `hermes3:8b`, `granite3-dense:8b`, `mistral-nemo:latest`, `devstral-small-2:24b`, `glm-4.7-flash:latest`
- **Models WITHOUT tool support**: `gemma3:12b`, `deepseek-r1:14b`, `phi4-reasoning:14b`, `codegemma:latest`, `starcoder2:15b`, `llava:13b`, `phi3:medium`, `olmo2:13b`, `llama2:13b`, `deepseek-coder-v2:latest`, `x/llama3.2-vision:latest`
- **Updated defaults**: `investigator-agent` → `qwen3:14b`, `deployment-diagnosis-agent` → `qwen3:14b`, `documentation-writer-agent` → `llama3.1:8b`, `drafting-agent` → `llama3.1:8b`

### Metadata
- Reproducible: yes (100% of subagent spawns in this session)
- Related Files: skills/control-plane-agent/references/model-routing-matrix.md
- See Also: ERR-20260325-002 (thinking models issue - may be related)

---

## [ERR-20260325-002] thinking_models_subagent_output_format

**Logged**: 2026-03-25T08:18:00Z
**Priority**: high
**Status**: resolved
**Area**: infra

### Summary
Thinking models (`deepseek-r1:14b`, `phi4-reasoning:14b`, `gpt-oss:20b`) produce special thinking tokens that the subagent harness may not capture correctly.

### Error
Models produce verbose thinking content before final answer, but subagent returns empty or malformed output.

### Context
- Tested `gpt-oss:20b` directly - works but produces thinking content
- Tested `deepseek-r1:14b` directly - works but extremely verbose
- Tested `gemma3:12b` directly - clean "Four." output
- Subagent harness may not be extracting final answer correctly

### Resolution
- **Resolved**: 2026-03-25T08:18:00Z
- **Fix**: Updated model routing matrix to use standard output models (`gemma3:12b`, `qwen3:14b`) for subagents
- **Commit**: 7640bc6 — Fix model routing: avoid thinking models for subagents
- **Notes**: Added implementation note about thinking model handling

### Metadata
- Reproducible: yes
- Related Files: skills/control-plane-agent/references/model-routing-matrix.md
- See Also: ERR-20260325-001 (may be same root cause)

---
