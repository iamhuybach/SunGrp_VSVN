## Model and reviewer manifest

- Model: `gpt-5.6-sol`, reasoning: `medium`
- Specialist reviewers: none required
- Risk gate: completed

## Gate verdict

`USER_DECISION`

## P0/P1 findings

- **GATE-001 — P1 — `docs/poi-serving-api/API-GAPS.md:39`**: The documented S2S Bearer-authentication contract is not enforced by the service, allowing unauthenticated access to PostgreSQL-backed POI data. **Fix:** Decide whether authentication belongs in the service or upstream gateway, record that boundary in architecture, and add a negative unauthenticated-request test.
- **GATE-002 — P1 — `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/config/OpenApiConfig.java:46`**: OpenAPI embeds an internal DEV hostname, violating the architecture invariant prohibiting DEV hostnames in the repository. **Fix:** Remove or environment-parameterize the server URL and scan the implementation paths for remaining DEV hostnames.

## Lower-severity findings

P2: 4 · P3: 0
