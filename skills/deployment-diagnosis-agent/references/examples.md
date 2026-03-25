# Deployment Diagnosis Examples

## Good diagnosis
- Image started but nginx bound port 80 inside a host-network deployment expecting 4173.
- Result: service health failed despite container creation.
- Recommended fix: align internal listen port/config with deployment target.

## Caution
A running container is not the same thing as a working deployment.
