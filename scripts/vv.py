#!/usr/bin/env python3
"""Deterministic VSVN agent-workflow helper."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
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
    "cross_state_impact", "runtime_proof_required", "data_evidence_required",
    "low_probability_high_impact", "deep_reasoning_required",
}
REVIEWERS = {
    "state-correctness-reviewer", "spark-runtime-reviewer",
    "sql-data-reviewer", "fabric-pipeline-reviewer",
}
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
    if review_plan.get("round") not in {0, 1, 2}:
        errors.append("review_plan.round must be 0, 1, or 2")

    expected_models = {
        "main": "grok-4.7", "architect": "claude-opus-5-5",
        "review": "gpt-5.6-sol",
    }
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

    required_actual_models = {"main"}
    if gates.get("architecture") == "pass":
        required_actual_models.add("architect")
    if gates.get("specialist_review") == "pass" or gates.get("risk_gate") == "pass":
        required_actual_models.add("review")
    if status in {"triage", "waiting_evidence", "waiting_architecture"}:
        required_actual_models.discard("main")
    for role in required_actual_models:
        model = models.get(role)
        if isinstance(model, dict) and model.get("actual") != expected_models[role]:
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

    for name, limit in {"verification": 2, "review": 2, "architecture": 2, "runtime_failure": 2}.items():
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


def render_prompt(task_id: str, target: str, round_number: int = 1) -> tuple[Path, str]:
    directory = task_dir(task_id)
    template = Path(".ai/prompts") / PROMPTS[target]
    if not template.is_file():
        fail(f"Prompt template not found: {template.as_posix()}")
    if target == "review" and round_number not in {1, 2}:
        fail("Review round must be 1 or 2.")
    text = template.read_text(encoding="utf-8")
    text = text.replace("{{TASK_ID}}", task_id).replace("{{ROUND}}", str(round_number))
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
            handoff, prompt = render_prompt(args.task, "architect")
            print(f"Running Claude Architect from {handoff.as_posix()}...")
            result = agent_runner.run_architecture(repo_root(), prompt, timeout_seconds=args.timeout)
            candidate = architecture_state_after(state, result.verdict)
            _validate_candidate_state(args.task, candidate)
            architecture = directory / "architecture.md"
            architecture.write_text(result.document, encoding="utf-8")
            write_state(state_path, candidate)
            print(f"ARCHITECTURE {result.verdict}: {architecture.as_posix()}")
            print(f"Executable: {result.executable}")
            print(f"Next status: {candidate['task']['status']}")
            return 0
        if status == "reviewing":
            if state["gates"]["local_verification"] != "pass":
                fail("Local verification must pass before automated review.")
            expected_round = state["rounds"]["review"] + 1
            if expected_round > 2:
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
            if round_number != expected_round or round_number not in {1, 2}:
                fail(f"Expected review round {expected_round}; received {round_number}.")
            handoff, prompt = render_prompt(args.task, "review", round_number)
            reviewers = list(state["review_plan"]["required_reviewers"])
            risk_required = state["classification"]["risk_level"] in {"high", "critical"}
            print(f"Running Codex review from {handoff.as_posix()}...")
            result = agent_runner.run_review(
                repo_root(), prompt, reviewers, risk_required, timeout_seconds=args.timeout,
            )
            candidate = review_state_after(state, result, round_number)
            _validate_candidate_state(args.task, candidate)
            review_path = directory / "reviews" / f"round-{round_number}.md"
            review_path.parent.mkdir(parents=True, exist_ok=True)
            review_path.write_text(result.report, encoding="utf-8")
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


def changed_files(all_files: bool) -> list[str]:
    if all_files:
        files = set(nul_paths(git("ls-files", "-z").stdout))
    elif git("rev-parse", "--verify", "-q", "HEAD", check=False).returncode == 0:
        files = set(nul_paths(git("diff", "--name-only", "-z", "HEAD").stdout))
    else:
        files = set(nul_paths(git("ls-files", "-z").stdout))
    files |= set(nul_paths(git("ls-files", "--others", "--exclude-standard", "-z").stdout))
    return sorted(path for path in files if not path.startswith(".ai/") and Path(path).is_file())


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
    print(report)
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
    command = subcommands.add_parser("verify", help="run deterministic local verification")
    command.add_argument("task", nargs="?")
    command.add_argument("--all", action="store_true")
    command.add_argument("--allow-missing", action="store_true")
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
    args = parser.parse_args()
    return args.function(args)


if __name__ == "__main__":
    sys.exit(main())
