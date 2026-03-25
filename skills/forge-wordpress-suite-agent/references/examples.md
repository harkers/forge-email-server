# ForgeWordPress Suite Examples

## Good finding
- Cache Forge and SEO Forge both need shared admin primitives, but those belong in `DevForge/shared`, not via direct plugin imports.
- Recommendation: move the shared UI primitive into the foundation and keep plugin logic local.

## Anti-pattern
Do not let one plugin reach into another plugin's internal classes or state directly.
