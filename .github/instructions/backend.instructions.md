---
applyTo: "**/*.py"
---

# Backend instructions

When developing backend code, follow the **`backend-api-development`** skill and `docs/adr/0001-backend-service-architecture.md`.

- Target Python/FastAPI service code unless the repository documents another backend framework.
- Keep API, application/use-case, domain, and infrastructure responsibilities separate (thin routers → services → domain → repositories), async-first.
- Follow the canonical module layout: `app/main.py`, `app/core/`, `app/api/v1/`, `app/domain/<context>/`, `app/repositories/`, `app/schemas/`.
- Use Pydantic v2 for API and agent contracts; load config via `pydantic-settings`.
- Inject dependencies via FastAPI `Depends`; no stateful module-level singletons.
- Do not expose ORM models as public API schemas.
- The MCP server is a separate repository built with FastMCP — do not implement it here.
- Do not author Dockerfiles/Helm/Kubernetes manifests (Platform-owned); hand off the runtime spec instead.
- Keep business calculations deterministic and independently testable.
- Include organization/project scoping in persistence operations.
- Use migrations for persistence changes.
- Do not access another domain service's tables.
- Add structured logging and propagate trace/correlation IDs.
- Convert expected domain failures into stable API errors.
- Add unit/API tests for changed behavior.
