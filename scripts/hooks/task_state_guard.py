"""After an edit of .ai/tasks/<id>/task-state.yaml, run `vv.py validate <id>` and report errors to the agent.

Usage: python scripts/hooks/task_state_guard.py --runtime cursor|claude  (reads one JSON object from stdin)
Never blocks; it only returns the validator output so Main does not need a separate `validate` call.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

TASK_STATE = re.compile(r"\.ai[\\/]tasks[\\/](\d{8}-[a-z0-9-]+)[\\/]task-state\.yaml$")


def edited_path(payload: dict, runtime: str) -> str:
    if runtime == "claude":
        tool_input = payload.get("tool_input") or {}
        return str(tool_input.get("file_path", ""))
    return str(payload.get("file_path") or payload.get("filePath") or "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", choices=("cursor", "claude"), required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    match = TASK_STATE.search(edited_path(payload if isinstance(payload, dict) else {}, args.runtime))
    if not match:
        if args.runtime == "cursor":
            print(json.dumps({}))
        return 0
    task_id = match.group(1)
    result = subprocess.run(
        [sys.executable, "scripts/vv.py", "validate", task_id],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    output = (result.stdout + result.stderr).strip()
    message = f"vv.py validate {task_id}: {'PASS' if result.returncode == 0 else 'FAIL'}\n{output}".strip()
    if args.runtime == "cursor":
        print(json.dumps({"agentMessage": message[:2000]}))
    else:
        print(message[:2000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
