---
applyTo: "**/*.tf"
---

# Terraform instructions

- Prefer declarative, reusable modules with clear input/output contracts.
- Keep infrastructure state and secrets handling aligned with least-privilege principles.
- Use explicit providers and version pinning for stability.
- Design for multi-environment deployment with clear variable separation.
- Avoid over-scoping IAM roles and storage permissions.
- Keep network, storage, compute, and observability concerns modular and auditable.
- Validate changes with Terraform fmt and plan where practical.
