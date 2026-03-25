# ForgeWordPress Orchestration Plan

*Captured: 2026-03-24*

## Platform Model

ForgeWordPress should be built as a modular WordPress suite made up of four plugins and one shared internal library.

### Plugins + 1 Shared Library

| Plugin | Slug | Purpose |
|--------|------|---------|
| SEO Forge | `seo-forge` | Meta tags, Open Graph, Twitter Cards, JSON-LD schema, XML sitemap at /sitemap.xml |
| Image Forge | `image-forge` | Upload-time optimisation, WebP conversion, lazy loading, bulk-optimise REST endpoint |
| Form Forge | `form-forge` | Gutenberg block, form CPT, submissions CPT, email notifications, honeypot spam protection |
| Cache Forge | `cache-forge` | File-based page cache, browser cache headers, HTML minifier, one-click purge |
| **DevForge/shared** | — | PHP abstracts + traits, React components, useSettings hook, REST API utilities |

## Operating Model

- Each plugin owns its own domain logic
- `DevForge/shared` owns the reusable infrastructure and UI primitives
- Plugins communicate through contracts, hooks, and shared conventions
- No plugin should directly depend on another plugin's internals

## Architectural Layers

1. **WordPress integration layer** — hooks, filters, REST routes, admin menus, CPT/block registration
2. **Domain layer** — plugin-specific business logic (SEO, image, forms, cache)
3. **Shared platform layer** — `DevForge/shared` abstracts, settings framework, REST helpers
4. **Cross-plugin contract layer** — namespaced hooks, shared option patterns, response schemas
5. **Delivery/release layer** — packaging, CI/CD, semver, compatibility testing

## Repository Strategy

**Recommended: Monorepo**

```
forge-wordpress/
  plugins/
    seo-forge/
    image-forge/
    form-forge/
    cache-forge/
  packages/
    shared/
  docs/
  tools/
  .github/
```

## Shared Foundation: DevForge/shared

### PHP Layer

Namespace: `DevForge\Shared\`

Contents:
- `AbstractPlugin`
- `PluginServiceProvider`
- `SettingsRegistrar`
- `AdminPageRegistrar`
- `RestController`
- `ResponseFactory`
- `CapabilityManager`
- `AssetLoader`
- `OptionRepository`
- `NonceVerifier`
- `LoggerInterface`
- Traits for bootstrapping, settings wiring, REST permissions, asset versioning

### React / Admin UI Layer

Base components:
- `SettingsPanel`
- `ToggleField`
- `TextField`
- `SaveButton`

Recommended additions:
- `SectionHeader`
- `SelectField`
- `NumberField`
- `NoticeBanner`
- `StatusBadge`
- `DangerZone`
- `EmptyState`
- `InlineLoader`
- `ConfirmDialog`

Hooks/utilities:
- `useSettings`
- `useRestRequest`
- `useDirtyState`
- `useNotice`
- REST request helpers
- Nonce attachment helpers

### What Must NOT Go in DevForge/shared

- SEO rule engines
- Form validation engines
- Image conversion logic
- Cache invalidation rules

Shared is infrastructure only — no domain logic.

## Plugin Boundaries

### SEO Forge

**Responsibilities:**
- Meta titles and descriptions
- Open Graph tags
- Twitter Cards
- Canonical tags
- Robots directives
- JSON-LD schema
- XML sitemap generation
- Optional page/post SEO overrides

**Internal modules:**
- `MetadataResolver`
- `SchemaBuilder`
- `SitemapGenerator`
- `RobotsManager`
- `FrontendTagRenderer`
- `AdminSettingsController`
- `PostMetaController`

### Image Forge

**Responsibilities:**
- Upload-time optimisation
- WebP generation
- Lazy loading behaviour
- Bulk optimisation endpoint
- Media-level optimisation metadata

**Internal modules:**
- `UploadOptimizer`
- `WebPConverter`
- `LazyLoadManager`
- `BulkOptimiseController`
- `MediaSettingsController`
- `ImageJobQueue`

### Form Forge

**Responsibilities:**
- Gutenberg form block
- Form CPT
- Submissions CPT
- Form rendering
- Submission validation
- Email notifications
- Honeypot spam protection
- Submissions review in admin

**Internal modules:**
- `FormPostType`
- `SubmissionPostType`
- `FormRenderer`
- `SubmissionProcessor`
- `NotificationService`
- `SpamProtectionService`
- `BlockRegistration`

### Cache Forge

**Responsibilities:**
- File-based page cache
- Browser cache headers
- HTML minifier
- Purge controls
- Invalidation on content changes
- Diagnostics and cache controls

**Internal modules:**
- `CacheStore`
- `CacheKeyResolver`
- `PageCacheMiddleware`
- `PurgeController`
- `HeaderManager`
- `HtmlMinifier`
- `InvalidationManager`

## Cross-Plugin Orchestration Rules

### Rule 1 — No Direct Internal Coupling

Bad:
```php
SEOForge\SitemapGenerator::regenerate();
```

Good:
```php
do_action('forge/seo/sitemap_regenerated', $payload);
```

### Rule 2 — Shared Event Naming

Use namespaced hooks:
- `forge/plugin_loaded`
- `forge/settings_updated`
- `forge/content_changed`
- `forge/cache/purge_requested`
- `forge/form/submission_created`
- `forge/image/optimised`
- `forge/seo/sitemap_regenerated`

### Rule 3 — Shared Settings Naming

Option keys:
- `forge_seo_settings`
- `forge_image_settings`
- `forge_form_settings`
- `forge_cache_settings`

Metadata:
- `forge_suite_version`
- `forge_plugin_registry`
- `forge_install_id`

### Rule 4 — Shared Capability Model

- `manage_forge_suite`
- `manage_forge_seo`
- `manage_forge_images`
- `manage_forge_forms`
- `manage_forge_cache`
- `view_forge_submissions`

### Rule 5 — Shared Response Format

Success:
```json
{
  "success": true,
  "data": {},
  "message": "Settings saved."
}
```

Error:
```json
{
  "success": false,
  "error": {
    "code": "invalid_setting",
    "message": "The provided setting is invalid."
  }
}
```

## Admin Experience

### Menu Structure

```
ForgeWordPress
  Overview
  SEO Forge
  Image Forge
  Form Forge
  Cache Forge
```

### Overview Page (Suite Control Plane)

- Installed plugin modules
- Active/inactive state
- Version numbers
- Health status
- Quick actions
- Environment checks
- Shared documentation links
- Compatibility warnings

### Plugin Settings Pages

Consistent structure:
- Header
- Status summary
- Tabbed settings sections
- Save actions
- Diagnostics/tools section
- Help/documentation

## REST API Structure

```
/wp-json/forge/v1/seo/...
/wp-json/forge/v1/image/...
/wp-json/forge/v1/form/...
/wp-json/forge/v1/cache/...
```

## Versioning Model

- Plugins have independent semver
- `DevForge/shared` has its own semver
- Suite can have a named release tag

Example:
- SEO Forge 1.2.0
- Image Forge 1.1.0
- Form Forge 1.0.0
- Cache Forge 1.0.3
- DevForge/shared 1.3.0
- Suite release: ForgeWordPress 2026.1

## Delivery Phases

### Phase 0 — Foundation

- Monorepo
- Coding standards
- Build pipeline
- Packaging scripts
- DevForge/shared PHP foundation
- DevForge/shared React settings shell
- Base plugin bootstrap
- Common REST helpers
- Common admin shell

### Phase 1 — MVP Plugin Delivery

**SEO Forge MVP:**
- Meta defaults
- Open Graph
- Twitter Cards
- JSON-LD base schema
- XML sitemap
- Settings UI

**Image Forge MVP:**
- Upload-time optimisation
- WebP conversion
- Lazy loading toggle
- Bulk optimisation endpoint
- Settings UI

**Form Forge MVP:**
- Form CPT
- Submissions CPT
- Gutenberg block
- Notifications
- Honeypot protection
- Basic admin review

**Cache Forge MVP:**
- File-based page cache
- Browser cache headers
- HTML minifier
- Purge all
- Purge on content update

### Phase 2 — Suite Orchestration

- ForgeWordPress overview dashboard
- Health/diagnostics registry
- Plugin registry
- Shared notices
- Event contracts
- Environment checks
- Shared debug tooling

### Phase 3 — Advanced Capability

**SEO Forge:** Post-level controls, breadcrumb schema, richer schema, granular robots
**Image Forge:** Background queues, responsive variants, optimisation reports
**Form Forge:** Conditional logic, exports, webhooks, advanced fields
**Cache Forge:** Cache warming, exclusion patterns, analytics, smarter invalidation

### Phase 4 — Productisation

- Licensing
- Telemetry
- Paid tiers
- Remote update controls
- Multisite management
- White-label capability
- Extension marketplace model

## Recommended Release Order

1. DevForge/shared (foundation)
2. SEO Forge (fastest visible value)
3. Image Forge (performance + media)
4. Cache Forge (high value, needs compatibility testing)
5. Form Forge (most UX/workflow complexity)

## Governance Model

| Role | Owns |
|------|------|
| Suite/platform owner | DevForge/shared, coding standards, shared contracts, admin design system, release orchestration |
| Plugin owners | Plugin domain logic, plugin roadmap, migrations, plugin-specific quality |
| Product owner | Suite direction, release priorities, commercial model, feature sequencing |

## Final Orchestration Position

ForgeWordPress should be run as:

- **One suite**
- **Four bounded plugins**
- **One internal foundation package:** DevForge/shared
- **One shared admin UX**
- **One set of technical contracts**
- **One disciplined release process**

**Core rule:**
- `DevForge/shared` handles infrastructure and shared UI
- Plugins handle domain capability
- Hooks handle coordination
- Suite shell handles product experience

This gives a clean platform instead of a plugin pile-up.