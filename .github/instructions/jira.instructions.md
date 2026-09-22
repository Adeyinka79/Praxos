---
applyTo: "**/*.{md,ts,tsx,js,jsx,py}"
---

# Jira instructions

- Treat Jira as the authoritative source for work items, acceptance criteria, status, priority, dependencies, and comments when available.
- Before coding or refining backlog items, read the entire Jira story or issue and identify the business objective, acceptance criteria, functional requirements, business rules, security requirements, and dependencies.
- Use the repository user-story format for all Jira work: title, user story, background/context, acceptance criteria, functional requirements, business rules, validation and error handling, technical notes, security requirements, non-functional requirements, dependencies, out of scope, and definition of done.
- Write acceptance criteria that are clear, specific, measurable, testable, independent when possible, and traceable to the user story. Prefer Given / When / Then phrasing.
- Preserve traceability across the flow: User Story → Acceptance Criterion → Implementation → Test.
- Do not invent business requirements. If an assumption is required, label it clearly as an assumption and call it out for review.
- Keep backlog items aligned with the project roadmap and the real-estate digital thread across land, feasibility, design, finance, construction, sales, and operations.
- Separate backlog planning from implementation design. The Jira agent should define the problem, scope, sequencing, and acceptance criteria, not replace the engineering specialist responsible for implementation details.
- Break large work into smaller, reviewable issues with clear value, dependencies, and sequencing.
- When a story crosses into frontend, backend, architecture, or platform work, hand off using the standard handoff format and identify the correct specialist.
- Ensure each Jira item is ready for execution: objective is clear, stakeholders are identified, dependencies are visible, and acceptance criteria are testable.
- Use the Definition of Done standard: implementation complete, acceptance criteria satisfied, tests run, security requirements met, documentation updated, no secrets or credentials committed, and code ready for review.
- When a work-item key is provided, preserve it in branch names, PR references, and commit messages when applicable.
- Do not change Jira issue content, status, assignee, story points, or workflow state unless the requested workflow explicitly allows it.
- If a requirement is ambiguous, surface the ambiguity and recommend the smallest safe next step before implementation begins.
- Prefer delivery planning that supports sprint readiness, dependency management, and risk visibility without creating noisy or low-value backlog items.
- Keep output structured and operational: scope/context, Jira recommendations, risks and guardrails, and next steps.
