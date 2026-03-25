# Architecture Reviewer Examples

## Good finding
- Plugin B depends directly on Plugin A internals instead of using a shared contract.
- This violates the boundary model and increases coupled release risk.
- Recommendation: move the shared contract into the common foundation or expose a namespaced hook/API boundary.

## Review focus
- ownership
- coupling
- contract clarity
- deployment or release implications
