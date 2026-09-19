# GitHub Copilot Instructions — Real Estate Development AI Platform

This repository is part of an AI-powered operating system for the complete real estate development lifecycle, and it uses a **role-separated multi-agent engineering model**.

## Read architecture first

Before significant implementation, read:
- `README.md`
- `PROJECT_ARCHITECTURE.md`
- relevant ADRs under `docs/adr/`

Preserve the established architecture unless the task explicitly changes it.

## Architecture principles

- Domain-oriented.
- API-first.
- Structured data first.
- Multi-tenant by design.
- Event-driven where appropriate.
- AI-native, not AI-dependent.
- Human approval for high-impact actions.
- Maintain the digital thread across parcel, feasibility, design, BIM, cost, schedule, construction, sale, and operations.

## Critical boundaries

- Do not directly access another domain service's database tables.
- Agents do not directly manipulate production databases.
- MCP tools call domain APIs/services rather than becoming a second business-logic layer.
- Deterministic services perform authoritative calculations and state transitions.
- Avoid premature microservice proliferation during the MVP.

## Baseline stack

- Next.js + TypeScript + Tailwind
- React Three Fiber / Three.js
- Python + FastAPI + Pydantic
- PostgreSQL + PostGIS
- Redis
- S3
- EventBridge + SQS
- LangGraph or equivalent
- MCP for agent tools
- Terraform
- ECS Fargate
- OpenTelemetry + CloudWatch
- GitHub Actions

## Standing engineering standards

- **Backend:** professional layered FastAPI, Pydantic v2, dependency injection, canonical module layout; the MCP server is a separate FastMCP repo. See `docs/adr/0001-backend-service-architecture.md` and the `backend-api-development` skill.
- **Delivery:** dev deploys automatically (build → ECR → Helm to self-managed k8s); prod is a manual, two-stage, reviewer-gated release. See `docs/adr/0002-cicd-deployment-architecture.md` and the `cicd-development` skill.

## Quality requirements

- Add or update tests for behavior changes.
- Use migrations for schema changes.
- Enforce tenant/project scope server-side.
- Never commit secrets.
- Prefer typed contracts.
- Use correlation/trace IDs for multi-step workflows.
- For material architecture changes, add or update an ADR.

## Mandatory governance rules

1. Respect `governance/agent-boundaries.yaml`. Default policy is **deny**.
2. Role boundary is more important than task completion.
3. Never modify files owned by another role to finish a task faster.
4. Use `contracts/handoffs/handoff.schema.json` for cross-role requests.
5. Read the nearest `AGENTS.md` and matching `.github/instructions/*.instructions.md` before editing files.
6. Prefer the smallest safe change. Do not perform unrelated refactors.
7. Do not expose, commit, log, or invent credentials or secrets.
8. Every implementation change needs appropriate tests or a documented reason why a test is not applicable.
9. Breaking contract changes require explicit architecture/product approval and migration notes.
10. Do not bypass CI, branch protection, CODEOWNERS, or security controls.

## Agent roles

This repository defines specialized agents in `.github/agents/*.agent.md`, each with owned paths, forbidden paths, allowed skills (`.github/skills/`), and allowed tools. See `docs/AGENT_CATALOG.md` and `docs/AGENT_SKILL_MATRIX.md` for the full roster.

- Product Owner owns product intent and acceptance criteria.
- Scrum Master owns process flow and blockers.
- Engineering Orchestrator owns routing, decomposition, and handoffs, not implementation.
- Solution Architect owns system-level technical decisions, ADRs, and shared contracts.
- UX/UI Designer owns user flows, wireframes, and accessibility specifications.
- Backend, Frontend, Database, API Integration, and AI/ML engineers own code only in their technical area.
- Platform Engineer owns infrastructure and delivery automation.
- QA, Test Automation, Security, Code Reviewer, and Architecture Compliance independently verify work.
- SRE/Observability and Incident/RCA observe and diagnose runtime; they route fixes to implementation owners.
- Release Manager, Documentation, Dependency Manager, and Performance Engineer own their respective supporting scopes.

Routing and boundary rules:

- Choose the agent whose owned paths and skills match the task. If the request spans multiple roles, the Orchestrator decomposes it into role-owned tasks.
- Never answer outside your scope as a substitute for the appropriate specialist. If a task belongs to another agent, create a structured handoff instead of doing the work yourself.
- Label agent-authored pull requests with `agent:<agent-id>` (for example `agent:backend-developer`) so the boundary check in `.github/workflows/agent-boundary-check.yml` can validate them.

Standard handoff format (see `contracts/handoffs/handoff.schema.json`):

- from: [source agent]
- to: [target agent]
- story: [work-item ID]
- reason: [why this is the correct specialist]
- requested_change: [API contract, UI design, architecture decision, migration, etc.]
- affected_interfaces: [shared contracts touched]
- acceptance_criteria: [testable conditions]
- blocking: [true/false]
- evidence: [context or links]

## Jira-driven development

When a Jira work-item key is provided, retrieve the issue first and use its stated objective and acceptance criteria as the implementation contract. Preserve traceability between Jira work, code changes, tests, and the resulting pull request. Do not mark work Done solely because code was generated.
