"""Local probe: compare apps.srv_poi_* columns between the API Flyway V1 and sql/postgres/gld_srv_serve.pg.sql.

Read-only. Prints table, column, type in each file and the primary keys. No data values.
Usage: python .ai/tasks/20261106-agent-system-unify-api/evidence/probes/api_schema_diff.py <api_root>
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
TABLE_RE = re.compile(r"CREATE TABLE(?: IF NOT EXISTS)?\s+apps\.(\w+)\s*\((.*?)\n\);", re.S)


def parse(path: Path) -> dict[str, dict]:
    text = re.sub(r"--[^\n]*", "", path.read_text(encoding="utf-8"))
    tables = {}
    for name, body in TABLE_RE.findall(text):
        cols, pk = {}, []
        for line in body.split("\n"):
            line = line.strip().rstrip(",")
            if not line:
                continue
            m = re.match(r"PRIMARY KEY\s*\((.*?)\)", line, re.I)
            if m:
                pk = [c.strip() for c in m.group(1).split(",")]
                continue
            parts = line.split()
            col, rest = parts[0], " ".join(parts[1:])
            if re.search(r"PRIMARY KEY", rest, re.I):
                pk = [col]
            typ = re.sub(r"\s+(NOT NULL|PRIMARY KEY)", "", rest, flags=re.I).strip().lower()
            typ = typ.replace("timestamp without time zone", "timestamp")
            cols[col] = typ
        tables[name] = {"cols": cols, "pk": pk}
    return tables


def main() -> None:
    api_root = Path(sys.argv[1])
    flyway = parse(api_root / "src/main/resources/db/migration/V1__init_srv_poi_tables.sql")
    repo = parse(REPO / "sql/postgres/gld_srv_serve.pg.sql")
    for table in sorted(set(flyway) | set(repo)):
        f, r = flyway.get(table), repo.get(table)
        if not f or not r:
            print(f"{table}: only in {'flyway' if f else 'repo_pg'}")
            continue
        print(f"{table}: flyway_cols={len(f['cols'])} repo_pg_cols={len(r['cols'])} "
              f"pk_flyway={f['pk']} pk_repo_pg={r['pk']}")
        for col in sorted(set(f["cols"]) | set(r["cols"])):
            ft, rt = f["cols"].get(col), r["cols"].get(col)
            if ft != rt:
                print(f"  DIFF {col}: flyway={ft} repo_pg={rt}")


if __name__ == "__main__":
    main()
