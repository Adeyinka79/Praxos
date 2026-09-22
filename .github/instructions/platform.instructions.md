---
applyTo: "platform/**,.github/workflows/**"
---

# Platform rules

Platform changes must be declarative, least-privilege, reproducible, and environment-aware. Never embed secrets. Application business logic does not belong in infrastructure files. Include validation/plan output where appropriate.

When building CI/CD or deployment infra, follow the **`cicd-development`** skill and `docs/adr/0002-cicd-deployment-architecture.md`:

- **Dev deploy is automated:** build image → push to AWS ECR → Helm deploy to the self-managed dev Kubernetes cluster on push/merge.
- **Prod deploy is manual and two-stage:** stage 1 runs all tests; stage 2 (build → ECR → Helm deploy to prod) is gated behind a GitHub Environment (`production`) with required reviewers and only runs after approval.
- Tag images with the commit SHA; authenticate to AWS/ECR with GitHub secrets (least privilege); connect to the cluster via a `KUBECONFIG` secret; use per-environment Helm values files.
- Keep build and deploy as distinct steps; document rollback (`helm rollback`) and failure behavior.
