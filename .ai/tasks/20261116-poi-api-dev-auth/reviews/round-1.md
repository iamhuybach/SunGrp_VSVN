## Model and reviewer manifest

- Model: `gpt-5.6-sol`, reasoning: `medium`
- `app-security-reviewer`: `PASS`
- `api-contract-reviewer`: `FIX_REQUIRED`
- Risk gate: not required

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `API-001` — **P1** — `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/config/OpenApiConfig.java:95`: OpenAPI documents the POI 401 response as `application/problem+json` with `ProblemDetail`, while `BearerTokenAuthenticationEntryPoint.java:40` returns the existing `ApiResponse` envelope as `application/json`. Fix by defining explicit 401 `application/json` content matching `ApiResponse` and documenting `WWW-Authenticate: Bearer`, so the generic problem-response customizer cannot replace it.

## Lower-severity findings

P2: 1; P3: 0.
