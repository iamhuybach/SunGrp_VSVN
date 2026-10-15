from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml

from scripts import vv


FIXTURE = Path("tests/fixtures/sample_notebook.ipynb")


def state(task_id: str = "20261014-test-context") -> dict:
    return {
        "schema_version": 1,
        "task": {
            "id": task_id, "title": "Context test", "status": "triage", "owner": "main",
            "created_at": "2026-10-14", "updated_at": "2026-10-14",
        },
        "classification": {
            "complexity": "low", "risk_level": "low", "architecture_required": False,
            "evidence_required": False, "runtime_required": False, "signals": [],
        },
        "scope": {"systems": [], "files": ["scripts/vv.py"]},
        "review_plan": {"required_reviewers": [], "round": 0},
        "models": {
            "main": {"expected": "grok-4.7", "effort": "medium", "actual": ""},
            "architect": {"expected": "claude-opus-5-5", "effort": "high", "actual": ""},
            "review": {"expected": "gpt-5.6-sol", "effort": "medium", "actual": ""},
        },
        "gates": {
            "evidence": "not_required", "architecture": "not_required",
            "local_verification": "pending", "specialist_review": "not_required",
            "risk_gate": "not_required", "runtime": "not_required",
        },
        "rounds": {"verification": 0, "review": 0, "architecture": 0, "runtime_failure": 0},
        "open_findings": [],
    }


def write_task(root: Path, data: dict, *, ledger: bool = True, brief: bool = True) -> str:
    task_id = data["task"]["id"]
    directory = root / ".ai" / "tasks" / task_id
    directory.mkdir(parents=True)
    (directory / "task-state.yaml").write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    (directory / "request.md").write_text(
        "# Request\n\n## User outcome\n\nOutcome.\n\n## Scope\n\nScope.\n\n"
        "## Acceptance criteria\n\n- Pass.\n\n## Constraints\n\n- Safe.\n",
        encoding="utf-8",
    )
    decision = "# Quyết định\n\n"
    if ledger:
        decision += "## Quyết định hiện hành\n\n| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |\n|---|---|---|---|---|\n"
    decision += "\n## Xử lý findings\n\n| Finding ID | Severity | Quyết định |\n|---|---|---|\n"
    (directory / "decision.md").write_text(decision, encoding="utf-8")
    architecture = "RESULT: PASS\n\n# Architecture\n\n"
    if brief:
        architecture += "## Main brief\n\n### Decision\n\nImplement the edit list.\n"
    architecture += "\n## Full design\n\nDetails.\n"
    (directory / "architecture.md").write_text(architecture, encoding="utf-8")
    return task_id


def test_markdown_toc_ignores_fenced_headings_and_ranges() -> None:
    text = "# A\nintro\n## B\n```md\n# ignored\n```\nbody\n# C\nend\n"
    headings = vv.markdown_toc(text)
    assert [(item.title, item.start, item.end) for item in headings] == [
        ("A", 1, 7), ("B", 3, 7), ("C", 8, 9),
    ]


def test_notebook_cells_maps_fabric_json_lines() -> None:
    cells = vv.notebook_cells(FIXTURE)
    assert len(cells) == 3
    assert cells[0].json_start == 3
    assert cells[0].json_end is not None
    assert cells[1].id == "function-cell"
    assert "greet" in vv._cell_defs(cells[1])


def test_notebook_cells_degrades_when_layout_differs(tmp_path: Path) -> None:
    path = tmp_path / "compact.ipynb"
    path.write_text('{"cells":[{"cell_type":"code","id":"x","source":["x=1"]}]}', encoding="utf-8")
    cell = vv.notebook_cells(path)[0]
    assert cell.json_start is None
    assert cell.json_end is None


def test_show_notebook_anchors_and_truncation() -> None:
    assert "def greet" in vv.render_show(FIXTURE, "cell:1")
    assert "function-cell" in vv.render_show(FIXTURE, "def:greet")
    grep = vv.render_show(FIXTURE, "grep:greet")
    assert "cell 1 line 1" in grep
    assert "cell 2 line 2" in grep
    truncated = vv.render_show(FIXTURE, "cell:0-2", max_lines=2)
    assert "truncated:" in truncated


def test_show_markdown_ambiguous_heading(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_text("# Main one\n\n# Main two\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="Ambiguous"):
        vv.render_show(path, "Main")


def test_build_context_phase_mapping_ledger_brief_and_limit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data = state()
    data["task"].update(status="implementing", owner="main")
    data["models"]["main"]["actual"] = "grok-4.7"
    task_id = write_task(tmp_path, data)
    monkeypatch.chdir(tmp_path)
    output = vv.build_context(task_id)
    assert "phase=implement" in output
    assert "## Quyết định hiện hành" in output
    assert "## Main brief" in output
    limited = vv.build_context(task_id, max_lines=8)
    assert len(limited.splitlines()) == 9
    assert "truncated:" in limited


def test_build_context_falls_back_to_tocs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data = state()
    data["task"].update(status="implementing", owner="main")
    data["models"]["main"]["actual"] = "grok-4.7"
    task_id = write_task(tmp_path, data, ledger=False, brief=False)
    monkeypatch.chdir(tmp_path)
    output = vv.build_context(task_id)
    assert "no ledger" in output
    assert "no Main brief" in output


def test_parse_file_blocks_preserves_crlf_and_markers() -> None:
    data = b"outside\r\nFILE: a.txt\r\none\r\ntwo\r\nEND_FILE\r\nSKILL_FILE: b.md\nbody\nEND_SKILL_FILE\n"
    assert vv.parse_file_blocks(data) == [
        ("a.txt", b"one\r\ntwo\r\n"), ("b.md", b"body\n"),
    ]
    with pytest.raises(SystemExit, match="Unclosed"):
        vv.parse_file_blocks(b"FILE: a.txt\nbody\n")
    with pytest.raises(SystemExit, match="Duplicate"):
        vv.parse_file_blocks(b"FILE: a.txt\nx\nEND_FILE\nFILE: a.txt\ny\nEND_FILE\n")


def test_materialize_path_rejection() -> None:
    for path in ("../escape", ".git/config", "x/task-state.yaml", "not-in-scope.txt"):
        with pytest.raises(SystemExit):
            vv._materialize_target(path, {"allowed.txt"})


def test_build_closeout_waiting_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data = state()
    data["task"].update(status="waiting_evidence", owner="user")
    data["classification"]["evidence_required"] = True
    data["gates"]["evidence"] = "evidence_required"
    task_id = write_task(tmp_path, data)
    probe = tmp_path / ".ai" / "tasks" / task_id / "evidence" / "probes" / "p1.sql"
    probe.parent.mkdir(parents=True)
    probe.write_text("-- Run in Fabric DEV\n-- Counts only\nSELECT 1;\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(vv, "_scoped_status_files", lambda *_: [])
    output = vv.build_closeout(task_id)
    assert list(filter(lambda line: line.startswith("## "), output.splitlines())) == [
        "## Đã làm", "## Bạn cần chạy", "## Agent đang chờ", "## Kết thúc",
    ]
    assert "probe: p1" in output
    assert "Tối đa 50 dòng" in output


def test_build_closeout_nothing_pending(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data = state()
    task_id = write_task(tmp_path, data)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(vv, "_scoped_status_files", lambda *_: [])
    output = vv.build_closeout(task_id)
    assert "Agent đang chờ\n\nKhông có." in output
    assert output.endswith("Lượt này đã xong trong repository.")


def test_exception_validation_and_actual_override() -> None:
    data = state()
    data["task"].update(status="implementing", owner="main")
    data["models"]["main"]["actual"] = "gpt-5.6-sol"
    override = {
        "id": "EXC-01", "kind": "model_override", "role": "main", "model": "gpt-5.6-sol",
        "effort": "medium", "runtime": "codex-cli", "approved_by": "user",
        "approved_on": "2026-10-14", "scope": "Test override.",
    }
    data["exceptions"] = [override]
    assert vv.validate_state_data(data, data["task"]["id"]) == []

    missing_approval = copy.deepcopy(data)
    missing_approval["exceptions"][0]["approved_by"] = "agent"
    assert any("approved_by" in item for item in vv.validate_state_data(missing_approval, data["task"]["id"]))

    wrong_role = copy.deepcopy(data)
    wrong_role["exceptions"][0]["role"] = "worker"
    assert any(".role" in item for item in vv.validate_state_data(wrong_role, data["task"]["id"]))

    mismatch = copy.deepcopy(data)
    mismatch["models"]["main"]["actual"] = "other-model"
    assert any("models.main.actual" in item for item in vv.validate_state_data(mismatch, data["task"]["id"]))


def test_optional_author_model_validation() -> None:
    data = state()
    data["models"]["author"] = {
        "expected": "claude-opus-5-5", "effort": "medium", "actual": "",
    }
    assert vv.validate_state_data(data, data["task"]["id"]) == []
    invalid = copy.deepcopy(data)
    invalid["models"]["author"]["effort"] = "high"
    assert any("models.author.effort" in item for item in vv.validate_state_data(invalid, data["task"]["id"]))

    unauthorized = copy.deepcopy(data)
    unauthorized["models"]["author"]["actual"] = "unapproved-model"
    assert any(
        "models.author.actual" in item
        for item in vv.validate_state_data(unauthorized, data["task"]["id"])
    )

    approved = copy.deepcopy(data)
    approved["models"]["author"]["actual"] = "approved-author-model"
    approved["exceptions"] = [{
        "id": "EXC-AUTHOR", "kind": "model_override", "role": "author",
        "model": "approved-author-model", "effort": "medium", "runtime": "claude-cli",
        "approved_by": "user", "approved_on": "2026-10-14", "scope": "Author fallback test.",
    }]
    assert vv.validate_state_data(approved, data["task"]["id"]) == []


def test_materialize_write_requires_implementing_before_any_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_id = "20261014-materialize-state"
    task = tmp_path / ".ai" / "tasks" / task_id
    task.mkdir(parents=True)
    (task / "task-state.yaml").write_text(
        yaml.safe_dump({
            "task": {"status": "ready_to_merge"},
            "scope": {"files": ["output/one.txt", "output/two.txt"]},
        }),
        encoding="utf-8",
    )
    (task / "architecture.md").write_text(
        "FILE: output/one.txt\none\nEND_FILE\n"
        "FILE: output/two.txt\ntwo\nEND_FILE\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(vv, "TASKS_ROOT", Path(".ai/tasks"))

    with pytest.raises(SystemExit, match="requires task status 'implementing'"):
        vv.materialize_blocks(task_id, "architecture.md", write=True)

    assert not (tmp_path / "output" / "one.txt").exists()
    assert not (tmp_path / "output" / "two.txt").exists()


def test_materialize_write_succeeds_while_implementing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_id = "20261014-materialize-implementing"
    task = tmp_path / ".ai" / "tasks" / task_id
    task.mkdir(parents=True)
    (task / "task-state.yaml").write_text(
        yaml.safe_dump({
            "task": {"status": "implementing"},
            "scope": {"files": ["output/result.txt"]},
        }),
        encoding="utf-8",
    )
    (task / "architecture.md").write_text(
        "FILE: output/result.txt\nresult\nEND_FILE\n", encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(vv, "TASKS_ROOT", Path(".ai/tasks"))

    vv.materialize_blocks(task_id, "architecture.md", write=True)

    assert (tmp_path / "output" / "result.txt").read_text(encoding="utf-8") == "result\n"


def test_compact_verify_formatting() -> None:
    output = vv.format_compact_verification(
        "# Verification — FAIL",
        [f"file-{index}.py" for index in range(12)],
        [("ruff", "PASS", ""), ("pytest", "FAIL", "\n".join(str(i) for i in range(45)))],
    )
    assert "Files: 12" in output
    assert "+2 more" in output
    assert "ruff: PASS" in output
    assert "pytest: FAIL" in output
    assert "truncated: 5 more lines" in output


def write_prompts(root: Path) -> None:
    prompts = root / ".ai" / "prompts"
    prompts.mkdir(parents=True)
    (prompts / "architect.md").write_text("# Architect {{TASK_ID}}\n", encoding="utf-8")
    (prompts / "review.md").write_text("# Review {{TASK_ID}} round {{ROUND}}\n", encoding="utf-8")


def test_architect_prompt_embeds_context_pack_and_large_file_toc(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = state()
    data["task"].update(status="waiting_architecture", owner="architect")
    data["scope"]["files"] = ["docs/big.md", "docs/small.md", "docs/missing.md"]
    task_id = write_task(tmp_path, data)
    write_prompts(tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "big.md").write_text("# Big\n\n## Part\n\n" + "x" * 21_000 + "\n", encoding="utf-8")
    (tmp_path / "docs" / "small.md").write_text("# Small\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    path, text = vv.render_prompt(task_id, "architect")

    assert text.startswith(f"# Architect {task_id}\n\n## Generated context pack")
    assert "phase=triage" in text
    assert "## Scope\n\nScope." in text
    assert "### docs/big.md" in text
    assert "## Part | L3-L5" in text
    assert "docs/small.md (" not in text
    assert path.read_text(encoding="utf-8") == text


def test_review_round_one_prompt_has_no_carry_over(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    task_id = write_task(tmp_path, state())
    write_prompts(tmp_path)
    monkeypatch.chdir(tmp_path)
    _, text = vv.render_prompt(task_id, "review", 1)
    assert text == f"# Review {task_id} round 1\n"


def test_review_round_two_carries_findings_dispositions_and_changed_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = state()
    data["task"].update(status="reviewing", owner="review")
    data["scope"]["files"] = ["src/a.py", "src/b.py", "src/c.py"]
    task_id = write_task(tmp_path, data)
    write_prompts(tmp_path)
    directory = tmp_path / ".ai" / "tasks" / task_id
    reviews = directory / "reviews"
    reviews.mkdir()
    (reviews / "round-1.md").write_text(
        "## Gate verdict\n\n| ID | Severity | Failure |\n|---|---|---|\n"
        "| GATE-001 | P1 | Breaks rerun. |\n| GATE-002 | P2 | Style. |\n\n"
        "### GATE-003 — P0 — Loses events\n\n- Evidence: x.\n\n### GATE-004 — P2 — Naming\n",
        encoding="utf-8",
    )
    decision = directory / "decision.md"
    decision.write_text(
        decision.read_text(encoding="utf-8")
        + "| GATE-001 | P1 | fixed |\n| GATE-003 | P0 | accepted-risk |\n| GATE-009 | P1 | backlog |\n",
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir()
    for name in ("a.py", "b.py", "c.py"):
        (tmp_path / "src" / name).write_text(f"{name} v1\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    snapshot = {
        "round": 1,
        "verdict": "FIX_REQUIRED",
        "findings": [
            {"id": "GATE-001", "severity": "P1"}, {"id": "GATE-002", "severity": "P2"},
            {"id": "GATE-003", "severity": "P0"},
        ],
        "files": {"src/a.py": vv._file_digest("src/a.py"), "src/b.py": vv._file_digest("src/b.py")},
    }
    (reviews / "round-1.json").write_text(json.dumps(snapshot), encoding="utf-8")
    (tmp_path / "src" / "a.py").write_text("a.py v2\n", encoding="utf-8")
    monkeypatch.setattr(vv, "_scoped_status_files", lambda *_: ["src/a.py", "src/b.py", "src/c.py"])

    _, text = vv.render_prompt(task_id, "review", 2)

    carry = text.split("## Round 1 carry-over", 1)[1]
    findings, rest = carry.split("### Dispositions in decision.md", 1)
    dispositions, changed = rest.split("### Files changed since round 1", 1)
    assert "| ID | Severity | Failure |" in findings
    assert "| GATE-001 | P1 | Breaks rerun. |" in findings
    assert "### GATE-003 — P0 — Loses events" in findings and "- Evidence: x." in findings
    assert "GATE-002" not in findings and "GATE-004" not in findings
    assert "| GATE-001 | P1 | fixed |" in dispositions
    assert "| GATE-003 | P0 | accepted-risk |" in dispositions
    assert "GATE-009" not in dispositions
    assert "- src/a.py | modified" in changed
    assert "- src/c.py | entered the diff after round 1" in changed
    assert "src/b.py" not in changed


def test_review_round_two_without_snapshot_falls_back_to_report_and_full_diff(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = state()
    data["task"].update(status="reviewing", owner="review")
    task_id = write_task(tmp_path, data)
    write_prompts(tmp_path)
    reviews = tmp_path / ".ai" / "tasks" / task_id / "reviews"
    reviews.mkdir()
    (reviews / "round-1.md").write_text("- SQL-007 P1 wrong merge key\n- SQL-008 P3 typo\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(vv, "_scoped_status_files", lambda *_: [])

    _, text = vv.render_prompt(task_id, "review", 2)

    assert "- SQL-007 P1 wrong merge key" in text
    assert "SQL-008" not in text
    assert "No round-1 snapshot" in text
