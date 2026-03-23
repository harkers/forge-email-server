# Privacy Agents

Reusable OpenClaw chat-agent specs for a practical privacy operations triangle.

## Agents

- `Privacy-Publisher.md`
- `Privacy-Incident-Reporter.md`
- `Privacy-Vendor-Assessor.md`
- `shared/privacy-backbone.md`
- `shared/output-schema.md`

## Design principles

- Recommendation-focused, not autonomous decision-makers
- Clear separation between facts, assumptions, missing information, and interpretation
- Human approval required for publication, final legal determinations, or externally shared conclusions
- Consistent structure so outputs can drop into tickets, reviews, and stakeholder updates

## Suggested usage

Use these as system prompts / agent instructions when creating dedicated OpenClaw agents or sessions.

Recommended roles:

1. **Privacy-Incident-Reporter** — reactive incident intake, triage, and analysis
2. **Privacy-Vendor-Assessor** — proactive third-party/privacy due diligence
3. **Privacy-Publisher** — controlled drafting and audience adaptation layer

## Shared backbone

All three agents are designed to use the same:

- organisation terminology library
- jurisdiction rules library
- approved language blocks
- evidence standards
- risk methodology
- escalation rules
- standard output schema

## Next step

If you want, I can also turn these into concrete OpenClaw config entries / runtime templates once you decide how you want to host agents in your setup.
