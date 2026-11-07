import hashlib
import io
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

SRC = r"D:\git\SunGrp_VSVN_API"
COMMIT = "20bca8a"
DEST = Path(r"d:\git\SunGrp_VSVN\services\data-serving-service")
DOCS_DEST = Path(r"d:\git\SunGrp_VSVN\docs\poi-serving-api")
WRITE = "--write" in sys.argv

tree = {}
for line in subprocess.run(["git", "-C", SRC, "ls-tree", "-r", COMMIT], capture_output=True, check=True, text=True).stdout.splitlines():
    meta, path = line.split("\t", 1)
    tree[path] = meta.split()[2]

data = subprocess.run(["git", "-C", SRC, "archive", "--format=tar", COMMIT], capture_output=True, check=True).stdout
members = {}
with tarfile.open(fileobj=io.BytesIO(data)) as tar:
    for m in tar.getmembers():
        if m.isfile():
            members[m.name] = tar.extractfile(m).read()

assert set(members) == set(tree), "archive and ls-tree differ"
service = {p: b for p, b in members.items() if p != ".env.example" and not p.startswith("docs/")}
docs = {p[len("docs/poi-serving-api/"):]: b for p, b in members.items() if p.startswith("docs/")}
print(f"tracked={len(tree)} service={len(service)} docs={len(docs)}")
if len(service) != 55 or len(docs) != 6:
    sys.exit("COUNT MISMATCH")

def blob_id(body: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(body) + body).hexdigest()

bad = [p for p, b in members.items() if blob_id(b) != tree[p]]
print(f"archive bytes == git blob: {not bad} {bad}")

plan = [(DEST / p, b, p) for p, b in service.items() if p != ".gitignore"] + [(DOCS_DEST / p, b, "docs/poi-serving-api/" + p) for p, b in docs.items()]
for target, body, _ in plan:
    if target.exists():
        sys.exit(f"TARGET EXISTS: {target}")
if WRITE:
    for target, body, _ in plan:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
    mismatch = [src for target, body, src in plan if hashlib.sha256(target.read_bytes()).hexdigest() != hashlib.sha256(body).hexdigest()]
    print(f"written={len(plan)} sha256_mismatch={mismatch}")
    if mismatch:
        sys.exit("SHA MISMATCH")
else:
    print(f"dry-run planned={len(plan)} (service {len(service) - 1} + docs {len(docs)}; .gitignore kept from row 2.6)")
