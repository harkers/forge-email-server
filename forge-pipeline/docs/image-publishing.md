# Forge Pipeline Image Build / Publish Assumptions

This document describes the intended assumptions for publishing Forge Pipeline as container images.

## Expected images

Two images are expected:

- `forge-pipeline-api`
- `forge-pipeline-web`

## Suggested tagging model

Recommended tags:

- `latest`
- semantic release tags such as `v1.0.0`
- optional commit-sha tags for traceability

Examples:

- `ghcr.io/your-org/forge-pipeline-api:latest`
- `ghcr.io/your-org/forge-pipeline-api:v0.1.0`
- `ghcr.io/your-org/forge-pipeline-web:latest`
- `ghcr.io/your-org/forge-pipeline-web:v0.1.0`

## Build assumptions

### API image

Build command:

```bash
docker build -f Dockerfile.api -t forge-pipeline-api:latest .
```

### Web image

Build command:

```bash
docker build -f Dockerfile.web -t forge-pipeline-web:latest .
```

## Registry assumptions

Forge Pipeline should be publishable to a standard container registry such as:

- GitHub Container Registry (GHCR)
- Docker Hub
- private registry
- self-hosted registry

## Runtime assumptions

Published images assume:

### API
- mounted persistent storage at `/app/storage`
- optional env var: `FORGE_PIPELINE_API_KEY`

### Web
- no persistent app state inside the web image
- `/api/` proxied internally to the API service

## Deployment assumptions

A deploy environment should provide:

- image pull access
- persistent volume for SQLite DB and exports
- reverse proxy or direct HTTP access to the web container
- environment injection for API key if used

## Autodiscovery / integration friendliness

When published, the container package should be accompanied by:

- clear README
- deployment docs
- API docs
- webhook docs
- backup docs
- env/config examples
- image purpose summary
- exposed ports and healthcheck behavior

## Suggested future automation

If you later automate publishing, the pipeline should:

1. build both images
2. run basic validation / smoke checks
3. tag images consistently
4. push images to the chosen registry
5. publish release notes/docs links alongside the images
