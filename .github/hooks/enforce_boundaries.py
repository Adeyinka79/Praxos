#!/usr/bin/env python3
"""PreToolUse hook: block file edits that fall outside the active agent's boundary.

Wired as an *agent-scoped* hook in each `.github/agents/<id>.agent.md` frontmatter:

    hooks:
      PreToolUse:
        - type: command
          command: "python3 .github/hooks/enforce_boundaries.py <agent-id>"

Because agent-scoped hooks only run while that agent is active, the agent id is
passed as argv[1] -- no need to detect the active agent from the payload.

Reads the tool call on stdin, checks the target path(s) against
governance/agent-boundaries.hook.json (generated from governance/agent-boundaries.yaml),
and returns permissionDecision "deny" for out-of-boundary writes. Read-only and
terminal tools are ignored. Errors fail OPEN (warn but allow) so the hook never
bricks normal editing.

Requires the VS Code setting `chat.useCustomAgentHooks: true` (set in .vscode/settings.json).
"""
import fnmatch
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "governance" / "agent-boundaries.hook.json"
LOG = Path(__file__).resolve().parent / "enforce.log"

# Known local file-writing tools (VS Code / Copilot / Claude aliases), lowercased.
FILE_WRITE_TOOLS = {
    "create_file", "createfile", "edit_file", "editfile", "editfiles",
    "replace_string_in_file", "insert_edit_into_file", "apply_patch", "applypatch",
    "delete_file", "deletefile", "notebook_edit", "notebookedit", "multiedit",
    "write", "edit", "str_replace", "str_replace_editor", "search_replace",
    "create_directory", "createdirectory",
}
# Fallback verb match for editor file tools we don't recognize by name.
WRITE_VERB_RE = re.compile(
    r"(create|edit|write|replace|insert|apply|patch|delete|notebook|modify)", re.I
)
# MCP / external tools (e.g. mcp_atlassian-mcp_createJiraIssue, github/*, postgres/*)
# call external services -- they never edit local repo files, so never enforce on them.
MCP_TOOL_RE = re.compile(r"(^mcp[_-]|[-_]mcp[_-]|/)", re.I)

PATH_KEYS = {
    "filepath", "file_path", "path", "target_file", "targetfile", "uri",
    "filename", "file", "notebookuri", "absolute_path", "relative_path", "newfilepath",
    "files", "paths", "filepaths", "uris", "filenames",
}


def is_file_write(tool):
    t = tool.strip().lower()
    if not t or MCP_TOOL_RE.search(t):
        return False
    if t in FILE_WRITE_TOOLS:
        return True
    return bool(WRITE_VERB_RE.search(t))


def emit(obj):
    print(json.dumps(obj))


def allow():
    emit({"continue": True})
    sys.exit(0)


def warn_allow(message):
    emit({"continue": True, "systemMessage": message})
    sys.exit(0)


def deny(reason):
    emit({"hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": reason}})
    sys.exit(0)


def log(line):
    try:
        with LOG.open("a") as fh:
            fh.write(line.rstrip() + "\n")
    except Exception:
        pass


def collect_paths(node, out, under_path_key=False):
    """Collect path-like strings.

    A bare string is only treated as a path when it (or the array containing it)
    sits under a path-like key such as `filePath` or `files`. This prevents grabbing
    arbitrary values (e.g. Jira labels/components) that merely look like a path.
    """
    if isinstance(node, dict):
        for k, v in node.items():
            collect_paths(v, out, k.lower() in PATH_KEYS)
    elif isinstance(node, list):
        for item in node:
            collect_paths(item, out, under_path_key)
    elif isinstance(node, str):
        if under_path_key:
            out.append(node)


def to_repo_relative(raw):
    p = raw.strip()
    if p.startswith("file://"):
        p = p[len("file://"):]
    path = Path(p)
    if path.is_absolute():
        try:
            rel = path.resolve().relative_to(ROOT)
        except Exception:
            return None  # outside the repo -> not our concern
        return rel.as_posix()
    s = Path(p).as_posix()
    return s[2:] if s.startswith("./") else s


def matches(path, patterns):
    for pat in patterns:
        if pat.endswith("/**") and (path == pat[:-3].rstrip("/") or path.startswith(pat[:-2])):
            return True
        if fnmatch.fnmatch(path, pat):
            return True
    return False


def main():
    agent = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except Exception:
        allow()

    tool = str(data.get("tool_name", ""))
    if not is_file_write(tool):
        allow()  # read/search/terminal/MCP etc. -- not a local file write

    tool_input = data.get("tool_input")
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except Exception:
            tool_input = {}
    if not isinstance(tool_input, (dict, list)):
        allow()

    raw_paths = []
    collect_paths(tool_input, raw_paths)
    rels = [r for r in (to_repo_relative(p) for p in raw_paths) if r]
    if not rels:
        allow()

    try:
        policy = json.loads(POLICY.read_text())
    except Exception:
        warn_allow(f"[boundary hook] could not read {POLICY.name}; enforcement skipped.")

    cfg = policy.get("agents", {}).get(agent)
    if not cfg:
        warn_allow(f"[boundary hook] unknown agent '{agent}'; enforcement skipped.")

    owns = cfg.get("owns", [])
    forbidden = cfg.get("forbidden", [])
    shared = policy.get("shared_prefixes", [])

    for rel in rels:
        if matches(rel, forbidden):
            log(f"DENY agent={agent} tool={tool} path={rel} reason=forbidden")
            deny(
                f"Role boundary: the '{agent}' agent is forbidden from editing '{rel}'. "
                f"Stop and create a handoff to the owning agent "
                f"(contracts/handoffs/handoff.schema.json) instead of editing this path."
            )
        if any(rel == s.rstrip("/") or rel.startswith(s) for s in shared) and not matches(rel, owns):
            log(f"DENY agent={agent} tool={tool} path={rel} reason=shared-governance")
            deny(
                f"Role boundary: '{rel}' is a shared governance area not owned by the "
                f"'{agent}' agent. Route this change through the owning role via a handoff."
            )

    log(f"ALLOW agent={agent} tool={tool} paths={','.join(rels)}")
    allow()


if __name__ == "__main__":
    main()
