## Model and reviewer manifest

- Model: `gpt-5.6-sol`, reasoning: `medium`
- Reviewers: `app-security-reviewer`, `api-contract-reviewer`
- Risk gate: not required
- `API-001`: resolved

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `API-002` — **P1** — `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/config/OpenApiConfig.java:55`: Root-level `bearerAuth` describes every documented operation as protected, conflicting with anonymously accessible operations. Attach the security requirement only to operations whose paths start with `/api/v1/pois`, rather than globally.

## P2/P3

0
