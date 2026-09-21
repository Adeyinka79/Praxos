# Agent boundary enforcement hook

This directory contains a local, runtime enforcement layer for the role boundaries
defined in `governance/agent-boundaries.yaml`. It complements (does not replace) the
PR-time boundary check in `.github/workflows/agent-boundary-check.yml`.

## Why this exists

The `owned`/`forbidden` paths in `.github/agents/*.agent.md` and in the governance
manifest are **instructions**, not a runtime sandbox. A model can ignore them (as a
weaker model did when a "Product Owner" agent started editing `backend/**`). This hook
makes the boundary **deterministic** in VS Code: an out-of-boundary file edit is blocked
before it happens.

## How it works

- Each `.github/agents/<id>.agent.md` declares an **agent-scoped** `PreToolUse` hook in
  its frontmatter:

  ```yaml
  hooks:
    PreToolUse:
      - type: command
        command: "python3 .github/hooks/enforce_boundaries.py <id>"
  ```

- Agent-scoped hooks run **only while that agent is active** (including when it is invoked
  as a subagent), so the script receives the agent id as `argv[1]` — no need to detect the
  active agent from the payload.
- `enforce_boundaries.py` reads the tool call on stdin, extracts the target file path(s),
  and checks them against `governance/agent-boundaries.hook.json`:
  - path in the agent's `forbidden` list → **deny**
  - path in a shared governance area (`.github/agents/`, `.github/skills/`, `governance/`,
    `contracts/handoffs/`) the agent does not own → **deny**
  - otherwise → allow (normal approval flow proceeds)
- Read-only and terminal tools are ignored. Errors (missing policy, unknown agent) **fail
  open** with a warning so the hook never blocks legitimate work.
- Decisions for write tools are appended to `.github/hooks/enforce.log` (gitignored).

## Required setting

Agent-scoped hooks are a preview feature and must be enabled:

```jsonc
// .vscode/settings.json (already set in this repo)
"chat.useCustomAgentHooks": true
```

Confirm the hook loaded via **Developer: Show Agent Debug Logs** (look for "Load Hooks")
or the **GitHub Copilot Chat Hooks** output channel.

## Keeping the policy in sync

`agent-boundaries.hook.json` is generated from the YAML manifest — do not edit it by hand:

```bash
# regenerate after changing governance/agent-boundaries.yaml
python scripts/validate_agent_boundaries.py --emit-hook-policy governance/agent-boundaries.hook.json

# verify it is in sync (also run in CI)
python scripts/validate_agent_boundaries.py --check-hook-policy governance/agent-boundaries.hook.json
```

## Limitations

- **VS Code only.** This enforces in the editor; pushed code is still gated by the PR
  boundary check + CODEOWNERS + branch protection.
- **Local file edits only.** Terminal commands (e.g. shell redirection into a forbidden
  path) are not inspected here. Use `chat.agent.sandbox` / approval settings for that vector.
- **MCP / external tools are exempt.** Calls like `mcp_atlassian-mcp_createJiraIssue`,
  `github/*`, or `postgres/*` talk to external services and never write local repo files,
  so the hook ignores them (path checks apply only to editor file-write tools).
- If `chat.useCustomAgentHooks` is disabled or hooks are turned off org-wide, enforcement
  silently does not run — the boundary reverts to guidance + PR CI.
