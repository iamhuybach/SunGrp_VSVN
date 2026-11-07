"""Deny destructive Git and delete commands from agent shells (AGENTS.md §8, D-05 of 20261106-agent-system-unify-api).

Usage: python scripts/hooks/git_guard.py --runtime cursor|claude|codex  (reads one JSON object from stdin)
Cursor: prints {"permission": "allow"|"deny", ...}. Claude Code: exit 2 with the reason on stderr to deny.
Codex PreToolUse: prints {"hookSpecificOutput": {"permissionDecision": "deny", ...}} and exits 0.
`git commit` is allowed; the user's turn decides whether it is wanted.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

# Global options before the subcommand, including `-C <path>` and `-c <key=value>`, whose argument has no leading dash.
GIT = r"^git(\s+(-[Cc]\s+\S+|--?[\w-]+(=\S+)?))*\s+"
DENY = [
    (re.compile(GIT + r"push\b"), "git push is reserved for the user"),
    (re.compile(GIT + r"reset\b"), "git reset is prohibited for agents"),
    (re.compile(GIT + r"rebase\b"), "git rebase is prohibited for agents"),
    (re.compile(GIT + r"commit\b.*--amend"), "git commit --amend rewrites history"),
    (re.compile(GIT + r"filter-branch\b"), "history rewrite is prohibited"),
    (re.compile(GIT + r"clean\b"), "git clean deletes untracked files recursively"),
    (re.compile(r"^rm\s+(-\S*[rR]\S*|--recursive)\b"), "recursive delete is prohibited"),
    (re.compile(r"^(rmdir|rd)\b.*(\s/s\b|\s-r)", re.IGNORECASE), "recursive delete is prohibited"),
    (re.compile(r"^remove-item\b.*-recurse", re.IGNORECASE), "recursive delete is prohibited"),
    (re.compile(r"^del\b.*\s/s\b", re.IGNORECASE), "recursive delete is prohibited"),
]
SPLIT = re.compile(r"&&|\|\||;|\||\n")
LOG = Path(__file__).resolve().parents[2] / ".ai" / ".tmp" / "hooks.log"


def extract_command(payload: dict, runtime: str) -> str:
    if runtime in ("claude", "codex"):
        tool_input = payload.get("tool_input") or {}
        return str(tool_input.get("command", ""))
    return str(payload.get("command", ""))


def find_violation(command: str) -> str | None:
    for segment in SPLIT.split(command):
        text = segment.strip().lstrip("(").strip()
        for pattern, reason in DENY:
            if pattern.search(text):
                return f"{reason}: `{text[:120]}`"
    return None


def _log(message: str) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as handle:
            handle.write(f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {message}\n")
    except OSError:
        pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", choices=("cursor", "claude", "codex"), required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    command = extract_command(payload if isinstance(payload, dict) else {}, args.runtime)
    violation = find_violation(command)
    if args.runtime == "cursor":
        if violation:
            _log(f"deny cursor {violation}")
            print(json.dumps({
                "permission": "deny",
                "userMessage": f"Blocked by scripts/hooks/git_guard.py: {violation}",
                "agentMessage": f"Command denied ({violation}). Push, reset, rebase, amend, and recursive delete belong to the user; ask instead.",
            }))
        else:
            print(json.dumps({"permission": "allow"}))
        return 0
    if args.runtime == "codex":
        # On Windows Codex runs the hook through `powershell -Command`, which turns exit 2 into exit 1 (non-blocking).
        if violation:
            _log(f"deny codex {violation}")
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Blocked by scripts/hooks/git_guard.py: {violation}",
            }}))
        return 0
    if violation:
        _log(f"deny {args.runtime} {violation}")
        print(f"Blocked by scripts/hooks/git_guard.py: {violation}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
