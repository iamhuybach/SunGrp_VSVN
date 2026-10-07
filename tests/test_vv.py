from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from scripts import agent_runner, vv


def template_state() -> dict:
    text = Path(".ai/tasks/_template/task-state.yaml").read_text(encoding="utf-8")
    text = text.replace("{{TASK_ID}}", "20261007-test-task").replace("{{DATE}}", "2026-10-07")
    return yaml.safe_load(text)


def test_task_id_validation() -> None:
    assert vv.validated_task_id("20261007-valid-task") == "20261007-valid-task"
    for value in ("../escape", "20261007-UPPER", "2026-10-07-task", ""):
        with pytest.raises(SystemExit):
            vv.validated_task_id(value)


def test_template_state_is_valid() -> None:
    assert vv.validate_state_data(template_state(), "20261007-test-task") == []


def test_high_risk_requires_risk_gate() -> None:
    state = deepcopy(template_state())
    state["classification"]["risk_level"] = "high"
    errors = vv.validate_state_data(state, "20261007-test-task")
    assert "gates.risk_gate cannot be not_required for this classification" in errors


def test_implementation_requires_confirmed_main_model() -> None:
    state = deepcopy(template_state())
    state["task"]["status"] = "implementing"
    errors = vv.validate_state_data(state, "20261007-test-task")
    assert "models.main.actual must confirm 'grok-4.7' before this gate/status" in errors


def test_passed_architecture_requires_confirmed_architect_model() -> None:
    state = deepcopy(template_state())
    state["classification"]["architecture_required"] = True
    state["gates"]["architecture"] = "pass"
    errors = vv.validate_state_data(state, "20261007-test-task")
    assert "models.architect.actual must confirm 'claude-opus-5-5' before this gate/status" in errors


def test_ready_state_rejects_open_blocker() -> None:
    state = deepcopy(template_state())
    state["task"]["status"] = "ready_to_merge"
    state["gates"]["local_verification"] = "pass"
    state["open_findings"] = [{"id": "STATE-001", "severity": "P1"}]
    errors = vv.validate_state_data(state, "20261007-test-task")
    assert any("blocking findings" in error for error in errors)


def test_pipeline_dependency_must_be_in_same_scope() -> None:
    pipeline = Path("tests/.pipeline-test.json")
    try:
        pipeline.write_text(
            '{"properties":{"activities":[{"name":"A","dependsOn":[{"activity":"B"}]}]}}',
            encoding="utf-8",
        )
        status, details = vv.check_json([str(pipeline)])
        assert status == "FAIL"
        assert "not in the same scope" in details
    finally:
        pipeline.unlink(missing_ok=True)


def test_claude_structured_output_parsing() -> None:
    payload = {
        "structured_output": {
            "verdict": "PASS",
            "document": "RESULT: PASS\n\n# Architecture\n",
        },
    }
    assert agent_runner.parse_claude_output(json.dumps(payload))["verdict"] == "PASS"


def test_review_schema_uses_supported_reviewer_array_keywords() -> None:
    schema = agent_runner._review_schema(["state-correctness-reviewer"])
    reviewers_run = schema["properties"]["reviewers_run"]
    assert "uniqueItems" not in reviewers_run
    assert schema["properties"]["model"]["enum"] == ["gpt-5.6-sol"]
    assert schema["properties"]["reasoning_effort"]["enum"] == ["high"]


def test_reviewer_manifest_rejects_duplicates() -> None:
    with pytest.raises(agent_runner.RunnerError, match="reviewer manifest mismatch"):
        agent_runner.validate_reviewer_manifest(
            ["state-correctness-reviewer", "state-correctness-reviewer"],
            ["state-correctness-reviewer"],
        )


def test_executable_environment_override() -> None:
    executable = Path("tests/.agent-runner-test-claude.exe")
    try:
        executable.write_bytes(b"test")
        result = agent_runner.discover_executable(
            "claude", {"VSVN_CLAUDE_EXE": str(executable), "PATH": ""},
        )
        assert result == executable.resolve()
    finally:
        executable.unlink(missing_ok=True)


def test_architecture_pass_advances_to_implementation() -> None:
    state = template_state()
    state["task"].update(status="waiting_architecture", owner="architect")
    state["classification"]["architecture_required"] = True
    state["gates"]["architecture"] = "pending"
    state["models"]["main"]["actual"] = "grok-4.7"
    candidate = vv.architecture_state_after(state, "PASS")
    assert candidate["task"]["status"] == "implementing"
    assert candidate["gates"]["architecture"] == "pass"
    assert candidate["models"]["architect"]["actual"] == "claude-opus-5-5"
    assert vv.validate_state_data(candidate, "20261007-test-task") == []


def test_review_evidence_verdict_routes_to_evidence() -> None:
    state = template_state()
    state["task"].update(status="reviewing", owner="review")
    state["models"]["main"]["actual"] = "grok-4.7"
    state["review_plan"]["required_reviewers"] = ["state-correctness-reviewer"]
    state["gates"]["specialist_review"] = "pending"
    state["gates"]["local_verification"] = "pass"
    result = agent_runner.ReviewResult(
        verdict="EVIDENCE_REQUIRED",
        report="# Review\n",
        reviewers_run=("state-correctness-reviewer",),
        risk_gate_run=False,
        findings=({"id": "STATE-001", "severity": "P1"},),
        executable=Path("codex.exe"),
    )
    candidate = vv.review_state_after(state, result, 1)
    assert candidate["task"]["status"] == "waiting_evidence"
    assert candidate["classification"]["evidence_required"] is True
    assert candidate["gates"]["evidence"] == "evidence_required"
    assert candidate["gates"]["specialist_review"] == "evidence_required"
    assert vv.validate_state_data(candidate, "20261007-test-task") == []
