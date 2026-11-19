# Codex review handoff: 20261119-gsm-as-google-extract, round 3

You are the VSVN Review Coordinator. Use the project agents in `.codex/agents/`.

Confirm the active model is `gpt-5.6-sol` with `medium` reasoning. Stop and report a model mismatch instead of silently substituting.

Read `architecture.md` when it exists, the open items in `decision.md`, and the implementation diff. Do not read the rest of the repository, past reviews, or evidence files unless one finding depends on a named path.

For round 1, invoke every reviewer named in `review_plan.required_reviewers` independently. Spawn each project custom agent without a full-history fork and without another specialist's findings. For round 2, use the generated round-1 carry-over at the end of this prompt: pass each specialist only the round-1 P0/P1 findings it owns, their dispositions, and the diff of the files listed as changed since round 1 (`git diff -- <path>`, or the file itself when untracked). Invoke `risk-gate` after the specialist results when task state requires it. Risk-gate reads those findings and the diff, not the whole repository.

Specialists are read-only. Do not edit repository files.

Return one short consolidated Markdown report:

1. Model and reviewer manifest.
2. Gate verdict: `PASS`, `FIX_REQUIRED`, `EVIDENCE_REQUIRED`, or `USER_DECISION`.
3. Deduplicated P0/P1 findings: ID, severity, `file:line`, one-sentence failure, one-sentence fix.
4. P2/P3 as a count.
5. One probe line when evidence is missing.

Do not promote style issues to P0/P1. Do not write a repository tour.

## Round 2 carry-over

`vv.py` generated this block. Use it instead of opening past review files. Re-check each round-2 P0/P1 against its disposition, then review only the changed files below for regressions caused by the fixes.

### Round 2 P0/P1 findings

- `PIPE-001` — P1 — `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:187`: Một wave `sgm` thông thường có thể ghi thành công bảng con nhưng thất bại ở `slv_3p_poi`; Google cũ hơn ở lần retry không được nhận diện là takeover, nên state/MERGE guard có thể để dữ liệu parent Google và child SGM lệch lâu dài. Fix: chạy và gate `slv_3p_poi` trước các bảng con cho wave `sgm`, hoặc lưu ownership độc lập/atomic; thêm test parent-failure/child-success rồi replay Google cũ hơn để chứng minh mọi bảng hội tụ.

### Dispositions in decision.md

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| PIPE-001 | P1 | fixed | Không takeover: `slv_3p_poi` chạy trước. Bảng con chỉ chạy khi `slv_3p_poi` là SUCCESS hoặc NO_DATA. Parent lỗi thì bảng con SKIPPED, không commit state. Lần sau Google cũ hơn vẫn thấy owner `sgm` nếu parent đã ghi, hoặc cả hai cùng chạy lại nếu parent chưa ghi. | |

### Files changed since round 2

- docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md | entered the diff after round 2
- notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb | modified
- tests/test_3p_sgm_identity_contract.py | entered the diff after round 2
