# Security policy

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Report it privately to the repository owner with a description, reproduction steps, and impact.

## Repository safeguards

- Credentials belong in a local `.env` file, which is ignored by Git.
- The Compose stack publishes services only on `127.0.0.1` by default.
- Grafana signup and anonymous access are disabled.
- Containers use pinned image tags; review and update them regularly.
- Prometheus and Grafana state is stored in Docker named volumes, never committed.
- The app image runs as a non-root user and has a read-only filesystem.

## Production notes

This repository is an educational baseline, not a complete production deployment. Put Grafana and Prometheus behind authenticated TLS ingress, restrict `/metrics` to the monitoring network, manage secrets with a secret manager, and use an external metrics backend for high availability.
