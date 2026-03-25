# Model Assignments for Pipeline Tasks

## Task Type to Model Mapping

### Infrastructure / DevOps
| Task Type | Default Model | Escalate To |
|-----------|---------------|-------------|
| deployment-diagnosis | qwen3:14b | qwen3.5:397b-cloud |
| deployment-execution | qwen3-coder-next:cloud | Codex |
| infrastructure-setup | qwen3-coder-next:cloud | Codex |
| monitoring-setup | qwen3:14b | qwen3.5:397b-cloud |

### Coding / Development
| Task Type | Default Model | Escalate To |
|-----------|---------------|-------------|
| feature-implementation | qwen3-coder-next:cloud | Codex |
| bug-fix | qwen3:14b | qwen3-coder-next:cloud |
| refactoring | qwen3-coder-next:cloud | Codex |
| test-writing | qwen3:14b | qwen3.5:397b-cloud |

### Review / Analysis
| Task Type | Default Model | Escalate To |
|-----------|---------------|-------------|
| code-review | qwen3.5:397b-cloud | Codex |
| security-review | Codex | — |
| architecture-review | qwen3.5:397b-cloud | Codex |
| performance-analysis | qwen3:14b | qwen3.5:397b-cloud |

### Documentation / Writing
| Task Type | Default Model | Escalate To |
|-----------|---------------|-------------|
| docs-writing | llama3.1:8b | qwen3:14b |
| spec-creation | qwen3:14b | qwen3.5:397b-cloud |
| changelog | llama3.1:8b | qwen3:14b |
| readme-update | llama3.1:8b | qwen3:14b |

### Planning / Strategy
| Task Type | Default Model | Escalate To |
|-----------|---------------|-------------|
| roadmap-planning | qwen3.5:397b-cloud | Codex |
| task-breakdown | qwen3:14b | qwen3.5:397b-cloud |
| priority-evaluation | gpt-oss:20b | Codex |
| portfolio-review | qwen3.5:397b-cloud | Codex |

### Investigation / Research
| Task Type | Default Model | Escalate To |
|-----------|---------------|-------------|
| bug-investigation | qwen3:14b | qwen3.5:397b-cloud |
| research | qwen3:14b | qwen3.5:397b-cloud |
| dependency-analysis | qwen3:14b | qwen3.5:397b-cloud |

## Token Budget Estimates

| Task Complexity | Estimated Tokens |
|-----------------|------------------|
| Simple (docs, small fix) | 10-50k in / 2-10k out |
| Medium (feature, review) | 50-200k in / 10-50k out |
| Complex (refactor, architecture) | 200-500k in / 50-100k out |
| Critical (security, production) | Reserve 500k+ |

## Model Capability Notes

### Strong Coding Models
- `qwen3-coder-next:cloud` — best for implementation
- `qwen2.5-coder:7b` — efficient for small tasks
- `devstral-small-2:24b` — coding specialist

### Strong Reasoning Models
- `gpt-oss:20b` — control-plane decisions
- `qwen3.5:397b-cloud` — complex analysis
- `qwen3:14b` — balanced reasoning

### Efficient Models
- `llama3.1:8b` — documentation, simple tasks
- `qwen2.5-coder:7b` — quick fixes
- `llama3.2:3b` — trivial tasks

### Premium (Reserve for Critical)
- `openai-codex/gpt-5.4` — security, production, strategic