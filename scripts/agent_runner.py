"""Run VSVN Architect and review gates through local non-interactive CLIs."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ARCHITECT_MODEL = "claude-opus-5-5"
ARCHITECT_EFFORT = "high"
REVIEW_MODEL = "gpt-5.6-sol"
REVIEW_EFFORT = "medium"
VERDICTS = {"PASS", "FIX_REQUIRED", "EVIDENCE_REQUIRED", "USER_DECISION"}


class RunnerError(RuntimeError):
    """Raised when an external gate cannot be completed safely."""


@dataclass(frozen=True)
class ArchitectureResult:
    verdict: str
    document: str
    executable: Path


@dataclass(frozen=True)
class ReviewResult:
    verdict: str
    report: str
    reviewers_run: tuple[str, ...]
    risk_gate_run: bool
    findings: tuple[dict[str, str], ...]
    executable: Path


def _natural_key(path: Path) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", path.as_posix()))


def _extension_candidates(kind: str) -> list[Path]:
    roots = [Path.home() / ".cursor" / "extensions", Path.home() / ".vscode" / "extensions"]
    if kind == "claude":
        pattern = "anthropic.claude-code-*-win32-x64/resources/native-binary/claude.exe"
    elif kind == "codex":
        pattern = "openai.chatgpt-*-win32-x64/bin/windows-x86_64/codex.exe"
    else:
        raise ValueError(f"Unknown executable kind: {kind}")
    candidates = [path for root in roots for path in root.glob(pattern) if path.is_file()]
    return sorted(candidates, key=_natural_key, reverse=True)


def discover_executable(kind: str, environment: dict[str, str] | None = None) -> Path:
    env = os.environ if environment is None else environment
    settings = {
        "claude": ("VSVN_CLAUDE_EXE", "claude"),
        "codex": ("VSVN_CODEX_EXE", "codex"),
    }
    if kind not in settings:
        raise ValueError(f"Unknown executable kind: {kind}")
    env_name, command = settings[kind]
    configured = env.get(env_name, "").strip()
    if configured:
        path = Path(os.path.expandvars(configured)).expanduser().resolve()
        if not path.is_file():
            raise RunnerError(f"{env_name} does not point to a file: {path}")
        return path
    discovered = shutil.which(command, path=env.get("PATH"))
    if discovered:
        return Path(discovered).resolve()
    candidates = _extension_candidates(kind)
    if candidates:
        return candidates[0].resolve()
    raise RunnerError(
        f"Cannot find {command}. Set {env_name} to the executable path or install the CLI on PATH."
    )


def _run(
    command: list[str],
    *,
    cwd: Path,
    input_text: str | None = None,
    timeout_seconds: int = 1800,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RunnerError(f"External agent timed out after {timeout_seconds} seconds.") from exc
    except OSError as exc:
        raise RunnerError(f"Cannot start external agent: {exc}") from exc


def _command_failure(label: str, result: subprocess.CompletedProcess[str]) -> RunnerError:
    details = (result.stderr or result.stdout).strip()
    if len(details) > 4000:
        details = details[-4000:]
    return RunnerError(f"{label} failed with exit code {result.returncode}:\n{details}")


def _git_snapshot(repo: Path) -> bytes:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=repo,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RunnerError(f"Cannot capture Git status: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def _assert_repo_unchanged(repo: Path, before: bytes, label: str) -> None:
    after = _git_snapshot(repo)
    if after == before:
        return
    status = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    ).stdout.strip()
    raise RunnerError(f"{label} changed the repository unexpectedly. Inspect before continuing:\n{status}")


def _parse_json_text(value: str) -> Any:
    text = value.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, count=1, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text, count=1)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RunnerError(f"External agent returned invalid JSON: {exc}") from exc


def parse_claude_output(output: str) -> dict[str, Any]:
    outer = _parse_json_text(output)
    if not isinstance(outer, dict):
        raise RunnerError("Claude output must be a JSON object.")
    if outer.get("is_error") is True:
        raise RunnerError(f"Claude reported an error: {outer.get('result', '<no details>')}")
    for key in ("structured_output", "result"):
        value = outer.get(key)
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            parsed = _parse_json_text(value)
            if isinstance(parsed, dict):
                return parsed
    if {"verdict", "document"}.issubset(outer):
        return outer
    raise RunnerError("Claude JSON did not contain structured architecture output.")


def _architecture_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["PASS", "EVIDENCE_REQUIRED"]},
            "document": {"type": "string", "minLength": 20},
        },
        "required": ["verdict", "document"],
        "additionalProperties": False,
    }


def run_architecture(repo: Path, prompt: str, timeout_seconds: int = 1800) -> ArchitectureResult:
    executable = discover_executable("claude")
    schema = _architecture_schema()
    automation_contract = """

## Automated execution contract

This is a non-interactive, read-only architecture run. Do not edit any file. Return structured JSON matching
the supplied schema. `document` must be the complete English content for the task's `architecture.md`, and its
first non-blank line must be exactly `RESULT: PASS` or `RESULT: EVIDENCE_REQUIRED`, matching `verdict`.
Do not wrap the JSON or document in Markdown fences.
"""
    before = _git_snapshot(repo)
    command = [
        str(executable),
        "-p",
        "--model", ARCHITECT_MODEL,
        "--effort", ARCHITECT_EFFORT,
        "--output-format", "json",
        "--json-schema", json.dumps(schema, separators=(",", ":")),
        "--max-turns", "80",
        "--permission-mode", "dontAsk",
        "--permission-prompts", "none",
        "--tools", "Read,Glob,Grep",
        "--safe-mode",
        "--setting-sources", "user",
        "--no-session-persistence",
    ]
    result = _run(command, cwd=repo, input_text=prompt + automation_contract, timeout_seconds=timeout_seconds)
    _assert_repo_unchanged(repo, before, "Claude Architect")
    if result.returncode:
        raise _command_failure("Claude Architect", result)
    payload = parse_claude_output(result.stdout)
    verdict = payload.get("verdict")
    document = payload.get("document")
    if verdict not in {"PASS", "EVIDENCE_REQUIRED"} or not isinstance(document, str):
        raise RunnerError("Claude architecture result has an invalid verdict or document.")
    first_line = next((line.strip() for line in document.splitlines() if line.strip()), "")
    if first_line != f"RESULT: {verdict}":
        raise RunnerError(f"architecture.md must begin with 'RESULT: {verdict}'.")
    return ArchitectureResult(verdict=verdict, document=document.rstrip() + "\n", executable=executable)


def _review_schema(reviewers: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "model": {"type": "string", "enum": [REVIEW_MODEL]},
            "reasoning_effort": {"type": "string", "enum": [REVIEW_EFFORT]},
            "reviewers_run": {
                "type": "array",
                "items": {"type": "string", "enum": reviewers or ["none"]},
            },
            "risk_gate_run": {"type": "boolean"},
            "verdict": {"type": "string", "enum": sorted(VERDICTS)},
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "minLength": 1},
                        "severity": {"type": "string", "enum": ["P0", "P1", "P2", "P3"]},
                    },
                    "required": ["id", "severity"],
                    "additionalProperties": False,
                },
            },
            "report": {"type": "string", "minLength": 20},
        },
        "required": [
            "model", "reasoning_effort", "reviewers_run", "risk_gate_run", "verdict", "findings", "report",
        ],
        "additionalProperties": False,
    }


def validate_reviewer_manifest(value: Any, required_reviewers: list[str]) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise RunnerError(
            f"Codex reviewer manifest mismatch: expected {required_reviewers}, got {value}."
        )
    if len(value) != len(set(value)) or set(value) != set(required_reviewers):
        raise RunnerError(
            f"Codex reviewer manifest mismatch: expected {required_reviewers}, got {value}."
        )
    return tuple(value)


def _validate_jsonl(output: str) -> None:
    for line_number, line in enumerate(output.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RunnerError(f"Codex emitted invalid JSONL at line {line_number}: {exc}") from exc
        if event.get("type") in {"error", "turn.failed"}:
            raise RunnerError(f"Codex reported {event.get('type')}: {event}")


def run_review(
    repo: Path,
    prompt: str,
    required_reviewers: list[str],
    risk_gate_required: bool,
    timeout_seconds: int = 1800,
) -> ReviewResult:
    executable = discover_executable("codex")
    schema = _review_schema(required_reviewers)
    automation_contract = f"""

## Automated execution contract

Run exactly these specialist reviewers independently: {json.dumps(required_reviewers)}.
Risk gate required: {str(risk_gate_required).lower()}.
Return only the JSON object required by the output schema. `reviewers_run` must list every specialist actually
spawned, `risk_gate_run` must state whether risk-gate completed, and `report` must contain the complete consolidated
Markdown review. Never edit repository files.
"""
    before = _git_snapshot(repo)
    temp_root = repo / ".ai" / ".tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vsvn-review-", dir=temp_root) as temporary:
        temp = Path(temporary)
        schema_path = temp / "review-schema.json"
        output_path = temp / "review-result.json"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        command = [
            str(executable), "exec",
            "--strict-config",
            "--ephemeral",
            "--json",
            "--model", REVIEW_MODEL,
            "-c", f'model_reasoning_effort="{REVIEW_EFFORT}"',
            "-c", 'approval_policy="never"',
            "--sandbox", "read-only",
            "--cd", str(repo),
            "--output-schema", str(schema_path),
            "--output-last-message", str(output_path),
            "-",
        ]
        result = _run(command, cwd=repo, input_text=prompt + automation_contract, timeout_seconds=timeout_seconds)
        _assert_repo_unchanged(repo, before, "Codex review")
        if result.returncode:
            raise _command_failure("Codex review", result)
        _validate_jsonl(result.stdout)
        if not output_path.is_file():
            raise RunnerError("Codex did not write its final structured result.")
        payload = _parse_json_text(output_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RunnerError("Codex final result must be a JSON object.")
    if payload.get("model") != REVIEW_MODEL or payload.get("reasoning_effort") != REVIEW_EFFORT:
        raise RunnerError("Codex reported a model or reasoning-effort mismatch.")
    reviewers_run = validate_reviewer_manifest(payload.get("reviewers_run"), required_reviewers)
    if payload.get("risk_gate_run") is not risk_gate_required:
        raise RunnerError(
            f"Codex risk-gate manifest mismatch: expected {risk_gate_required}, got {payload.get('risk_gate_run')}."
        )
    verdict = payload.get("verdict")
    report = payload.get("report")
    findings = payload.get("findings")
    if verdict not in VERDICTS or not isinstance(report, str) or not isinstance(findings, list):
        raise RunnerError("Codex review result has an invalid verdict, findings list, or report.")
    normalized_findings = tuple({"id": item["id"], "severity": item["severity"]} for item in findings)
    if verdict == "PASS" and any(item["severity"] in {"P0", "P1"} for item in normalized_findings):
        raise RunnerError("Codex returned PASS while P0/P1 findings remain open.")
    return ReviewResult(
        verdict=verdict,
        report=report.rstrip() + "\n",
        reviewers_run=reviewers_run,
        risk_gate_run=risk_gate_required,
        findings=normalized_findings,
        executable=executable,
    )


def external_preflight(repo: Path, timeout_seconds: int = 30) -> dict[str, str]:
    claude = discover_executable("claude")
    codex = discover_executable("codex")
    claude_version = _run([str(claude), "--version"], cwd=repo, timeout_seconds=timeout_seconds)
    if claude_version.returncode:
        raise _command_failure("Claude version check", claude_version)
    claude_auth = _run([str(claude), "auth", "status"], cwd=repo, timeout_seconds=timeout_seconds)
    if claude_auth.returncode:
        raise _command_failure("Claude authentication check", claude_auth)
    try:
        claude_auth_data = json.loads(claude_auth.stdout)
    except json.JSONDecodeError as exc:
        raise RunnerError(f"Claude auth status returned invalid JSON: {exc}") from exc
    if claude_auth_data.get("loggedIn") is not True:
        raise RunnerError("Claude CLI is not authenticated.")
    codex_version = _run([str(codex), "--version"], cwd=repo, timeout_seconds=timeout_seconds)
    if codex_version.returncode:
        raise _command_failure("Codex version check", codex_version)
    codex_auth = _run([str(codex), "login", "status"], cwd=repo, timeout_seconds=timeout_seconds)
    codex_auth_output = codex_auth.stdout + codex_auth.stderr
    if codex_auth.returncode or "Logged in" not in codex_auth_output:
        raise _command_failure("Codex authentication check", codex_auth)
    return {
        "claude_executable": str(claude),
        "claude_version": claude_version.stdout.strip().splitlines()[0],
        "claude_auth": "configured",
        "codex_executable": str(codex),
        "codex_version": codex_version.stdout.strip().splitlines()[0],
        "codex_auth": "configured",
    }
