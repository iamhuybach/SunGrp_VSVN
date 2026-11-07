"""Local scan: count repeated user actions for task 20261106-agent-system-unify-api.

Read-only. Sources (allowed by request.md): .ai/tasks/*/task-state.yaml, .ai/tasks/*/resume.md,
the "Quyết định hiện hành" section of .ai/tasks/*/decision.md, `git log --stat -n 200`, and this
project's agent transcripts. Prints counts only, plus sanitized error snippets (<= 160 chars).
No names, emails, tokens, or payload values are printed.

Usage: python .ai/tasks/20261106-agent-system-unify-api/evidence/probes/user_actions_scan.py [transcripts_dir]
"""
from __future__ import annotations

import collections
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[5]
SELF_TASK = "20261106-agent-system-unify-api"
DEFAULT_TRANSCRIPTS = Path(os.environ.get("USERPROFILE", "~")).expanduser() / (
    ".cursor/projects/d-git-SunGrp-VSVN/agent-transcripts"
)

TEMPLATES = [
    ("A19", r"external-smoke"),
    ("A18", r"Thay đổi agent-system"),
    ("A17", r"Bước runtime được bỏ qua"),
    ("A16", r"^Góp ý:|\nGóp ý:"),
    ("A14", r"Phase:\s*proposal[\s\S]*requirements-analyst|READY_FOR_ANALYSIS"),
    ("A13", r"Bảng đích:"),
    ("A15", r"Task mới:[\s\S]*Phase:\s*proposal"),
    ("A12", r"Review implementation chưa commit"),
    ("A11", r"Giải thích cho người vận hành"),
    ("A10", r"Chỉ dựa vào output đó và resume\.md"),
    ("A9", r"Lỗi \(đã làm sạch\)"),
    ("A8", r"Phase:\s*closeout[\s\S]*Kết quả:"),
    ("A7", r"Phase:\s*runtime"),
    ("A6", r"Chỉ khi status là waiting_architecture hoặc reviewing"),
    ("A5", r"Phase:\s*remediate"),
    ("A4", r"Phase:\s*implement\b(?!\s*\+)"),
    ("A3", r"Kết quả đã dán"),
    ("A2", r"Phase:\s*triage\s*\+\s*implement"),
    ("A1", r"Task mới:[\s\S]*Phase:\s*triage"),
]
MANUAL_STEPS = {
    "paste_probe_result": r"evidence/results/|Kết quả đã dán|đã dán|kết quả probe",
    "ran_runbook_or_fabric": r"runtime-runbook|runbook|Fabric DEV|đã chạy",
    "copy_file_or_content": r"\bchép\b|\bcopy\b|\bdán\b",
    "commit_request": r"\bcommit\b",
    "model_or_exception_override": r"exception|EX-\d+|EXC-\d+|model_override",
}
ERROR_PAT = re.compile(
    r"(RunnerError|Traceback|Error:|ERROR|FAIL(?:ED)?\b|timed out|timeout|not logged in|"
    r"structured output|immutab|fallback|unavailable|exit code [1-9]|non-zero|rate limit|"
    r"overloaded|permission denied|Rejected)",
    re.I,
)
SANITIZE = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "<email>"),
    (re.compile(r"(?i)(token|key|secret|password|sig|sas)[=:]\s*\S+"), r"\1=<redacted>"),
    (re.compile(r"[A-Za-z0-9_-]{32,}"), "<long-id>"),
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I), "<uuid>"),
    (re.compile(r"(?i)C:\\Users\\[^\\\s]+"), r"C:\\Users\\<user>"),
    (re.compile(r"(?i)/Users/[^/\s]+"), "/Users/<user>"),
]


def sanitize(text: str) -> str:
    text = " ".join(text.split())
    for pattern, repl in SANITIZE:
        text = pattern.sub(repl, text)
    return text[:160]


def section(title: str) -> None:
    print(f"\n## {title}\n")


def table(rows, headers) -> None:
    print("| " + " | ".join(headers) + " |")
    print("|" + "---|" * len(headers))
    for row in rows:
        print("| " + " | ".join(str(c) for c in row) + " |")


def scan_tasks() -> None:
    tasks = sorted(p for p in (REPO / ".ai/tasks").iterdir() if p.is_dir() and p.name[:8].isdigit())
    tasks = [t for t in tasks if t.name != SELF_TASK]
    status, rounds, gates, exc_roles, signals = (collections.Counter() for _ in range(5))
    review_hist, arch_hist, verif_hist = (collections.Counter() for _ in range(3))
    findings_open = 0
    waiting = collections.Counter()
    for task in tasks:
        state_path = task / "task-state.yaml"
        if state_path.is_file():
            state = yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}
            status[state.get("task", {}).get("status")] += 1
            r = state.get("rounds", {}) or {}
            review_hist[r.get("review", 0)] += 1
            arch_hist[r.get("architecture", 0)] += 1
            verif_hist[r.get("verification", 0)] += 1
            rounds["runtime_failure>0"] += 1 if r.get("runtime_failure", 0) else 0
            for gate, value in (state.get("gates") or {}).items():
                gates[(gate, value)] += 1
            for exc in state.get("exceptions") or []:
                if isinstance(exc, dict):
                    exc_roles[(exc.get("role"), exc.get("model"))] += 1
            if state.get("model_policy_exception"):
                exc_roles[("legacy model_policy_exception", "-")] += 1
            for s in (state.get("classification") or {}).get("signals") or []:
                signals[s] += 1
            findings_open += len(state.get("open_findings") or [])
        resume = task / "resume.md"
        if resume.is_file():
            text = resume.read_text(encoding="utf-8")
            m = re.search(r"Waiting on[^\n]*\n([\s\S]*?)(\n#|\Z)", text, re.I)
            body = (m.group(1) if m else "").lower()
            for key, pat in {
                "user_commit": r"commit", "fabric_dev_probe_or_runtime": r"fabric|probe|runbook|runtime",
                "user_decision": r"decision|chốt|choose|approve", "gate_or_cli": r"run-gate|cli|gate",
                "nothing": r"^\s*-?\s*(none|nothing|không có)",
            }.items():
                if re.search(pat, body, re.M):
                    waiting[key] += 1
    section(f"Task state ({len(tasks)} tasks, excluding this task)")
    table(sorted(status.items(), key=lambda x: -x[1]), ["status", "tasks"])
    print()
    table([(k, review_hist[k], arch_hist[k], verif_hist[k]) for k in sorted(set(review_hist) | set(arch_hist) | set(verif_hist))],
          ["round value", "rounds.review", "rounds.architecture", "rounds.verification"])
    print(f"\nTasks with runtime_failure > 0: {rounds['runtime_failure>0']}. Open findings across tasks: {findings_open}.")
    section("Gate results across tasks")
    by_gate = collections.defaultdict(dict)
    for (gate, value), n in gates.items():
        by_gate[gate][value] = n
    values = sorted({v for d in by_gate.values() for v in d})
    table([[g] + [by_gate[g].get(v, 0) for v in values] for g in sorted(by_gate)], ["gate"] + values)
    section("Model exceptions recorded in task-state.yaml")
    table(sorted(((r, m, n) for (r, m), n in exc_roles.items()), key=lambda x: -x[2]), ["role", "model", "entries"])
    section("Classification signals")
    table(signals.most_common(), ["signal", "tasks"])
    section("resume.md 'Waiting on' categories (a task may hit several)")
    table(waiting.most_common(), ["category", "tasks"])


def scan_decisions() -> None:
    prefixes, topics = collections.Counter(), collections.Counter()
    for path in sorted((REPO / ".ai/tasks").glob("*/decision.md")):
        if path.parent.name == SELF_TASK:
            continue
        text = path.read_text(encoding="utf-8")
        m = re.search(r"## Quyết định hiện hành\n([\s\S]*?)(\n## |\Z)", text)
        if not m:
            continue
        for line in m.group(1).splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3 or cells[0] in {"ID", ""} or set(cells[0]) <= {"-"}:
                continue
            prefixes[re.match(r"[A-Za-z]+", cells[0]).group(0).upper() if re.match(r"[A-Za-z]+", cells[0]) else "other"] += 1
            topics[cells[1].lower()] += 1
    section(f"decision.md 'Quyết định hiện hành' rows ({sum(prefixes.values())} rows)")
    table(prefixes.most_common(12), ["ID leading letters", "rows"])
    print("\nTopics appearing in >= 2 rows:\n")
    table([(t, n) for t, n in topics.most_common() if n >= 2], ["topic", "rows"])


def scan_git() -> None:
    out = subprocess.run(
        ["git", "log", "--stat", "-n", "200", "--format=@@%ad", "--date=short"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout
    commits = out.count("@@")
    area = collections.Counter()
    for line in out.splitlines():
        m = re.match(r"\s(\S+)\s+\|\s+", line)
        if not m:
            continue
        path = m.group(1)
        for key, pat in {
            "evidence/results": r"evidence/results/", "evidence/probes": r"evidence/probes/",
            "runtime-runbook.md": r"runtime-runbook\.md", "architecture.md": r"architecture\.md",
            "reviews/": r"/reviews/", "decision.md": r"decision\.md", "resume.md": r"resume\.md",
            "notebooks/": r"^notebooks/", "pipelines/": r"^pipelines/", "sql/": r"^sql/",
            "tests/": r"^tests/", "scripts/vv.py|agent_runner.py": r"^scripts/",
            "agent config (.cursor/.claude/.codex/AGENTS/CLAUDE)": r"^(\.cursor|\.claude|\.codex)/|^(AGENTS|CLAUDE)\.md",
            "docs/context": r"^docs/context/", "docs/AGENT_PROMPT_SAMPLES.md": r"AGENT_PROMPT_SAMPLES",
        }.items():
            if re.search(pat, path):
                area[key] += 1
    section(f"git log --stat -n 200 ({commits} commits; file-change lines per area)")
    table(area.most_common(), ["area", "file changes"])


def iter_messages(path: Path):
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def scan_transcripts(root: Path) -> None:
    files = sorted(root.rglob("*.jsonl")) if root.is_dir() else []
    parents = [f for f in files if f.parent.name != "subagents"]
    templates, manual, tools, shell_cmds, errors = (collections.Counter() for _ in range(5))
    user_turns = 0
    openers = collections.Counter()
    error_samples: dict[str, int] = collections.Counter()
    for f in parents:
        for msg in iter_messages(f):
            role = msg.get("role")
            for part in (msg.get("message") or {}).get("content") or []:
                if not isinstance(part, dict):
                    continue
                if role == "user" and part.get("type") == "text":
                    m = re.search(r"<user_query>([\s\S]*?)</user_query>", part.get("text", ""))
                    if not m:
                        continue
                    query = m.group(1).strip()
                    user_turns += 1
                    hit = next((tid for tid, pat in TEMPLATES if re.search(pat, query)), "none")
                    templates[hit] += 1
                    if hit == "none":
                        words = re.findall(r"\w+:?", query.split("\n", 1)[0])[:2]
                        openers[" ".join(words).lower() or "<empty>"] += 1
                    for key, pat in MANUAL_STEPS.items():
                        if re.search(pat, query, re.I):
                            manual[key] += 1
                elif role == "assistant" and part.get("type") == "tool_use":
                    name = part.get("name", "?")
                    tools[name] += 1
                    raw_input = part.get("input")
                    cmd = raw_input.get("command") if isinstance(raw_input, dict) else None
                    if name == "Shell" and isinstance(cmd, str):
                        for sub in re.findall(r"python\s+scripts[\\/]vv\.py\s+([\w-]+)", cmd):
                            shell_cmds[f"vv.py {sub}"] += 1
                        for sub in re.findall(r"(?:^|[;&|]\s*)git\s+([\w-]+)", cmd.strip()):
                            shell_cmds[f"git {sub}"] += 1
                        for tool in re.findall(r"\b(claude|codex|pytest|ruff|sqlfluff|mvn|mvnw|docker)\b", cmd):
                            shell_cmds[tool] += 1
                elif role == "assistant" and part.get("type") == "text":
                    for line in part.get("text", "").splitlines():
                        if ERROR_PAT.search(line) and re.search(r"run-gate|run-author|claude|codex|CLI|runner|verify|doctor|external", line, re.I):
                            errors[ERROR_PAT.search(line).group(1).lower()] += 1
                            error_samples[sanitize(line)] += 1
    section(f"Transcripts: {len(parents)} parent chats, {len(files) - len(parents)} subagent files, {user_turns} user turns")
    order = {tid: i for i, (tid, _) in enumerate(sorted(TEMPLATES, key=lambda t: int(t[0][1:])))}
    rows = sorted(templates.items(), key=lambda x: order.get(x[0], 99))
    table(rows, ["template (A1–A19, first match)", "user turns"])
    print("\nFirst two words of unmatched user turns (top 15):\n")
    table(openers.most_common(15), ["opener", "user turns"])
    print("\nRepeated manual-step mentions in user turns (a turn may match several):\n")
    table(manual.most_common(), ["manual step", "user turns"])
    section("Assistant tool calls (parent chats)")
    table(tools.most_common(15), ["tool", "calls"])
    section("Shell commands inside assistant tool calls")
    table(shell_cmds.most_common(30), ["command", "occurrences"])
    section("Gate/CLI failure keywords in assistant text (lines that also name a gate/CLI)")
    table(errors.most_common(), ["keyword", "lines"])
    print("\nMost frequent sanitized lines (count >= 1, top 25):\n")
    table([(n, s.replace("|", "/")) for s, n in error_samples.most_common(25)], ["count", "sanitized line"])


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TRANSCRIPTS
    print("# user_actions_scan output\n\nRepo: <repo>. Transcripts root: <agent-transcripts>.")
    scan_tasks()
    scan_decisions()
    scan_git()
    scan_transcripts(root)


if __name__ == "__main__":
    main()
