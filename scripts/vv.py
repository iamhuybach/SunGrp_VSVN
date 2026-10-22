#!/usr/bin/env python3
"""Deterministic VSVN agent-workflow helper."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from scripts import agent_runner
except ImportError:
    import agent_runner  # type: ignore[no-redef]

try:
    import yaml
except ImportError:
    yaml = None

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

TASKS_ROOT = Path(".ai/tasks")
TEMPLATE_ROOT = TASKS_ROOT / "_template"
TASK_ID_RE = re.compile(r"^\d{8}-[a-z0-9]+(?:-[a-z0-9]+)*$")
PROMPTS = {"architect": "architect.md", "review": "review.md"}
ARCHITECT_TOC_MAX_LINES = 150
REVIEW_CARRY_MAX_LINES = 250
FINDING_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*-\d{2,}\b")
STATUSES = {
    "triage", "waiting_evidence", "waiting_architecture", "implementing",
    "verifying", "reviewing", "waiting_runtime", "user_decision",
    "ready_to_merge", "blocked",
}
GATE_RESULTS = {
    "pending", "pass", "fix_required", "evidence_required",
    "user_decision", "not_required",
}
SIGNALS = {
    "stateful_logic", "concurrency", "retry_recovery", "partial_failure",
    "transaction_boundaries", "event_ordering", "idempotency",
    "distributed_behavior", "cross_system", "design_tradeoffs",
    "cross_state_impact",     "runtime_proof_required", "data_evidence_required", "data_model_change",
    "low_probability_high_impact", "deep_reasoning_required",
}
REVIEWERS = {
    "state-correctness-reviewer", "spark-runtime-reviewer",
    "sql-data-reviewer", "fabric-pipeline-reviewer",
}
AUTHOR_LANES = agent_runner.AUTHOR_KIND_LANES
AUTHOR_OUTPUTS = {
    "analysis": "problem-analysis.md", "model": "model-design.md",
    "proposal": "proposal.md", "runbook": "runtime-runbook.md",
}
EXCEPTION_ROLES = {"main", "architect", "review", "author", "author_proposal"}
GATE_NAMES = {
    "evidence", "architecture", "local_verification", "specialist_review",
    "risk_gate", "runtime",
}
TRANSITIONS = {
    "triage": {"waiting_evidence", "waiting_architecture", "implementing", "verifying", "user_decision", "blocked"},
    "waiting_evidence": {"triage", "waiting_architecture", "implementing", "user_decision", "blocked"},
    "waiting_architecture": {"waiting_evidence", "implementing", "user_decision", "blocked"},
    "implementing": {"waiting_evidence", "waiting_architecture", "verifying", "user_decision", "blocked"},
    "verifying": {"implementing", "reviewing", "waiting_runtime", "ready_to_merge", "user_decision", "blocked"},
    "reviewing": {"implementing", "waiting_evidence", "waiting_architecture", "waiting_runtime", "ready_to_merge", "user_decision", "blocked"},
    "waiting_runtime": {"implementing", "waiting_evidence", "waiting_architecture", "ready_to_merge", "user_decision", "blocked"},
    "user_decision": {"triage", "implementing", "waiting_runtime", "ready_to_merge", "blocked"},
    "ready_to_merge": set(),
    "blocked": {"triage", "user_decision"},
}
OWNER_BY_STATUS = {
    "waiting_evidence": "user", "waiting_architecture": "architect",
    "reviewing": "review", "waiting_runtime": "user", "user_decision": "user",
}


def fail(message: str) -> None:
    raise SystemExit(message)


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args], capture_output=True,
        text=True, encoding="utf-8", errors="replace",
    )
    if check and result.returncode:
        fail(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result


def nul_paths(output: str) -> list[str]:
    return [path for path in output.split("\0") if path]


def repo_root() -> Path:
    result = git("rev-parse", "--show-toplevel", check=False)
    if result.returncode:
        fail("Not inside a Git repository.")
    return Path(result.stdout.strip()).resolve()


def validated_task_id(task_id: str) -> str:
    if not TASK_ID_RE.fullmatch(task_id):
        fail(f"Invalid task ID: {task_id!r}. Expected YYYYMMDD-lowercase-slug.")
    return task_id


def task_dir(task_id: str, *, must_exist: bool = True) -> Path:
    validated_task_id(task_id)
    root = TASKS_ROOT.resolve()
    path = (TASKS_ROOT / task_id).resolve()
    if path.parent != root:
        fail(f"Task path escapes {TASKS_ROOT.as_posix()}: {path}")
    if must_exist and not path.is_dir():
        fail(f"Task not found: {path}")
    return path


def require_yaml() -> None:
    if yaml is None:
        fail("PyYAML is required. Run: python -m pip install -r requirements-dev.txt")


@dataclass(frozen=True)
class Heading:
    level: int
    title: str
    start: int
    end: int


@dataclass(frozen=True)
class Cell:
    index: int
    id: str
    cell_type: str
    source: str
    json_start: int | None
    json_end: int | None


def markdown_toc(text: str) -> list[Heading]:
    """Return Markdown headings and their inclusive section ranges."""
    lines = text.splitlines()
    found: list[tuple[int, str, int]] = []
    fence: str | None = None
    for number, line in enumerate(lines, 1):
        fence_match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence_match:
            marker = fence_match.group(1)[0]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is not None:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            title = re.sub(r"\s+#+\s*$", "", match.group(2)).strip()
            found.append((len(match.group(1)), title, number))
    headings: list[Heading] = []
    for index, (level, title, start) in enumerate(found):
        end = len(lines)
        for next_level, _, next_start in found[index + 1:]:
            if next_level <= level:
                end = next_start - 1
                break
        headings.append(Heading(level, title, start, end))
    return headings


def notebook_cells(path: Path) -> list[Cell]:
    """Load notebook cells and map Fabric-formatted JSON line ranges when possible."""
    raw = path.read_text(encoding="utf-8-sig")
    document = json.loads(raw)
    raw_cells = document.get("cells", [])
    if not isinstance(raw_cells, list):
        fail(f"{path.as_posix()} cells must be a list")
    lines = raw.splitlines()
    markers = [index for index, line in enumerate(lines) if re.match(r'^   "cell_type": ', line)]
    ranges: list[tuple[int | None, int | None]] = [(None, None)] * len(raw_cells)
    if len(markers) == len(raw_cells):
        starts = [marker for marker in markers]
        close_index = next(
            (index for index in range(markers[-1] + 1, len(lines)) if re.match(r"^ ],?\s*$", lines[index])),
            len(lines),
        ) if markers else len(lines)
        mapped: list[tuple[int | None, int | None]] = []
        for index, start in enumerate(starts):
            end = starts[index + 1] - 1 if index + 1 < len(starts) else close_index
            mapped.append((start, end))
        ranges = mapped
    result: list[Cell] = []
    for index, item in enumerate(raw_cells):
        if not isinstance(item, dict):
            fail(f"{path.as_posix()} cell {index} must be an object")
        source_value = item.get("source", [])
        source = "".join(source_value) if isinstance(source_value, list) else str(source_value)
        result.append(Cell(
            index=index,
            id=str(item.get("id", "<none>")),
            cell_type=str(item.get("cell_type", "unknown")),
            source=source,
            json_start=ranges[index][0],
            json_end=ranges[index][1],
        ))
    return result


def _cell_label(cell: Cell) -> str:
    lines = cell.source.splitlines()
    if cell.cell_type == "markdown":
        for line in lines:
            match = re.match(r"^\s*#{1,6}\s+(.+?)\s*$", line)
            if match:
                return match.group(1).strip()[:80]
    for line in lines:
        value = line.strip()
        if value and not value.startswith("#"):
            return value[:80]
    return "<empty>"


def _cell_defs(cell: Cell) -> list[str]:
    names: list[str] = []
    for line in cell.source.splitlines():
        match = re.match(r"^\s*(?:def|class)\s+(\w+)", line)
        if match:
            names.append(match.group(1))
    return names


def _bounded_text(text: str, max_lines: int) -> str:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text.rstrip()
    remaining = len(lines) - max_lines
    return "\n".join(lines[:max_lines]) + f"\n… truncated: {remaining} more lines; use --max-lines or a narrower anchor"


def render_toc(path: Path) -> str:
    if path.suffix.lower() == ".ipynb":
        output: list[str] = []
        for cell in notebook_cells(path):
            json_range = f"{cell.json_start}-{cell.json_end}" if cell.json_start is not None else "unknown"
            names = ", ".join(_cell_defs(cell)) or "none"
            output.append(
                f"[{cell.index}] {cell.cell_type} id={cell.id} json={json_range} "
                f"lines={len(cell.source.splitlines())} | {_cell_label(cell)} | defs: {names}"
            )
        return "\n".join(output)
    if path.suffix.lower() == ".md":
        return "\n".join(
            f"{'#' * heading.level} {heading.title} | L{heading.start}-L{heading.end}"
            for heading in markdown_toc(path.read_text(encoding="utf-8"))
        )
    fail("toc supports only .md and .ipynb files")


def _cell_banner(cell: Cell) -> str:
    json_range = f"{cell.json_start}-{cell.json_end}" if cell.json_start is not None else "unknown"
    return f"# --- cell {cell.index} id={cell.id} type={cell.cell_type} json={json_range} ---"


def render_show(path: Path, anchor: str, max_lines: int = 400) -> str:
    if max_lines < 1:
        fail("--max-lines must be positive")
    if path.suffix.lower() == ".md":
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        line_match = re.fullmatch(r"L(\d+)-L(\d+)", anchor, re.IGNORECASE)
        if line_match:
            start, end = map(int, line_match.groups())
            if start < 1 or end < start or end > len(lines):
                fail(f"Invalid line range {anchor!r} for {path.as_posix()}")
            return _bounded_text("\n".join(lines[start - 1:end]), max_lines)
        matches = [
            heading for heading in markdown_toc(text)
            if heading.title.casefold().startswith(anchor.casefold())
        ]
        if not matches:
            fail(f"No Markdown heading matches {anchor!r}")
        if len(matches) > 1:
            candidates = ", ".join(f"{item.title} (L{item.start})" for item in matches)
            fail(f"Ambiguous Markdown heading {anchor!r}: {candidates}")
        heading = matches[0]
        return _bounded_text("\n".join(lines[heading.start - 1:heading.end]), max_lines)
    if path.suffix.lower() != ".ipynb":
        fail("show supports only .md and .ipynb files")
    cells = notebook_cells(path)
    selected: list[Cell] = []
    if match := re.fullmatch(r"cell:(\d+)(?:-(\d+))?", anchor, re.IGNORECASE):
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if start < 0 or end < start or end >= len(cells):
            fail(f"Invalid cell range {anchor!r}")
        selected = cells[start:end + 1]
    elif anchor.lower().startswith("id:"):
        cell_id = anchor[3:]
        selected = [cell for cell in cells if cell.id == cell_id]
        if not selected:
            fail(f"No notebook cell has id {cell_id!r}")
    elif anchor.lower().startswith("def:"):
        name = anchor[4:]
        selected = [
            cell for cell in cells
            if re.search(rf"^\s*def\s+{re.escape(name)}\s*\(", cell.source, re.MULTILINE)
        ]
        if not selected:
            fail(f"No notebook cell defines {name!r}")
    elif anchor.lower().startswith("grep:"):
        pattern_text = anchor[5:]
        try:
            pattern = re.compile(pattern_text)
        except re.error as exc:
            fail(f"Invalid grep regex: {exc}")
        output: list[str] = []
        seen: set[tuple[int, int]] = set()
        for cell in cells:
            source_lines = cell.source.splitlines()
            for line_index, line in enumerate(source_lines):
                if not pattern.search(line):
                    continue
                for context_index in range(max(0, line_index - 1), min(len(source_lines), line_index + 2)):
                    key = (cell.index, context_index)
                    if key not in seen:
                        output.append(f"cell {cell.index} line {context_index + 1}: {source_lines[context_index]}")
                        seen.add(key)
        return _bounded_text("\n".join(output) if output else "no matches", max_lines)
    else:
        fail(f"Unsupported notebook anchor: {anchor!r}")
    rendered = "\n".join(f"{_cell_banner(cell)}\n{cell.source.rstrip()}" for cell in selected)
    return _bounded_text(rendered, max_lines)


def load_state(path: Path) -> dict[str, Any]:
    require_yaml()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"Cannot parse {path.as_posix()}: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.as_posix()} must contain a YAML mapping.")
    return data


def write_state(path: Path, data: dict[str, Any]) -> None:
    require_yaml()
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def get_mapping(data: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key} must be a mapping")
        return {}
    return value


def review_round_cap(state: dict[str, Any]) -> int:
    """Two review rounds, or three when the user approved one extra round for this task."""
    review_plan = state.get("review_plan")
    approved = review_plan.get("extra_round_approved_on") if isinstance(review_plan, dict) else None
    if approved is None:
        return 2
    try:
        if not isinstance(approved, str):
            raise ValueError
        dt.date.fromisoformat(approved)
    except ValueError:
        return 2
    return 3


def validate_state_data(data: dict[str, Any], expected_id: str) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    task = get_mapping(data, "task", errors)
    classification = get_mapping(data, "classification", errors)
    scope = get_mapping(data, "scope", errors)
    review_plan = get_mapping(data, "review_plan", errors)
    models = get_mapping(data, "models", errors)
    gates = get_mapping(data, "gates", errors)
    rounds = get_mapping(data, "rounds", errors)

    if task.get("id") != expected_id:
        errors.append(f"task.id must equal {expected_id!r}")
    status = task.get("status")
    if status not in STATUSES:
        errors.append(f"task.status must be one of {sorted(STATUSES)}")
    if task.get("owner") not in {"main", "architect", "review", "user"}:
        errors.append("task.owner must be main, architect, review, or user")

    if classification.get("complexity") not in {"low", "medium", "high"}:
        errors.append("classification.complexity must be low, medium, or high")
    risk = classification.get("risk_level")
    if risk not in {"low", "medium", "high", "critical"}:
        errors.append("classification.risk_level must be low, medium, high, or critical")
    for key in ("architecture_required", "evidence_required", "runtime_required"):
        if not isinstance(classification.get(key), bool):
            errors.append(f"classification.{key} must be boolean")
    signals = classification.get("signals")
    if not isinstance(signals, list):
        errors.append("classification.signals must be a list")
        signals = []
    unknown_signals = sorted(set(signals) - SIGNALS)
    if unknown_signals:
        errors.append(f"unknown classification signals: {', '.join(unknown_signals)}")
    if len(signals) != len(set(signals)):
        errors.append("classification.signals contains duplicates")

    for key in ("systems", "files"):
        if not isinstance(scope.get(key), list):
            errors.append(f"scope.{key} must be a list")
    required_reviewers = review_plan.get("required_reviewers")
    if not isinstance(required_reviewers, list):
        errors.append("review_plan.required_reviewers must be a list")
        required_reviewers = []
    unknown_reviewers = sorted(set(required_reviewers) - REVIEWERS)
    if unknown_reviewers:
        errors.append(f"unknown reviewers: {', '.join(unknown_reviewers)}")
    if len(required_reviewers) != len(set(required_reviewers)):
        errors.append("review_plan.required_reviewers contains duplicates")
    approved_extra_round = review_plan.get("extra_round_approved_on")
    if approved_extra_round is not None:
        try:
            if not isinstance(approved_extra_round, str):
                raise ValueError
            dt.date.fromisoformat(approved_extra_round)
        except ValueError:
            errors.append("review_plan.extra_round_approved_on must be an ISO date")
    review_cap = review_round_cap(data)
    if review_plan.get("round") not in set(range(review_cap + 1)):
        errors.append(f"review_plan.round must be 0 through {review_cap}")

    expected_models = {
        "main": "grok-4.7", "architect": "claude-opus-5-5",
        "review": "gpt-5.6-sol",
    }
    exceptions = data.get("exceptions", [])
    valid_overrides: dict[str, set[str]] = {}
    if not isinstance(exceptions, list):
        errors.append("exceptions must be a list")
        exceptions = []
    exception_ids: set[str] = set()
    exception_keys = {
        "id", "kind", "role", "model", "effort", "runtime",
        "approved_by", "approved_on", "scope",
    }
    for index, exception in enumerate(exceptions):
        prefix = f"exceptions[{index}]"
        if not isinstance(exception, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        missing = exception_keys - set(exception)
        extra = set(exception) - exception_keys
        if missing:
            errors.append(f"{prefix} missing keys: {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"{prefix} unknown keys: {', '.join(sorted(extra))}")
        exception_id = exception.get("id")
        if not isinstance(exception_id, str) or not exception_id.strip():
            errors.append(f"{prefix}.id must be a non-empty string")
        elif exception_id in exception_ids:
            errors.append(f"{prefix}.id must be unique")
        else:
            exception_ids.add(exception_id)
        if exception.get("kind") != "model_override":
            errors.append(f"{prefix}.kind must be 'model_override'")
        role = exception.get("role")
        if role not in EXCEPTION_ROLES:
            errors.append(f"{prefix}.role must be one of {sorted(EXCEPTION_ROLES)}")
        model_name = exception.get("model")
        if not isinstance(model_name, str) or not model_name.strip():
            errors.append(f"{prefix}.model must be a non-empty string")
        if exception.get("effort") not in {"low", "medium", "high"}:
            errors.append(f"{prefix}.effort must be low, medium, or high")
        if not isinstance(exception.get("runtime"), str) or not exception.get("runtime", "").strip():
            errors.append(f"{prefix}.runtime must be a non-empty string")
        if exception.get("approved_by") != "user":
            errors.append(f"{prefix}.approved_by must be 'user'")
        approved_on = exception.get("approved_on")
        try:
            if not isinstance(approved_on, str):
                raise ValueError
            dt.date.fromisoformat(approved_on)
        except ValueError:
            errors.append(f"{prefix}.approved_on must be an ISO date")
        if not isinstance(exception.get("scope"), str) or not exception.get("scope", "").strip():
            errors.append(f"{prefix}.scope must be a non-empty string")
        if (
            exception.get("kind") == "model_override"
            and role in EXCEPTION_ROLES
            and isinstance(model_name, str) and model_name.strip()
        ):
            valid_overrides.setdefault(role, set()).add(model_name)
    for role, expected in expected_models.items():
        model = models.get(role)
        if not isinstance(model, dict):
            errors.append(f"models.{role} must be a mapping")
            continue
        if model.get("expected") != expected:
            errors.append(f"models.{role}.expected must be {expected!r}")
        expected_effort = "high" if role == "architect" else "medium"
        if model.get("effort") != expected_effort:
            errors.append(f"models.{role}.effort must be {expected_effort!r}")
        if not isinstance(model.get("actual"), str):
            errors.append(f"models.{role}.actual must be a string")
    for key, effort in agent_runner.AUTHOR_LANE_EFFORTS.items():
        if key not in models:
            continue
        author = models[key]
        if not isinstance(author, dict):
            errors.append(f"models.{key} must be a mapping")
            continue
        expected_author_keys = {"expected", "effort", "actual"}
        missing = expected_author_keys - set(author)
        extra = set(author) - expected_author_keys
        if missing:
            errors.append(f"models.{key} missing keys: {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"models.{key} unknown keys: {', '.join(sorted(extra))}")
        if author.get("expected") != agent_runner.AUTHOR_MODEL:
            errors.append(f"models.{key}.expected must be {agent_runner.AUTHOR_MODEL!r}")
        if author.get("effort") != effort:
            errors.append(f"models.{key}.effort must be {effort!r}")
        author_actual = author.get("actual")
        if not isinstance(author_actual, str):
            errors.append(f"models.{key}.actual must be a string")
        elif author_actual and author_actual not in {
            agent_runner.AUTHOR_MODEL, *valid_overrides.get(key, set()),
        }:
            errors.append(
                f"models.{key}.actual must be {agent_runner.AUTHOR_MODEL!r} or an approved {key} override"
            )

    required_actual_models = {"main"}
    if gates.get("architecture") == "pass":
        required_actual_models.add("architect")
    if gates.get("specialist_review") == "pass" or gates.get("risk_gate") == "pass":
        required_actual_models.add("review")
    if status in {"triage", "waiting_evidence", "waiting_architecture"}:
        required_actual_models.discard("main")
    for role in required_actual_models:
        model = models.get(role)
        allowed_actuals = {expected_models[role], *valid_overrides.get(role, set())}
        if isinstance(model, dict) and model.get("actual") not in allowed_actuals:
            errors.append(f"models.{role}.actual must confirm {expected_models[role]!r} before this gate/status")

    missing_gates = GATE_NAMES - set(gates)
    extra_gates = set(gates) - GATE_NAMES
    if missing_gates:
        errors.append(f"missing gates: {', '.join(sorted(missing_gates))}")
    if extra_gates:
        errors.append(f"unknown gates: {', '.join(sorted(extra_gates))}")
    for name, result in gates.items():
        if result not in GATE_RESULTS:
            errors.append(f"gates.{name} must be one of {sorted(GATE_RESULTS)}")
    requirements = {
        "evidence": bool(classification.get("evidence_required")),
        "architecture": bool(classification.get("architecture_required")),
        "runtime": bool(classification.get("runtime_required")),
        "specialist_review": bool(required_reviewers),
        "risk_gate": risk in {"high", "critical"},
    }
    for gate, required in requirements.items():
        result = gates.get(gate)
        if required and result == "not_required":
            errors.append(f"gates.{gate} cannot be not_required for this classification")
        if not required and result not in {"not_required", "pending"}:
            errors.append(f"gates.{gate} must be not_required or pending when not required")

    round_limits = {"verification": 2, "review": review_round_cap(data), "architecture": 2, "runtime_failure": 2}
    for name, limit in round_limits.items():
        value = rounds.get(name)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"rounds.{name} must be a non-negative integer")
        elif value > limit:
            errors.append(f"rounds.{name} exceeds cap {limit}")

    findings = data.get("open_findings")
    if not isinstance(findings, list):
        errors.append("open_findings must be a list")
        findings = []
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            errors.append(f"open_findings[{index}] must be a mapping")
            continue
        if finding.get("severity") not in {"P0", "P1", "P2", "P3"}:
            errors.append(f"open_findings[{index}].severity is invalid")
        if not finding.get("id"):
            errors.append(f"open_findings[{index}].id is required")

    if status == "ready_to_merge":
        for name, result in gates.items():
            if result not in {"pass", "not_required"}:
                errors.append(f"ready_to_merge requires gates.{name} to pass or be not_required")
        blocking = [
            finding.get("id", "<unknown>") for finding in findings
            if isinstance(finding, dict) and finding.get("severity") in {"P0", "P1"}
        ]
        if blocking:
            errors.append(f"ready_to_merge has blocking findings: {', '.join(blocking)}")
    return errors


def validate_task(task_id: str) -> list[str]:
    path = task_dir(task_id) / "task-state.yaml"
    if not path.is_file():
        return [f"missing {path.as_posix()}"]
    return validate_state_data(load_state(path), task_id)


PHASE_BY_STATUS = {
    "triage": "triage", "waiting_architecture": "triage",
    "waiting_evidence": "evidence", "reviewing": "review",
    "waiting_runtime": "runtime", "user_decision": "closeout",
    "ready_to_merge": "closeout", "blocked": "closeout",
}


def _markdown_section(text: str, title: str) -> str | None:
    matches = [item for item in markdown_toc(text) if item.title.casefold() == title.casefold()]
    if not matches:
        return None
    lines = text.splitlines()
    item = matches[0]
    return "\n".join(lines[item.start - 1:item.end]).rstrip()


def _markdown_sections(text: str, titles: list[str]) -> str:
    return "\n\n".join(section for title in titles if (section := _markdown_section(text, title)))


def _context_phase(state: dict[str, Any], requested: str) -> str:
    if requested != "auto":
        return requested
    status = state["task"]["status"]
    if status in {"implementing", "verifying"}:
        has_blocker = any(
            isinstance(item, dict) and item.get("severity") in {"P0", "P1"}
            for item in state.get("open_findings", [])
        )
        return "remediate" if state["rounds"]["review"] > 0 and has_blocker else "implement"
    return PHASE_BY_STATUS[status]


def _template_equivalent(path: Path, task_id: str, created_at: str) -> bool:
    directory = task_dir(task_id)
    try:
        relative = path.relative_to(directory)
    except ValueError:
        return False
    template = TEMPLATE_ROOT / relative
    if not template.is_file():
        return False
    try:
        expected = template.read_text(encoding="utf-8")
        expected = expected.replace("{{TASK_ID}}", task_id).replace("{{DATE}}", created_at)
        return path.read_text(encoding="utf-8") == expected
    except UnicodeDecodeError:
        return path.read_bytes() == template.read_bytes()


def _state_context(state: dict[str, Any]) -> str:
    task = state["task"]
    classification = state["classification"]
    gates = ", ".join(f"{key}={value}" for key, value in state["gates"].items())
    rounds = ", ".join(f"{key}={value}" for key, value in state["rounds"].items())
    findings = ", ".join(
        f"{item.get('id')} {item.get('severity')}"
        for item in state.get("open_findings", []) if isinstance(item, dict)
    ) or "none"
    exceptions = ", ".join(
        f"{item.get('id')} {item.get('role')} {item.get('model')} {item.get('effort')} {item.get('approved_on')}"
        for item in state.get("exceptions", []) if isinstance(item, dict)
    ) or "none"
    files = list(state["scope"].get("files", []))
    file_lines = [f"- {path}" for path in files[:30]]
    if len(files) > 30:
        file_lines.append(f"- +{len(files) - 30} more")
    return "\n".join([
        f"id: {task['id']}",
        f"title: {task.get('title', '')}",
        f"status/owner: {task['status']}/{task['owner']}",
        f"complexity/risk: {classification['complexity']}/{classification['risk_level']}",
        "required: " + ", ".join(
            f"{key}={classification[key]}"
            for key in ("architecture_required", "evidence_required", "runtime_required")
        ),
        f"signals: {', '.join(classification.get('signals', [])) or 'none'}",
        f"gates: {gates}",
        f"rounds: {rounds}",
        f"reviewers: {', '.join(state['review_plan'].get('required_reviewers', [])) or 'none'}",
        f"open findings: {findings}",
        f"exceptions: {exceptions}",
        "scope.files:",
        *file_lines,
    ])


def _architecture_summary(directory: Path, phase: str) -> str:
    path = directory / "architecture.md"
    if not path.is_file():
        return "missing architecture.md"
    text = path.read_text(encoding="utf-8")
    result = next((line for line in text.splitlines() if line.strip().startswith("RESULT:")), "RESULT: missing")
    if phase not in {"implement", "remediate", "review", "runtime"}:
        return f"{result}\nsize: {path.stat().st_size} bytes"
    brief = _markdown_section(text, "Main brief")
    if brief:
        return brief
    toc = render_toc(path)
    return f"no Main brief\n{toc}"


def _evidence_context(directory: Path) -> str:
    probe_dir = directory / "evidence" / "probes"
    result_dir = directory / "evidence" / "results"
    if not probe_dir.is_dir():
        return "no probes"
    groups: dict[str, list[Path]] = {}
    for path in sorted(probe_dir.iterdir()):
        if path.is_file() and path.name != "README.md":
            groups.setdefault(path.stem, []).append(path)
    output: list[str] = []
    for stem, paths in groups.items():
        results = sorted(result_dir.glob(f"{stem}.*")) if result_dir.is_dir() else []
        result = results[0].as_posix() if results else "NO RESULT"
        output.append(f"- {stem}: {', '.join(path.as_posix() for path in paths)} | result: {result}")
    return "\n".join(output) or "no probes"


def _remediation_context(directory: Path) -> str:
    review_dir = directory / "reviews"
    candidates: list[tuple[int, Path]] = []
    if review_dir.is_dir():
        for path in review_dir.glob("round-*.md"):
            match = re.fullmatch(r"round-(\d+)\.md", path.name)
            if match:
                candidates.append((int(match.group(1)), path))
    if not candidates:
        return "no review rounds"
    path = max(candidates)[1]
    lines = path.read_text(encoding="utf-8").splitlines()
    selected: list[str] = [f"source: {path.as_posix()}"]
    selected.extend(line for line in lines if re.match(r"^\|", line) and ("Severity" in line or re.search(r"\bP[01]\b", line)))
    return "\n".join(selected)


def _runtime_context(directory: Path) -> str:
    path = directory / "runtime-runbook.md"
    if not path.is_file():
        return "missing runtime-runbook.md"
    text = path.read_text(encoding="utf-8")
    result = [render_toc(path)]
    section = _markdown_section(text, "Kết quả người dùng ghi nhận")
    if section:
        result.append(section)
    return "\n\n".join(result)


def _next_context(task_id: str, status: str) -> str:
    commands = {
        "triage": f"python scripts/vv.py transition {task_id} <next-status>",
        "waiting_evidence": f"interpret results, then python scripts/vv.py transition {task_id} <next-status>",
        "waiting_architecture": f"python scripts/vv.py run-gate {task_id}",
        "implementing": f"implement, then python scripts/vv.py transition {task_id} verifying",
        "verifying": f"python scripts/vv.py verify {task_id}",
        "reviewing": f"python scripts/vv.py run-gate {task_id}",
        "waiting_runtime": f"python scripts/vv.py closeout {task_id}",
        "user_decision": "wait for the named user decision",
        "ready_to_merge": "user commit/merge only",
        "blocked": "resolve the named blocker",
    }
    return commands[status]


def build_context(task_id: str, phase: str = "auto", max_lines: int = 400) -> str:
    directory = task_dir(task_id)
    state = load_state(directory / "task-state.yaml")
    selected_phase = _context_phase(state, phase)
    allowed_phases = {"triage", "evidence", "implement", "remediate", "review", "runtime", "closeout"}
    if selected_phase not in allowed_phases:
        fail(f"Unknown context phase: {selected_phase!r}")
    blocks: list[tuple[str, str]] = [("STATE", _state_context(state))]
    validation = validate_state_data(state, task_id)
    blocks.append(("VALIDATION", "PASS" if not validation else "\n".join(f"- {item}" for item in validation)))

    resume = directory / "resume.md"
    if resume.is_file():
        text = resume.read_text(encoding="utf-8")
        created_at = str(state["task"].get("created_at", ""))
        if "{{" not in text and text.strip() and not _template_equivalent(resume, task_id, created_at):
            blocks.append(("RESUME", "\n".join(text.splitlines()[:60])))

    request_path = directory / "request.md"
    request_text = request_path.read_text(encoding="utf-8") if request_path.is_file() else ""
    request = request_text if selected_phase == "triage" else _markdown_sections(
        request_text, ["User outcome", "Acceptance criteria", "Constraints"],
    )
    blocks.append(("REQUEST", request or "missing request sections"))

    decision_path = directory / "decision.md"
    decision_text = decision_path.read_text(encoding="utf-8") if decision_path.is_file() else ""
    ledger = _markdown_section(decision_text, "Quyết định hiện hành")
    finding_table = _markdown_section(decision_text, "Xử lý findings")
    if ledger:
        decisions = "\n\n".join(part for part in (ledger, finding_table) if part)
    else:
        decisions = "no ledger\n" + (render_toc(decision_path) if decision_path.is_file() else "missing decision.md")
    blocks.append(("DECISIONS", decisions))
    blocks.append(("ARCHITECTURE", _architecture_summary(directory, selected_phase)))

    if selected_phase == "evidence":
        blocks.append(("EVIDENCE", _evidence_context(directory)))
    if selected_phase == "remediate":
        blocks.append(("REMEDIATION", _remediation_context(directory)))
    if selected_phase in {"runtime", "closeout"}:
        blocks.append(("RUNTIME", _runtime_context(directory)))

    task_files: list[str] = []
    created_at = str(state["task"].get("created_at", ""))
    for path in sorted(item for item in directory.rglob("*") if item.is_file()):
        relative = path.relative_to(directory).as_posix()
        labels: list[str] = []
        if _template_equivalent(path, task_id, created_at):
            labels.append("placeholder")
        if path.stat().st_size > 20 * 1024:
            labels.append("large: use toc/show")
        suffix = f" | {', '.join(labels)}" if labels else ""
        task_files.append(f"- {relative} | {path.stat().st_size} bytes{suffix}")
    blocks.append(("FILES", "\n".join(task_files) or "none"))
    blocks.append(("NEXT", _next_context(task_id, state["task"]["status"])))
    output = f"# Context {task_id} | phase={selected_phase}\n\n" + "\n\n".join(
        f"## {title}\n\n{content}" for title, content in blocks
    )
    return _bounded_text(output, max_lines)


def cmd_new(args: argparse.Namespace) -> int:
    slug = re.sub(r"[^a-z0-9-]+", "-", args.slug.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not slug:
        fail("Slug is empty after normalization.")
    task_id = f"{dt.date.today():%Y%m%d}-{slug}"
    destination = task_dir(task_id, must_exist=False)
    if destination.exists():
        fail(f"Task already exists: {destination}")
    if not TEMPLATE_ROOT.is_dir():
        fail(f"Template directory not found: {TEMPLATE_ROOT.as_posix()}")
    shutil.copytree(TEMPLATE_ROOT, destination)
    for directory in ("evidence/results", "verification", "handoffs"):
        (destination / directory).mkdir(parents=True, exist_ok=True)
    replacements = {"{{TASK_ID}}": task_id, "{{DATE}}": dt.date.today().isoformat()}
    for path in destination.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for old, new in replacements.items():
                text = text.replace(old, new)
            path.write_text(text, encoding="utf-8")
    errors = validate_task(task_id)
    if errors:
        fail("Created task is invalid:\n- " + "\n- ".join(errors))
    print(task_id)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    if args.all:
        task_ids = sorted(path.name for path in TASKS_ROOT.iterdir() if path.is_dir() and path.name != "_template")
    elif args.task:
        task_ids = [args.task]
    else:
        fail("Provide a task ID or --all.")
    failures = 0
    for task_id in task_ids:
        errors = validate_task(task_id)
        print(f"{task_id}: {'FAIL' if errors else 'PASS'}")
        for error in errors:
            print(f"  - {error}")
        failures += bool(errors)
    if not task_ids:
        print("No task instances found.")
    return 1 if failures else 0


def cmd_transition(args: argparse.Namespace) -> int:
    path = task_dir(args.task) / "task-state.yaml"
    state = load_state(path)
    errors = validate_state_data(state, args.task)
    if errors:
        fail("Current task state is invalid:\n- " + "\n- ".join(errors))
    current = state["task"]["status"]
    if args.status not in TRANSITIONS[current]:
        fail(f"Invalid transition: {current} -> {args.status}")
    state["task"]["status"] = args.status
    state["task"]["owner"] = OWNER_BY_STATUS.get(args.status, "main")
    state["task"]["updated_at"] = dt.date.today().isoformat()
    candidate_errors = validate_state_data(state, args.task)
    if candidate_errors:
        fail("Requested transition would create invalid state:\n- " + "\n- ".join(candidate_errors))
    write_state(path, state)
    print(f"{args.task}: {current} -> {args.status}")
    return 0


def _architect_appendix(task_id: str, state: dict[str, Any]) -> str:
    parts = [
        "## Generated context pack",
        "",
        "`vv.py` generated this block. Do not re-read the task state, request, decision ledger, or task file list it covers.",
        "",
        build_context(task_id, phase="triage"),
    ]
    tocs: list[str] = []
    for value in state["scope"].get("files", []):
        path = Path(str(value).replace("\\", "/"))
        if path.suffix.lower() not in {".md", ".ipynb"} or not path.is_file() or path.stat().st_size <= 20 * 1024:
            continue
        try:
            toc = render_toc(path)
        except (SystemExit, ValueError):
            continue
        tocs.append(
            f"### {path.as_posix()} ({path.stat().st_size} bytes)\n\n"
            f"{_bounded_text(toc, ARCHITECT_TOC_MAX_LINES)}"
        )
    if tocs:
        parts.extend([
            "",
            "## Large scope files",
            "",
            "Read these narrowly: `Read` with `offset`/`limit` for a Markdown line range; `Grep` with context for a "
            "notebook function name or cell id.",
            "",
            "\n\n".join(tocs),
        ])
    return "\n".join(parts)


def _review_files(task_id: str, state: dict[str, Any]) -> list[str]:
    task_prefix = f".ai/tasks/{task_id}/"
    return [path for path in _scoped_status_files(task_id, state) if not path.startswith(task_prefix)]


def _file_digest(path: str) -> str | None:
    target = Path(path)
    return hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None


def _finding_excerpts(text: str, finding_ids: list[str]) -> list[str]:
    """Return the headed sections or list/table rows that mention each finding ID."""
    lines = text.splitlines()
    headings = markdown_toc(text)
    excerpts: list[str] = []
    emitted_headers: set[int] = set()
    for finding_id in finding_ids:
        pattern = re.compile(rf"(?<![\w-]){re.escape(finding_id)}(?![\w-])")
        heading = next((item for item in headings if pattern.search(item.title)), None)
        if heading:
            excerpts.append("\n".join(lines[heading.start - 1:heading.end]).rstrip())
            continue
        rows = [index for index, line in enumerate(lines) if line.lstrip().startswith(("|", "-", "*")) and pattern.search(line)]
        if not rows:
            excerpts.append(f"- {finding_id}: no details found")
        for index in rows:
            start = index
            while start > 0 and lines[start - 1].lstrip().startswith("|"):
                start -= 1
            if lines[index].lstrip().startswith("|") and start < index - 1 and start not in emitted_headers:
                emitted_headers.add(start)
                excerpts.append("\n".join(lines[start:start + 2]))
            excerpts.append(lines[index])
    return excerpts


def _review_appendix(task_id: str, state: dict[str, Any], round_number: int) -> str:
    directory = task_dir(task_id)
    previous = round_number - 1
    snapshot_path = directory / "reviews" / f"round-{previous}.json"
    report_path = directory / "reviews" / f"round-{previous}.md"
    snapshot: dict[str, Any] = {}
    if snapshot_path.is_file():
        try:
            loaded = json.loads(snapshot_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            loaded = {}
        snapshot = loaded if isinstance(loaded, dict) else {}
    report = report_path.read_text(encoding="utf-8") if report_path.is_file() else ""

    finding_ids: list[str] = []
    for item in [*snapshot.get("findings", []), *state.get("open_findings", [])]:
        if isinstance(item, dict) and item.get("severity") in {"P0", "P1"} and str(item.get("id")) not in finding_ids:
            finding_ids.append(str(item.get("id")))
    if not finding_ids:
        for line in report.splitlines():
            if re.search(r"\bP[01]\b", line):
                finding_ids.extend(item for item in FINDING_ID_RE.findall(line) if item not in finding_ids)

    if finding_ids and report:
        findings = "\n".join(_finding_excerpts(report, finding_ids))
    elif finding_ids:
        findings = "\n".join(f"- {item}: missing {report_path.as_posix()}" for item in finding_ids)
    else:
        findings = "none recorded"

    decision_path = directory / "decision.md"
    decision_text = decision_path.read_text(encoding="utf-8") if decision_path.is_file() else ""
    section = _markdown_section(decision_text, "Xử lý findings") or ""
    dispositions = "\n".join(_finding_excerpts(section, finding_ids)) if section and finding_ids else ""

    files = snapshot.get("files")
    if isinstance(files, dict):
        changed: list[str] = []
        for path in sorted(set(files) | set(_review_files(task_id, state))):
            current = _file_digest(path)
            if path not in files:
                changed.append(f"- {path} | entered the diff after round {previous}")
            elif current != files[path]:
                label = "deleted" if current is None else "re-created" if files[path] is None else "modified"
                changed.append(f"- {path} | {label}")
        changed_text = "\n".join(changed) or f"none: no scoped file changed since round {previous}"
    else:
        changed_text = (
            f"No round-{previous} snapshot ({snapshot_path.as_posix()}). Review the full implementation diff, "
            "including untracked files from `git status --untracked-files=all`."
        )

    output = "\n".join([
        f"## Round {previous} carry-over",
        "",
        f"`vv.py` generated this block. Use it instead of opening past review files. Re-check each round-{previous} "
        "P0/P1 against its disposition, then review only the changed files below for regressions caused by the fixes.",
        "",
        f"### Round {previous} P0/P1 findings",
        "",
        findings,
        "",
        "### Dispositions in decision.md",
        "",
        dispositions or "missing: no `Xử lý findings` row mentions these IDs",
        "",
        f"### Files changed since round {previous}",
        "",
        changed_text,
    ])
    return _bounded_text(output, REVIEW_CARRY_MAX_LINES)


def render_prompt(task_id: str, target: str, round_number: int = 1) -> tuple[Path, str]:
    directory = task_dir(task_id)
    template = Path(".ai/prompts") / PROMPTS[target]
    if not template.is_file():
        fail(f"Prompt template not found: {template.as_posix()}")
    if target == "review":
        cap = review_round_cap(load_state(directory / "task-state.yaml"))
        if round_number not in set(range(1, cap + 1)):
            fail(f"Review round must be 1 through {cap}.")
    text = template.read_text(encoding="utf-8")
    text = text.replace("{{TASK_ID}}", task_id).replace("{{ROUND}}", str(round_number))
    if target == "architect":
        state = load_state(directory / "task-state.yaml")
        text = text.rstrip() + "\n\n" + _architect_appendix(task_id, state) + "\n"
    elif round_number >= 2:
        state = load_state(directory / "task-state.yaml")
        text = text.rstrip() + "\n\n" + _review_appendix(task_id, state, round_number) + "\n"
    name = "architect.md" if target == "architect" else f"review-round-{round_number}.md"
    output = directory / "handoffs" / name
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    return output, text


def cmd_prompt(args: argparse.Namespace) -> int:
    output, _ = render_prompt(args.task, args.target, args.round)
    print(output.as_posix())
    return 0


def _set_task_status(state: dict[str, Any], status: str) -> None:
    state["task"]["status"] = status
    state["task"]["owner"] = OWNER_BY_STATUS.get(status, "main")
    state["task"]["updated_at"] = dt.date.today().isoformat()


def architecture_state_after(state: dict[str, Any], verdict: str) -> dict[str, Any]:
    candidate = copy.deepcopy(state)
    candidate["models"]["architect"]["actual"] = agent_runner.ARCHITECT_MODEL
    candidate["rounds"]["architecture"] += 1
    if verdict == "PASS":
        candidate["gates"]["architecture"] = "pass"
        _set_task_status(candidate, "implementing")
    elif verdict == "EVIDENCE_REQUIRED":
        candidate["classification"]["evidence_required"] = True
        candidate["gates"]["evidence"] = "evidence_required"
        candidate["gates"]["architecture"] = "evidence_required"
        _set_task_status(candidate, "waiting_evidence")
    else:
        fail(f"Unsupported architecture verdict: {verdict}")
    return candidate


def review_state_after(
    state: dict[str, Any], result: agent_runner.ReviewResult, round_number: int,
) -> dict[str, Any]:
    candidate = copy.deepcopy(state)
    candidate["models"]["review"]["actual"] = agent_runner.REVIEW_MODEL
    candidate["review_plan"]["round"] = round_number
    candidate["rounds"]["review"] = round_number
    candidate["open_findings"] = [dict(item) for item in result.findings]
    gate_result = {
        "PASS": "pass",
        "FIX_REQUIRED": "fix_required",
        "EVIDENCE_REQUIRED": "evidence_required",
        "USER_DECISION": "user_decision",
    }[result.verdict]
    required_reviewers = candidate["review_plan"]["required_reviewers"]
    risk_required = candidate["classification"]["risk_level"] in {"high", "critical"}
    candidate["gates"]["specialist_review"] = gate_result if required_reviewers else "not_required"
    candidate["gates"]["risk_gate"] = gate_result if risk_required else "not_required"
    if result.verdict == "PASS":
        if candidate["classification"]["runtime_required"]:
            _set_task_status(candidate, "waiting_runtime")
        else:
            _set_task_status(candidate, "user_decision")
    elif result.verdict == "FIX_REQUIRED":
        _set_task_status(candidate, "implementing")
    elif result.verdict == "EVIDENCE_REQUIRED":
        candidate["classification"]["evidence_required"] = True
        candidate["gates"]["evidence"] = "evidence_required"
        _set_task_status(candidate, "waiting_evidence")
    else:
        _set_task_status(candidate, "user_decision")
    return candidate


def _validate_candidate_state(task_id: str, state: dict[str, Any]) -> None:
    errors = validate_state_data(state, task_id)
    if errors:
        fail("Automated gate produced invalid task state:\n- " + "\n- ".join(errors))


def cmd_external_doctor(args: argparse.Namespace) -> int:
    try:
        details = agent_runner.external_preflight(repo_root(), timeout_seconds=args.timeout)
    except agent_runner.RunnerError as exc:
        fail(f"EXTERNAL DOCTOR FAIL: {exc}")
    print("EXTERNAL DOCTOR PASS")
    for key, value in details.items():
        print(f"{key}: {value}")
    return 0


def cmd_external_smoke(args: argparse.Namespace) -> int:
    repo = repo_root()
    try:
        details = agent_runner.external_preflight(repo, timeout_seconds=min(args.timeout, 60))
        architecture_prompt = """# Automated Architect smoke test

Follow AGENTS.md as the VSVN Architect. Analyze this synthetic scenario only:
the business Delta MERGE commits, the process crashes before watermark update, and the pipeline retries.
Produce a concise architecture document covering transaction boundaries, idempotency, watermark ownership,
retry/recovery, evidence requirements, and verification. Do not edit any repository file.
"""
        architecture = agent_runner.run_architecture(repo, architecture_prompt, timeout_seconds=args.timeout)
        review_prompt = """# Automated Codex multi-agent smoke test

Follow AGENTS.md as the VSVN Review Coordinator. Review this synthetic scenario only:
the business Delta MERGE commits, the process crashes before watermark update, and the pipeline retries.
Invoke state-correctness-reviewer and sql-data-reviewer independently. After both complete, invoke risk-gate.
Do not edit any repository file. The purpose is to validate custom-agent execution and result consolidation.
"""
        review = agent_runner.run_review(
            repo,
            review_prompt,
            ["state-correctness-reviewer", "sql-data-reviewer"],
            True,
            timeout_seconds=args.timeout,
        )
    except agent_runner.RunnerError as exc:
        fail(f"EXTERNAL SMOKE FAIL: {exc}")
    print("EXTERNAL SMOKE PASS")
    print(f"Claude: {details['claude_version']} / architecture verdict {architecture.verdict}")
    print(f"Codex: {details['codex_version']} / review verdict {review.verdict}")
    print(f"Reviewers: {', '.join(review.reviewers_run)}")
    print("Risk gate: run")
    print("Repository changes: none")
    return 0


def cmd_run_gate(args: argparse.Namespace) -> int:
    directory = task_dir(args.task)
    state_path = directory / "task-state.yaml"
    state = load_state(state_path)
    errors = validate_state_data(state, args.task)
    if errors:
        fail("Current task state is invalid:\n- " + "\n- ".join(errors))
    status = state["task"]["status"]
    try:
        if status == "waiting_architecture":
            if not state["classification"]["architecture_required"]:
                fail("Task is waiting_architecture but architecture_required is false.")
            if state["rounds"]["architecture"] >= 2:
                candidate = copy.deepcopy(state)
                candidate["gates"]["architecture"] = "user_decision"
                _set_task_status(candidate, "user_decision")
                _validate_candidate_state(args.task, candidate)
                write_state(state_path, candidate)
                print("Architecture round cap reached; routed task to user_decision.")
                return 0
            if "data_model_change" in state["classification"].get("signals", []):
                design = directory / "model-design.md"
                if not design.is_file() or not design.read_text(encoding="utf-8").strip():
                    fail(
                        "Signal data_model_change requires model-design.md before the Architect runs. "
                        f"Run: python scripts/vv.py run-author {args.task} --kind model"
                    )
            handoff, prompt = render_prompt(args.task, "architect")
            print(f"Running Claude Architect from {handoff.as_posix()}...")
            started = time.monotonic()
            try:
                result = agent_runner.run_architecture(repo_root(), prompt, timeout_seconds=args.timeout)
            finally:
                elapsed_seconds = int(time.monotonic() - started)
                print(f"Elapsed: {elapsed_seconds} s")
            candidate = architecture_state_after(state, result.verdict)
            _validate_candidate_state(args.task, candidate)
            architecture = directory / "architecture.md"
            architecture.write_text(result.document, encoding="utf-8")
            write_state(state_path, candidate)
            print(f"ARCHITECTURE {result.verdict}: {architecture.as_posix()}")
            print(f"Executable: {result.executable}")
            for warning in result.warnings:
                print(f"WARN: {warning}")
            print(f"Next status: {candidate['task']['status']}")
            return 0
        if status == "reviewing":
            if state["gates"]["local_verification"] != "pass":
                fail("Local verification must pass before automated review.")
            review_cap = review_round_cap(state)
            expected_round = state["rounds"]["review"] + 1
            if expected_round > review_cap:
                candidate = copy.deepcopy(state)
                if candidate["review_plan"]["required_reviewers"]:
                    candidate["gates"]["specialist_review"] = "user_decision"
                if candidate["classification"]["risk_level"] in {"high", "critical"}:
                    candidate["gates"]["risk_gate"] = "user_decision"
                _set_task_status(candidate, "user_decision")
                _validate_candidate_state(args.task, candidate)
                write_state(state_path, candidate)
                print("Review round cap reached; routed task to user_decision.")
                return 0
            round_number = args.round if args.round is not None else expected_round
            if round_number != expected_round or round_number not in set(range(1, review_cap + 1)):
                fail(f"Expected review round {expected_round}; received {round_number}.")
            handoff, prompt = render_prompt(args.task, "review", round_number)
            reviewers = list(state["review_plan"]["required_reviewers"])
            risk_required = state["classification"]["risk_level"] in {"high", "critical"}
            reviewed_files = {path: _file_digest(path) for path in _review_files(args.task, state)}
            print(f"Running Codex review from {handoff.as_posix()}...")
            started = time.monotonic()
            try:
                result = agent_runner.run_review(
                    repo_root(), prompt, reviewers, risk_required, timeout_seconds=args.timeout,
                )
            finally:
                elapsed_seconds = int(time.monotonic() - started)
                print(f"Elapsed: {elapsed_seconds} s")
            candidate = review_state_after(state, result, round_number)
            _validate_candidate_state(args.task, candidate)
            review_path = directory / "reviews" / f"round-{round_number}.md"
            review_path.parent.mkdir(parents=True, exist_ok=True)
            review_path.write_text(result.report, encoding="utf-8")
            snapshot = {
                "round": round_number,
                "verdict": result.verdict,
                "findings": [dict(item) for item in result.findings],
                "files": reviewed_files,
                "elapsed_seconds": elapsed_seconds,
            }
            review_path.with_suffix(".json").write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
            write_state(state_path, candidate)
            print(f"REVIEW {result.verdict}: {review_path.as_posix()}")
            print(f"Reviewers: {', '.join(result.reviewers_run) or 'none'}")
            print(f"Risk gate: {'run' if result.risk_gate_run else 'not required'}")
            print(f"Executable: {result.executable}")
            print(f"Next status: {candidate['task']['status']}")
            return 0
    except agent_runner.RunnerError as exc:
        fail(f"AUTOMATED GATE FAIL: {exc}")
    fail(
        f"No automated external gate for status {status!r}. "
        "Use run-gate only for waiting_architecture or reviewing."
    )


def _author_output_path(directory: Path, task_id: str, created_at: str, kind: str) -> tuple[Path, bool]:
    name = AUTHOR_OUTPUTS[kind]
    target = directory / name
    if not target.exists() or _template_equivalent(target, task_id, created_at):
        return target, False
    return target.with_name(f"{target.stem}.new{target.suffix}"), True


def cmd_run_author(args: argparse.Namespace) -> int:
    directory = task_dir(args.task)
    state_path = directory / "task-state.yaml"
    state = load_state(state_path)
    errors = validate_state_data(state, args.task)
    if errors:
        fail("Current task state is invalid:\n- " + "\n- ".join(errors))
    author_input_path = directory / "handoffs" / "author-input.md"
    if not author_input_path.is_file():
        fail(f"Author input not found: {author_input_path.as_posix()}")
    author_input = author_input_path.read_text(encoding="utf-8")
    line_count = len(author_input.splitlines())
    if line_count > 60:
        fail(f"Author input exceeds 60 lines: {line_count}")
    template_path = Path(".ai/prompts") / f"author-{args.kind}.md"
    if not template_path.is_file():
        fail(f"Author prompt template not found: {template_path.as_posix()}")
    prompt = template_path.read_text(encoding="utf-8").replace("{{TASK_ID}}", args.task)
    prompt = f"{prompt.rstrip()}\n\n## Author input\n\n{author_input.rstrip()}\n"
    key = AUTHOR_LANES[args.kind]
    effort = agent_runner.AUTHOR_EFFORTS[args.kind]
    started = time.monotonic()
    try:
        try:
            result = agent_runner.run_author(repo_root(), prompt, args.kind, timeout_seconds=args.timeout)
        finally:
            elapsed_seconds = int(time.monotonic() - started)
            print(f"Elapsed: {elapsed_seconds} s")
    except agent_runner.RunnerError as exc:
        fail(f"AUTHOR FAIL: {exc}")
    candidate = copy.deepcopy(state)
    author = candidate["models"].setdefault(
        key, {"expected": agent_runner.AUTHOR_MODEL, "effort": effort, "actual": ""},
    )
    author["actual"] = agent_runner.AUTHOR_MODEL
    _validate_candidate_state(args.task, candidate)
    output, collision = _author_output_path(
        directory, args.task, str(state["task"].get("created_at", "")), args.kind,
    )
    output.write_text(result.document, encoding="utf-8")
    write_state(state_path, candidate)
    if collision:
        print(f"NOTICE: Existing artifact preserved; Main must merge {output.as_posix()}.")
    print(f"AUTHOR OUTPUT: {output.as_posix()}")
    print(f"Model: {agent_runner.AUTHOR_MODEL} effort {effort}")
    print(f"Lane: models.{key}")
    print(f"Executable: {result.executable}")
    return 0


def changed_files(all_files: bool) -> list[str]:
    if all_files:
        files = set(nul_paths(git("ls-files", "-z").stdout))
    elif git("rev-parse", "--verify", "-q", "HEAD", check=False).returncode == 0:
        files = set(nul_paths(git("diff", "--name-only", "-z", "HEAD").stdout))
    else:
        files = set(nul_paths(git("ls-files", "-z").stdout))
    files |= set(nul_paths(git("ls-files", "--others", "--exclude-standard", "-z").stdout))
    return sorted(path for path in files if not path.startswith(".ai/") and Path(path).is_file())


def parse_file_blocks(data: bytes) -> list[tuple[str, bytes]]:
    """Extract exact FILE and SKILL_FILE block bodies from a byte stream."""
    blocks: list[tuple[str, bytes]] = []
    seen: set[str] = set()
    current_path: str | None = None
    expected_end: bytes | None = None
    body: list[bytes] = []
    for line in data.splitlines(keepends=True):
        stripped = line.rstrip(b"\r\n")
        start = re.fullmatch(rb"(FILE|SKILL_FILE):\s*(.+)", stripped)
        if start:
            if current_path is not None:
                fail(f"Nested file block inside {current_path}")
            current_path = start.group(2).decode("utf-8").strip()
            if current_path in seen:
                fail(f"Duplicate file block: {current_path}")
            seen.add(current_path)
            expected_end = b"END_FILE" if start.group(1) == b"FILE" else b"END_SKILL_FILE"
            body = []
            continue
        if current_path is not None:
            if stripped == expected_end:
                blocks.append((current_path, b"".join(body)))
                current_path = None
                expected_end = None
                body = []
                continue
            if re.fullmatch(rb"(?:FILE|SKILL_FILE):\s*.+", stripped):
                fail(f"Nested file block inside {current_path}")
            body.append(line)
    if current_path is not None:
        fail(f"Unclosed file block: {current_path}")
    return blocks


def _materialize_target(path_text: str, allowed: set[str]) -> Path:
    normalized = path_text.replace("\\", "/")
    path = Path(normalized)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        fail(f"Unsafe materialize path: {path_text!r}")
    template_state = path.parts[:3] == (".ai", "tasks", "_template") and path.name == "task-state.yaml"
    if path.parts[0] == ".git" or (path.name == "task-state.yaml" and not template_state):
        fail(f"Prohibited materialize path: {path_text!r}")
    if normalized not in allowed:
        fail(f"Materialize path is not listed in scope.files: {normalized}")
    return path


def materialize_blocks(task_id: str, source_name: str, write: bool = False) -> list[str]:
    directory = task_dir(task_id)
    if source_name not in {"architecture.md", "proposal.md"}:
        fail("--source must be architecture.md or proposal.md")
    source = directory / source_name
    if not source.is_file():
        fail(f"Materialize source not found: {source.as_posix()}")
    state = load_state(directory / "task-state.yaml")
    allowed = {str(item).replace("\\", "/") for item in state["scope"].get("files", [])}
    planned: list[tuple[Path, bytes, str, str]] = []
    output: list[str] = []
    for path_text, body in parse_file_blocks(source.read_bytes()):
        target = _materialize_target(path_text, allowed)
        status = "new" if not target.exists() else ("identical" if target.read_bytes() == body else "changed")
        digest = hashlib.sha256(body).hexdigest()[:12]
        planned.append((target, body, status, digest))
        output.append(f"{target.as_posix()} | {len(body)} | {digest} | {status}")
    if write and any(status != "identical" for _, _, status, _ in planned):
        if state.get("task", {}).get("status") != "implementing":
            fail("materialize --write requires task status 'implementing' before any durable write")
    if write:
        for target, body, status, _ in planned:
            if status == "identical":
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
    return output


def _scoped_status_files(task_id: str, state: dict[str, Any]) -> list[str]:
    result = git("status", "--porcelain", "--untracked-files=all").stdout.splitlines()
    paths: list[str] = []
    task_prefix = f".ai/tasks/{task_id}/"
    scope = {str(item).replace("\\", "/") for item in state["scope"].get("files", [])}
    for line in result:
        if len(line) < 4:
            continue
        value = line[3:].strip().strip('"').replace("\\", "/")
        if " -> " in value:
            value = value.split(" -> ", 1)[1]
        if value in scope or value.startswith(task_prefix):
            paths.append(value)
    return sorted(set(paths))


def _leading_probe_comments(path: Path) -> str:
    output: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped and not output:
            continue
        if stripped.startswith(("#", "--")) or not stripped:
            output.append(line)
            if len(output) >= 15:
                break
            continue
        break
    return "\n".join(output).rstrip()


def build_closeout(task_id: str) -> str:
    directory = task_dir(task_id)
    state = load_state(directory / "task-state.yaml")
    status = state["task"]["status"]
    gates = ", ".join(f"{key}={value}" for key, value in state["gates"].items())
    changed = _scoped_status_files(task_id, state)
    changed_text = "\n".join(f"- {path}" for path in changed) or "- Không có file scoped thay đổi."
    done = f"status={status}; gates: {gates}\n{changed_text}\n<Main: tóm tắt 1–3 dòng>"

    run_blocks: list[str] = []
    waits: list[str] = []
    if status == "waiting_evidence":
        probe_dir = directory / "evidence" / "probes"
        result_dir = directory / "evidence" / "results"
        grouped: dict[str, list[Path]] = {}
        if probe_dir.is_dir():
            for path in sorted(probe_dir.iterdir()):
                if path.is_file() and path.name != "README.md":
                    grouped.setdefault(path.stem, []).append(path)
        for stem, paths in grouped.items():
            if result_dir.is_dir() and any(result_dir.glob(f"{stem}.*")):
                continue
            selected = paths[0]
            comments = _leading_probe_comments(selected)
            run_blocks.append(
                f"- Probe: {selected.as_posix()}\n"
                f"  Type: {selected.suffix.lstrip('.')}\n"
                f"  Hướng dẫn đầu file:\n{comments or '  <không có comment đầu file>'}\n"
                f"  Dán kết quả vào: {result_dir.as_posix()}/{stem}.txt\n"
                "  Tối đa 50 dòng, không dữ liệu cá nhân, không secret."
            )
            waits.append(f"probe: {stem}")
    elif status == "waiting_runtime":
        runbook = directory / "runtime-runbook.md"
        if runbook.is_file():
            text = runbook.read_text(encoding="utf-8")
            titles = [
                "Phạm vi và môi trường", "Điều kiện tiên quyết", "Baseline trước khi chạy",
                "Các bước thực hiện", "Kiểm tra kết quả", "Chạy lại để kiểm tra idempotency",
                "Kiểm tra log và watermark", "Rollback và forward recovery",
                "Kết quả người dùng ghi nhận",
            ]
            for title in titles:
                section = _markdown_section(text, title)
                if section:
                    run_blocks.append("\n".join(section.splitlines()[:80]))
        waits.append("runtime-result: ghi kết quả đã làm sạch vào runtime-runbook.md")
    if status == "user_decision":
        for finding in state.get("open_findings", []):
            if isinstance(finding, dict) and finding.get("severity") in {"P0", "P1"}:
                waits.append(f"decision/accept-risk: {finding.get('id')} ({finding.get('severity')})")
    if changed:
        waits.append("commit: " + ", ".join(changed))

    run_text = "\n\n".join(run_blocks) if run_blocks else "Không có."
    wait_text = "\n".join(f"- {item}" for item in waits) if waits else "Không có."
    substantive_waits = [item for item in waits if not item.startswith("commit:")]
    if not substantive_waits:
        ending = "Lượt này đã xong trong repository."
    else:
        need = "; ".join(substantive_waits)
        ending = f"Trạng thái tiếp theo: {status}. Trả lời: {need}"
    return (
        f"## Đã làm\n\n{done}\n\n"
        f"## Bạn cần chạy\n\n{run_text}\n\n"
        f"## Agent đang chờ\n\n{wait_text}\n\n"
        f"## Kết thúc\n\n{ending}"
    )


def cmd_toc(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        fail(f"File not found: {path.as_posix()}")
    print(render_toc(path))
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        fail(f"File not found: {path.as_posix()}")
    print(render_show(path, args.anchor, args.max_lines))
    return 0


def cmd_context(args: argparse.Namespace) -> int:
    print(build_context(args.task, args.phase, args.max_lines))
    return 0


def cmd_materialize(args: argparse.Namespace) -> int:
    lines = materialize_blocks(args.task, args.source, args.write)
    print("\n".join(lines) if lines else "No file blocks found.")
    return 0


def cmd_closeout(args: argparse.Namespace) -> int:
    print(build_closeout(args.task))
    return 0


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.returncode, (result.stdout + result.stderr).strip()


CHILD_LISTS = ("activities", "ifTrueActivities", "ifFalseActivities", "defaultActivities")


def walk_activities(activities: list[Any], scope: str, all_names: list[str], errors: list[str]) -> None:
    names = [item.get("name") for item in activities if isinstance(item, dict) and isinstance(item.get("name"), str)]
    all_names.extend(names)
    local_names = set(names)
    for activity in activities:
        if not isinstance(activity, dict):
            errors.append(f"{scope}: activity must be an object")
            continue
        name = activity.get("name", "<unnamed>")
        for dependency in activity.get("dependsOn") or []:
            target = dependency.get("activity") if isinstance(dependency, dict) else dependency
            if target not in local_names:
                errors.append(f"{scope}/{name}: dependsOn {target!r} is not in the same scope")
        properties = activity.get("typeProperties") or {}
        if not isinstance(properties, dict):
            continue
        for key in CHILD_LISTS:
            if isinstance(properties.get(key), list):
                walk_activities(properties[key], f"{scope}/{name}.{key}", all_names, errors)
        for case in properties.get("cases") or []:
            if isinstance(case, dict):
                walk_activities(case.get("activities") or [], f"{scope}/{name}.case[{case.get('value')}]", all_names, errors)


def check_json(paths: list[str]) -> tuple[str, str]:
    errors: list[str] = []
    for path in paths:
        try:
            document = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        activities = (document.get("properties") or {}).get("activities") if isinstance(document, dict) else None
        if isinstance(activities, list):
            names: list[str] = []
            walk_activities(activities, path, names, errors)
            duplicates = sorted({name for name in names if names.count(name) > 1})
            if duplicates:
                errors.append(f"{path}: duplicate activity names: {', '.join(duplicates)}")
    return ("FAIL" if errors else "PASS"), "\n".join(errors)


def check_toml(paths: list[str]) -> tuple[str, str]:
    errors: list[str] = []
    for path in paths:
        try:
            with Path(path).open("rb") as handle:
                tomllib.load(handle)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: invalid TOML: {exc}")
    return ("FAIL" if errors else "PASS"), "\n".join(errors)


def format_compact_verification(
    header: str, files: list[str], results: list[tuple[str, str, str]],
) -> str:
    lines = [header, f"Files: {len(files)}"]
    lines.extend(f"- {path}" for path in files[:10])
    if len(files) > 10:
        lines.append(f"- +{len(files) - 10} more")
    for name, status, output in results:
        lines.append(f"{name}: {status}")
        if status == "FAIL" and output:
            output_lines = output.splitlines()
            lines.extend(output_lines[:40])
            if len(output_lines) > 40:
                lines.append(f"… truncated: {len(output_lines) - 40} more lines; open verification/verify.log")
    return "\n".join(lines)


def cmd_verify(args: argparse.Namespace) -> int:
    files = changed_files(args.all)
    python_files = [path for path in files if path.endswith(".py")]
    postgres_sql = [path for path in files if path.endswith(".pg.sql")]
    spark_sql = [path for path in files if path.endswith(".sql") and not path.endswith(".pg.sql")]
    json_files = [path for path in files if path.endswith(".json") and not path.startswith(".vscode/")]
    toml_files = [path for path in files if path.endswith(".toml")]
    tests = Path("tests")
    has_tests = tests.is_dir() and any(tests.rglob("test_*.py"))
    results: list[tuple[str, str, str]] = []

    def tool(name: str, module: str, command: list[str], targets: list[str]) -> None:
        if not targets:
            results.append((name, "SKIP", "no relevant files"))
        elif not has_module(module):
            status = "SKIP" if args.allow_missing else "FAIL"
            results.append((name, status, f"missing module {module!r}; install requirements-dev.txt"))
        else:
            code, output = run([sys.executable, "-m", module, *command, *targets])
            results.append((name, "PASS" if code == 0 else "FAIL", output))

    tool("ruff", "ruff", ["check", "--no-cache"], python_files)
    tool("sqlfluff[sparksql]", "sqlfluff", ["lint", "--dialect", "sparksql", "--nocolor"], spark_sql)
    tool("sqlfluff[postgres]", "sqlfluff", ["lint", "--dialect", "postgres", "--nocolor"], postgres_sql)
    results.append(("json+pipeline", *check_json(json_files)) if json_files else ("json+pipeline", "SKIP", "no relevant files"))
    results.append(("toml", *check_toml(toml_files)) if toml_files else ("toml", "SKIP", "no relevant files"))
    tool(
        "pytest", "pytest",
        ["-q", "--no-header", "-p", "no:cacheprovider", "--basetemp", ".ai/.tmp/pytest"],
        [str(tests)] if has_tests else [],
    )

    task_errors: list[str] = []
    if args.task:
        task_errors = validate_task(args.task)
    elif args.all:
        for path in sorted(TASKS_ROOT.iterdir()):
            if path.is_dir() and path.name != "_template":
                task_errors.extend(f"{path.name}: {error}" for error in validate_task(path.name))
    results.append(("task-state", "FAIL" if task_errors else "PASS", "\n".join(task_errors)))

    failed = any(status == "FAIL" for _, status, _ in results)
    lines = [
        f"# Verification {dt.datetime.now():%Y-%m-%d %H:%M:%S} — {'FAIL' if failed else 'PASS'}",
        f"Files ({len(files)}): " + (", ".join(files) if files else "none"), "",
    ]
    for name, status, output in results:
        lines.extend([f"## {name}: {status}", output, ""] if output else [f"## {name}: {status}", ""])
    report = "\n".join(lines)
    print(report if args.full else format_compact_verification(lines[0], files, results))
    if args.task:
        log = task_dir(args.task) / "verification" / "verify.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as handle:
            handle.write(report + "\n")
        print(f"Wrote {log.as_posix()}")
    return 1 if failed else 0


def cmd_doctor(_: argparse.Namespace) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    paths = [
        Path("AGENTS.md"), Path("CLAUDE.md"), Path(".codex/config.toml"),
        Path(".claude/settings.json"), TEMPLATE_ROOT / "task-state.yaml",
        Path(".ai/prompts/architect.md"), Path(".ai/prompts/review.md"),
        Path(".ai/evals/cases.yaml"), Path(".ai/evals/rubric.md"),
    ]
    paths.extend(Path(".codex/agents") / f"{name}.toml" for name in [*sorted(REVIEWERS), "risk-gate"])
    for path in paths:
        if not path.is_file():
            errors.append(f"missing required file: {path.as_posix()}")
    if sys.version_info < (3, 11):
        errors.append("Python 3.11 or later is required")
    if yaml is None:
        errors.append("PyYAML is not installed")
    for module in ("ruff", "sqlfluff", "pytest"):
        if not has_module(module):
            warnings.append(f"verification module is not installed: {module}")
    codex_path = Path(".codex/config.toml")
    if codex_path.is_file():
        try:
            with codex_path.open("rb") as handle:
                codex = tomllib.load(handle)
            if codex.get("model") != "gpt-5.6-sol":
                errors.append(".codex/config.toml model must be gpt-5.6-sol")
            if codex.get("model_reasoning_effort") != "medium":
                errors.append(".codex/config.toml reasoning effort must be medium")
            agents = codex.get("agents") or {}
            if agents.get("default_subagent_reasoning_effort") != "medium":
                errors.append(".codex/config.toml subagent reasoning effort must be medium")
            if codex.get("sandbox_mode") != "read-only":
                errors.append(".codex/config.toml sandbox_mode must be read-only")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"cannot parse .codex/config.toml: {exc}")
    claude_path = Path(".claude/settings.json")
    if claude_path.is_file():
        try:
            claude = json.loads(claude_path.read_text(encoding="utf-8"))
            if claude.get("model") != "claude-opus-5-5":
                errors.append(".claude/settings.json model must be claude-opus-5-5")
            if claude.get("effortLevel") != "high":
                errors.append(".claude/settings.json effortLevel must be high")
            permissions = claude.get("permissions") or {}
            if permissions.get("defaultMode") != "dontAsk":
                errors.append(".claude/settings.json defaultMode must be dontAsk")
            if "Edit(/.ai/tasks/*/architecture.md)" not in permissions.get("allow", []):
                errors.append("Claude Architect must be allowed to edit only task architecture files")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"cannot parse .claude/settings.json: {exc}")
    for name in [*sorted(REVIEWERS), "risk-gate"]:
        agent_path = Path(".codex/agents") / f"{name}.toml"
        if not agent_path.is_file():
            continue
        try:
            with agent_path.open("rb") as handle:
                agent = tomllib.load(handle)
            if agent.get("name") != name:
                errors.append(f"{agent_path.as_posix()} name must be {name!r}")
            if agent.get("model") != "gpt-5.6-sol" or agent.get("model_reasoning_effort") != "medium":
                errors.append(f"{agent_path.as_posix()} must use gpt-5.6-sol with medium reasoning")
            if agent.get("sandbox_mode") != "read-only":
                errors.append(f"{agent_path.as_posix()} must use read-only sandbox")
            if not agent.get("description") or not agent.get("developer_instructions"):
                errors.append(f"{agent_path.as_posix()} is missing required agent instructions")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"cannot parse {agent_path.as_posix()}: {exc}")
    if not Path("docs/context/CTRL_TABLES_CONTEXT.md").is_file():
        warnings.append("CTRL_TABLES_CONTEXT.md is missing; ctrl_* changes require evidence and user action")
    eval_path = Path(".ai/evals/cases.yaml")
    if eval_path.is_file() and yaml is not None:
        try:
            evals = yaml.safe_load(eval_path.read_text(encoding="utf-8"))
            cases = evals.get("cases") if isinstance(evals, dict) else None
            if not isinstance(cases, list) or not cases:
                errors.append(".ai/evals/cases.yaml must define at least one case")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"cannot parse .ai/evals/cases.yaml: {exc}")
    old_agents = sorted(Path(".cursor/agents").glob("*.md")) if Path(".cursor/agents").is_dir() else []
    if old_agents:
        errors.append("legacy Cursor reviewers remain: " + ", ".join(path.as_posix() for path in old_agents))
    agent_file = Path("AGENTS.md")
    if agent_file.is_file() and agent_file.stat().st_size > 8192:
        warnings.append(f"instruction budget exceeded: AGENTS.md is {agent_file.stat().st_size} bytes (limit 8192)")
    always_apply_size = 0
    for path in Path(".cursor/rules").rglob("*.mdc") if Path(".cursor/rules").is_dir() else []:
        text = path.read_text(encoding="utf-8")
        if re.search(r"(?m)^alwaysApply:\s*true\s*$", text):
            always_apply_size += path.stat().st_size
    if always_apply_size > 4096:
        warnings.append(f"instruction budget exceeded: always-apply rules total {always_apply_size} bytes (limit 4096)")
    for path in Path(".cursor/skills").rglob("SKILL.md") if Path(".cursor/skills").is_dir() else []:
        if path.stat().st_size > 20480:
            warnings.append(f"skill budget exceeded: {path.as_posix()} is {path.stat().st_size} bytes (limit 20480)")
    samples = Path("docs/AGENT_PROMPT_SAMPLES.md")
    if samples.is_file() and samples.stat().st_size > 25600:
        warnings.append(f"prompt sample budget exceeded: {samples.as_posix()} is {samples.stat().st_size} bytes (limit 25600)")
    if not Path(".cursorindexingignore").is_file():
        warnings.append(".cursorindexingignore is missing")
    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"FAIL: {error}")
    if errors:
        return 1
    print("DOCTOR PASS")
    return 0


def main() -> int:
    os.chdir(repo_root())
    parser = argparse.ArgumentParser(prog="vv", description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    command = subcommands.add_parser("new", help="create a task from the canonical template")
    command.add_argument("slug")
    command.set_defaults(function=cmd_new)
    command = subcommands.add_parser("validate", help="validate task state")
    command.add_argument("task", nargs="?")
    command.add_argument("--all", action="store_true")
    command.set_defaults(function=cmd_validate)
    command = subcommands.add_parser("transition", help="perform an allowed task-state transition")
    command.add_argument("task")
    command.add_argument("status", choices=sorted(STATUSES))
    command.set_defaults(function=cmd_transition)
    command = subcommands.add_parser("prompt", help="generate an Architect or review handoff prompt")
    command.add_argument("task")
    command.add_argument("target", choices=sorted(PROMPTS))
    command.add_argument("--round", type=int, default=1)
    command.set_defaults(function=cmd_prompt)
    command = subcommands.add_parser("toc", help="show Markdown sections or notebook cells")
    command.add_argument("path")
    command.set_defaults(function=cmd_toc)
    command = subcommands.add_parser("show", help="show one Markdown section or notebook anchor")
    command.add_argument("path")
    command.add_argument("anchor")
    command.add_argument("--max-lines", type=int, default=400)
    command.set_defaults(function=cmd_show)
    command = subcommands.add_parser("context", help="build a bounded task context pack")
    command.add_argument("task")
    command.add_argument(
        "--phase", default="auto",
        choices=("auto", "triage", "evidence", "implement", "remediate", "review", "runtime", "closeout"),
    )
    command.add_argument("--max-lines", type=int, default=400)
    command.set_defaults(function=cmd_context)
    command = subcommands.add_parser("materialize", help="extract exact file blocks from a task artifact")
    command.add_argument("task")
    command.add_argument("--source", default="architecture.md", choices=("architecture.md", "proposal.md"))
    command.add_argument("--write", action="store_true")
    command.set_defaults(function=cmd_materialize)
    command = subcommands.add_parser("closeout", help="build the Vietnamese task closeout skeleton")
    command.add_argument("task")
    command.set_defaults(function=cmd_closeout)
    command = subcommands.add_parser("verify", help="run deterministic local verification")
    command.add_argument("task", nargs="?")
    command.add_argument("--all", action="store_true")
    command.add_argument("--allow-missing", action="store_true")
    command.add_argument("--full", action="store_true")
    command.set_defaults(function=cmd_verify)
    command = subcommands.add_parser("doctor", help="check agent-system installation")
    command.set_defaults(function=cmd_doctor)
    command = subcommands.add_parser("external-doctor", help="check Claude and Codex CLI automation")
    command.add_argument("--timeout", type=int, default=30)
    command.set_defaults(function=cmd_external_doctor)
    command = subcommands.add_parser("external-smoke", help="run a read-only Claude and Codex integration smoke test")
    command.add_argument("--timeout", type=int, default=1800)
    command.set_defaults(function=cmd_external_smoke)
    command = subcommands.add_parser("run-gate", help="run the current Architect or review gate non-interactively")
    command.add_argument("task")
    command.add_argument("--round", type=int, choices=(1, 2))
    command.add_argument("--timeout", type=int, default=1800)
    command.set_defaults(function=cmd_run_gate)
    command = subcommands.add_parser("run-author", help="run the Claude proposal or runbook author lane")
    command.add_argument("task")
    command.add_argument("--kind", required=True, choices=tuple(AUTHOR_LANES))
    command.add_argument("--timeout", type=int, default=1800)
    command.set_defaults(function=cmd_run_author)
    args = parser.parse_args()
    return args.function(args)


if __name__ == "__main__":
    sys.exit(main())
