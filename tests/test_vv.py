from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from scripts import vv


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
