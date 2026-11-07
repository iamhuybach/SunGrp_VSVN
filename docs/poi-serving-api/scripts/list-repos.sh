#!/usr/bin/env bash
# Liệt kê toàn bộ repo trong ADO project Sun-Visit-VN.
#
# Chạy:
#     export AZDO_PAT=...        # PAT scope "Code: Read" — lấy từ secret/info.md (ngoài repo), khoá `tocken`
#     bash docs/poi-serving-api/scripts/list-repos.sh
#
# PAT đọc từ biến môi trường, không đọc file và không in token ra màn hình.
set -euo pipefail

ORG=${AZDO_ORG:-Sun-group}
PROJECT=${AZDO_PROJECT:-Sun-Visit-VN}

if [ -z "${AZDO_PAT:-}" ]; then
  echo "Thiếu AZDO_PAT. Xem hướng dẫn ở đầu file." >&2
  exit 1
fi

curl -sf -u ":${AZDO_PAT}" \
  "https://dev.azure.com/${ORG}/${PROJECT}/_apis/git/repositories?api-version=7.1" \
| python3 -c '
import sys, json
d = json.load(sys.stdin)
repos = sorted(d.get("value", []), key=lambda r: r["name"])
print(str(len(repos)) + " repos\n")
for r in repos:
    branch = str(r.get("defaultBranch")).replace("refs/heads/", "")
    print("  %-42s default=%-24s size=%s" % (r["name"], branch, r.get("size", 0)))
'
