from __future__ import annotations

import json
from argparse import Namespace
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


def test_architecture_schema_requires_bounded_main_brief() -> None:
    schema = agent_runner._architecture_schema()
    assert "main_brief" in schema["required"]
    assert schema["properties"]["main_brief"] == {
        "type": "string", "minLength": 200, "maxLength": 14000,
    }


def test_compose_architecture_places_brief_and_demotes_headings() -> None:
    document = "RESULT: PASS\n\n# Architecture\n\n## Scope\n\nDetails.\n"
    brief = "## Decision\n\nProceed.\n\n### Edit list\n\nOne row."
    composed = agent_runner.compose_architecture(document, brief)
    assert composed.startswith("RESULT: PASS\n\n## Main brief\n\n### Decision")
    assert "\n\n# Architecture\n" in composed
    assert composed.count("RESULT: PASS") == 1
    assert "\n## Decision\n" not in composed


def test_architecture_duplicate_main_brief_warning() -> None:
    warnings = agent_runner.architecture_warnings("RESULT: PASS\n\n## Main brief\n\nDuplicate.\n")
    assert len(warnings) == 1
    assert "already contains" in warnings[0]


def test_author_schema_requires_document() -> None:
    schema = agent_runner._author_schema()
    assert schema["required"] == ["document"]
    assert schema["properties"]["document"] == {"type": "string", "minLength": 200}


def test_review_schema_uses_supported_reviewer_array_keywords() -> None:
    schema = agent_runner._review_schema(["state-correctness-reviewer"])
    reviewers_run = schema["properties"]["reviewers_run"]
    assert "uniqueItems" not in reviewers_run
    assert schema["properties"]["model"]["enum"] == ["gpt-5.6-sol"]
    assert schema["properties"]["reasoning_effort"]["enum"] == ["medium"]


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


def prepare_author_task(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, author_input: str | None,
) -> tuple[str, Path, dict]:
    data = template_state()
    task_id = "20261014-author-test"
    data["task"].update(id=task_id, created_at="2026-10-14", updated_at="2026-10-14")
    directory = tmp_path / ".ai" / "tasks" / task_id
    (directory / "handoffs").mkdir(parents=True)
    (tmp_path / ".ai" / "tasks" / "_template").mkdir(parents=True)
    (tmp_path / ".ai" / "prompts").mkdir(parents=True)
    (directory / "task-state.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False), encoding="utf-8",
    )
    if author_input is not None:
        (directory / "handoffs" / "author-input.md").write_text(author_input, encoding="utf-8")
    for kind in ("proposal", "runbook"):
        (tmp_path / ".ai" / "prompts" / f"author-{kind}.md").write_text(
            f"# {kind} for {{{{TASK_ID}}}}\n", encoding="utf-8",
        )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(vv, "TASKS_ROOT", Path(".ai/tasks"))
    monkeypatch.setattr(vv, "TEMPLATE_ROOT", Path(".ai/tasks/_template"))
    monkeypatch.setattr(vv, "repo_root", lambda: tmp_path)
    return task_id, directory, data


def fake_author_result() -> agent_runner.AuthorResult:
    return agent_runner.AuthorResult(
        document="# Tài liệu\n\n" + "Nội dung kiểm thử. " * 20,
        executable=Path("claude.exe"),
    )


def test_run_author_requires_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    task_id, _, _ = prepare_author_task(tmp_path, monkeypatch, author_input=None)
    with pytest.raises(SystemExit, match="Author input not found"):
        vv.cmd_run_author(Namespace(task=task_id, kind="proposal", timeout=30))


def test_run_author_rejects_long_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    task_id, _, _ = prepare_author_task(
        tmp_path, monkeypatch, author_input="\n".join(f"line {index}" for index in range(61)),
    )
    with pytest.raises(SystemExit, match="exceeds 60 lines: 61"):
        vv.cmd_run_author(Namespace(task=task_id, kind="proposal", timeout=30))


def test_run_author_writes_output_and_updates_only_author_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_id, directory, original = prepare_author_task(tmp_path, monkeypatch, author_input="Use request.md.")
    state_path = directory / "task-state.yaml"
    state_without_author = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    del state_without_author["models"]["author"]
    state_path.write_text(yaml.safe_dump(state_without_author, sort_keys=False), encoding="utf-8")
    monkeypatch.setattr(agent_runner, "run_author", lambda *_args, **_kwargs: fake_author_result())

    assert vv.cmd_run_author(Namespace(task=task_id, kind="proposal", timeout=30)) == 0

    assert (directory / "proposal.md").read_text(encoding="utf-8") == fake_author_result().document
    updated = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    assert updated["models"]["author"] == {
        "expected": "claude-opus-5-5", "effort": "medium", "actual": "claude-opus-5-5",
    }
    assert updated["task"]["status"] == original["task"]["status"]
    assert updated["gates"] == original["gates"]


def test_run_author_preserves_existing_output_with_new_suffix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    task_id, directory, _ = prepare_author_task(tmp_path, monkeypatch, author_input="Use architecture.md.")
    existing = "# Existing runbook\n\nKeep this content.\n"
    (directory / "runtime-runbook.md").write_text(existing, encoding="utf-8")
    monkeypatch.setattr(agent_runner, "run_author", lambda *_args, **_kwargs: fake_author_result())

    assert vv.cmd_run_author(Namespace(task=task_id, kind="runbook", timeout=30)) == 0

    assert (directory / "runtime-runbook.md").read_text(encoding="utf-8") == existing
    assert (directory / "runtime-runbook.new.md").read_text(encoding="utf-8") == fake_author_result().document
    assert "Existing artifact preserved" in capsys.readouterr().out
