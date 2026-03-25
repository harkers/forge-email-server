# Deployer Agent Examples

## Good deployment report
- Artifact: localhost:5000/example-web:latest
- Target: titan host-network deployment
- Deploy result: container started
- Verification: GET /health returned 200
- Open risk: browser path not checked yet
- Rollback note: previous image tag still available

## Anti-pattern
Do not report deploy success only because the deploy command returned 0.
Post-deploy verification is required.
