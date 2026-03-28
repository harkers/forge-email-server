# DevForge: Project Foundry
## CODEOWNERS Draft

Status: Planning draft  
Date: 2026-03-28

## Purpose

Draft the ownership shape for the future repository before named humans are assigned.

## Draft Ownership Model

```text
# Global fallback
* @product-owner @governance-lead

# Core planning docs
/docs/ @product-owner @governance-lead
/templates/ @governance-lead @documentation-lead
/schemas/ @architecture-lead @governance-lead
/directives/ @governance-lead @workspace-governor
/agents/ @product-owner @governance-lead
/automation/ @delivery-ops-lead @architecture-lead

# Workspace domains
/workspaces/forge-flash-design/ @product-owner
/workspaces/forge-architecture/ @architecture-lead
/workspaces/forge-governance/ @governance-lead
/workspaces/forge-risk/ @risk-lead @privacy-lead
/workspaces/forge-document-engine/ @documentation-lead @governance-lead
/workspaces/forge-orchestrate/ @delivery-ops-lead
/workspaces/forge-pipeline/ @pipeline-lead
/workspaces/forge-whats-next/ @pipeline-lead
/workspaces/forge-control-plane/ @delivery-ops-lead
/workspaces/forge-review/ @quality-lead @security-lead @privacy-lead
/workspaces/forge-release/ @release-lead
/workspaces/forge-deploy/ @release-lead @ops-lead
/workspaces/forge-validate/ @ops-lead
/workspaces/forge-comms/ @comms-lead
/workspaces/forge-training/ @enablement-lead
/workspaces/forge-close/ @governance-lead @product-owner
/workspaces/forge-fix/ @delivery-ops-lead @pipeline-lead
```

## Note

This is a structural draft only. Real GitHub usernames should not be assigned until the named owners exist.
