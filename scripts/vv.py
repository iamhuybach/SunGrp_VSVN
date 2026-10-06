#!/usr/bin/env python3
"""VSVN agent workflow helper (cross-platform, chỉ dùng thư viện chuẩn).

  python scripts/vv.py new <slug>                         tạo .ai/task/<YYYYMMDD-slug>/
  python scripts/vv.py handoff <task-id> claude|codex [--round N]
                                                          stage snapshot + sinh prompt
  python scripts/vv.py guard [--restore]                  FAIL nếu file ngoài .ai/task/ bị đổi
  python scripts/vv.py verify [<task-id>] [--all] [--allow-missing]
                                                          lint + test deterministic
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ALLOWED_PREFIX = ".ai/task/"          # vùng Claude/Codex được ghi
PROMPTS = {"claude": "claude-architect.md", "codex": "codex-gate.md"}


# ---------------------------------------------------------------- git helpers
def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-c", "core.quotepath=false", *args],
                       capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)} lỗi:\n{r.stderr.strip()}")
    return r


def z(out: str) -> list[str]:
    return [p for p in out.split("\0") if p]


def repo_root() -> Path:
    r = git("rev-parse", "--show-toplevel", check=False)
    if r.returncode != 0:
        sys.exit("Không phải git repo. Chạy `git init` trước.")
    return Path(r.stdout.strip())


def task_dir(task_id: str) -> Path:
    d = Path(".ai/task") / task_id
    if not d.is_dir():
        sys.exit(f"Không thấy task: {d}")
    return d


# ---------------------------------------------------------------- new
def cmd_new(a: argparse.Namespace) -> int:
    slug = re.sub(r"[^a-z0-9-]+", "-", a.slug.lower()).strip("-")
    if not slug:
        sys.exit("slug rỗng")
    tid = f"{dt.date.today():%Y%m%d}-{slug}"
    dst = Path(".ai/task") / tid
    if dst.exists():
        sys.exit(f"Đã tồn tại: {dst}")
    shutil.copytree(Path(".ai/task/_template"), dst)
    (dst / "evidence" / "results").mkdir(parents=True, exist_ok=True)
    for f in dst.rglob("*.md"):
        f.write_text(f.read_text(encoding="utf-8").replace("{{TASK_ID}}", tid), encoding="utf-8")
    print(tid)
    return 0


# ---------------------------------------------------------------- handoff
def cmd_handoff(a: argparse.Namespace) -> int:
    d = task_dir(a.task)
    tpl = Path(".ai/prompts") / PROMPTS[a.target]
    out = d / f"handoff-{a.target}-r{a.round}.md"
    text = tpl.read_text(encoding="utf-8")
    out.write_text(text.replace("{{TASK_ID}}", a.task).replace("{{ROUND}}", str(a.round)),
                   encoding="utf-8")
    git("add", "-A")          # snapshot: guard so sánh working tree với index này
    print(f"Snapshot đã stage. Prompt: {out.as_posix()}")
    print(f"→ Mở {'Claude Code' if a.target == 'claude' else 'Codex'}, gửi: "
          f"\"Thực hiện {out.as_posix()}\"")
    print("→ Xong phiên: python scripts/vv.py guard")
    return 0


# ---------------------------------------------------------------- guard
def changed_vs_index() -> list[str]:
    files = set(z(git("diff", "--name-only", "-z").stdout))
    files |= set(z(git("ls-files", "--others", "--exclude-standard", "-z").stdout))
    return sorted(f for f in files if not f.startswith(ALLOWED_PREFIX))


def cmd_guard(a: argparse.Namespace) -> int:
    bad = changed_vs_index()
    if not bad:
        print("GUARD PASS: không có thay đổi ngoài .ai/task/ so với snapshot.")
        return 0
    print("GUARD FAIL: file ngoài .ai/task/ bị thay đổi sau snapshot:")
    for f in bad:
        print(f"  {f}")
    if a.restore:
        tracked = set(z(git("ls-files", "-z").stdout))
        for f in bad:
            if f in tracked:
                git("checkout", "--", f)       # khôi phục từ index (snapshot)
            else:
                Path(f).unlink(missing_ok=True)
        print("Đã khôi phục về snapshot.")
    else:
        print("Xem diff: git diff   ·   Khôi phục: python scripts/vv.py guard --restore")
    return 1


# ---------------------------------------------------------------- verify
def changed_files(all_files: bool) -> list[str]:
    if all_files:
        files = set(z(git("ls-files", "-z").stdout))
    elif git("rev-parse", "--verify", "-q", "HEAD", check=False).returncode == 0:
        files = set(z(git("diff", "--name-only", "-z", "HEAD").stdout))
    else:
        files = set(z(git("ls-files", "-z").stdout))
    files |= set(z(git("ls-files", "--others", "--exclude-standard", "-z").stdout))
    return sorted(f for f in files if not f.startswith(".ai/") and Path(f).is_file())


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def run(cmd: list[str]) -> tuple[int, str]:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, (r.stdout + r.stderr).strip()


CHILD_LISTS = ("activities", "ifTrueActivities", "ifFalseActivities", "defaultActivities")


def walk_activities(acts: list, scope: str, all_names: list, errs: list) -> None:
    names = [x.get("name") for x in acts if isinstance(x, dict)]
    all_names.extend(names)
    local = set(names)
    for act in acts:
        if not isinstance(act, dict):
            continue
        name = act.get("name")
        for dep in act.get("dependsOn") or []:
            if dep.get("activity") not in local:
                errs.append(f"{scope}/{name}: dependsOn '{dep.get('activity')}' không có cùng cấp")
        tp = act.get("typeProperties") or {}
        for key in CHILD_LISTS:
            if isinstance(tp.get(key), list):
                walk_activities(tp[key], f"{scope}/{name}.{key}", all_names, errs)
        for case in tp.get("cases") or []:
            walk_activities(case.get("activities") or [], f"{scope}/{name}.case[{case.get('value')}]",
                            all_names, errs)


def check_json(paths: list[str]) -> tuple[str, str]:
    errs: list[str] = []
    for p in paths:
        try:
            doc = json.loads(Path(p).read_text(encoding="utf-8-sig"))
        except Exception as e:  # noqa: BLE001
            errs.append(f"{p}: JSON lỗi: {e}")
            continue
        acts = (doc.get("properties") or {}).get("activities") if isinstance(doc, dict) else None
        if isinstance(acts, list):
            names: list = []
            walk_activities(acts, p, names, errs)
            dup = sorted({n for n in names if names.count(n) > 1})
            if dup:
                errs.append(f"{p}: activity trùng tên: {', '.join(dup)}")
    return ("FAIL" if errs else "PASS"), "\n".join(errs)


def cmd_verify(a: argparse.Namespace) -> int:
    files = changed_files(a.all)
    py = [f for f in files if f.endswith((".py", ".ipynb"))]
    pg = [f for f in files if f.endswith(".pg.sql")]
    spark_sql = [f for f in files if f.endswith(".sql") and not f.endswith(".pg.sql")]
    js = [f for f in files if f.endswith(".json") and not f.startswith((".vscode/", ".claude/"))]
    tests = Path("tests")
    has_tests = tests.is_dir() and any(tests.rglob("test_*.py"))

    results: list[tuple[str, str, str]] = []

    def tool(name: str, module: str, cmd: list[str], targets: list[str]) -> None:
        if not targets:
            results.append((name, "SKIP", "không có file liên quan"))
            return
        if not has_module(module):
            status = "SKIP" if a.allow_missing else "FAIL"
            results.append((name, status, f"chưa cài '{module}': pip install -r requirements-dev.txt"))
            return
        code, out = run([sys.executable, "-m", module, *cmd, *targets])
        results.append((name, "PASS" if code == 0 else "FAIL", out))

    tool("ruff", "ruff", ["check", "--no-cache"], py)
    tool("sqlfluff[sparksql]", "sqlfluff", ["lint", "--dialect", "sparksql", "--nocolor"], spark_sql)
    tool("sqlfluff[postgres]", "sqlfluff", ["lint", "--dialect", "postgres", "--nocolor"], pg)
    if js:
        st, out = check_json(js)
        results.append(("json+pipeline", st, out))
    else:
        results.append(("json+pipeline", "SKIP", "không có file liên quan"))
    if has_tests:
        tool("pytest", "pytest", ["-q", "--no-header"], [str(tests)])
    else:
        results.append(("pytest", "SKIP", "chưa có tests/test_*.py"))

    failed = any(s == "FAIL" for _, s, _ in results)
    lines = [f"# verify {dt.datetime.now():%Y-%m-%d %H:%M:%S} — {'FAIL' if failed else 'PASS'}",
             f"files ({len(files)}): " + (", ".join(files) if files else "none"), ""]
    for name, st, out in results:
        lines.append(f"## {name}: {st}")
        if out:
            lines.append(out)
        lines.append("")
    report = "\n".join(lines)
    print(report)
    if a.task:
        log = task_dir(a.task) / "verify.log"
        with log.open("a", encoding="utf-8") as fh:
            fh.write(report + "\n")
        print(f"(đã ghi {log.as_posix()})")
    return 1 if failed else 0


# ---------------------------------------------------------------- main
def main() -> int:
    import os
    os.chdir(repo_root())
    p = argparse.ArgumentParser(prog="vv", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("new")
    s.add_argument("slug")
    s.set_defaults(fn=cmd_new)

    s = sub.add_parser("handoff")
    s.add_argument("task")
    s.add_argument("target", choices=sorted(PROMPTS))
    s.add_argument("--round", type=int, default=1)
    s.set_defaults(fn=cmd_handoff)

    s = sub.add_parser("guard")
    s.add_argument("--restore", action="store_true")
    s.set_defaults(fn=cmd_guard)

    s = sub.add_parser("verify")
    s.add_argument("task", nargs="?")
    s.add_argument("--all", action="store_true", help="kiểm tra toàn repo thay vì file thay đổi")
    s.add_argument("--allow-missing", action="store_true", help="tool chưa cài → SKIP thay vì FAIL")
    s.set_defaults(fn=cmd_verify)

    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
