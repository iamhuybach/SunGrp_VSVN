# Request

## User outcome

Every endpoint under `/api/v1/pois` rejects a call that has no `Authorization` header, a scheme other than Bearer, or a token that does not match the configured secret, with HTTP 401 and the existing `GlobalExceptionHandler` error envelope. A request with `Authorization: Bearer <token>` continues with the same status and body as today. `GET /actuator/health` stays open with no token. A blank or missing token configuration does not open `/api`. The secret is never logged and never returned in a response body.

## Scope

### In scope

- One shared environment variable for local dev and Kubernetes deploy, declared in `services/data-serving-service/src/main/resources/application.yml` and in a new `services/data-serving-service/.env.example`, both with an empty value.
- Local dev: `services/data-serving-service/.env` (already gitignored) receives one generated random token. `docker-compose.yml` passes that variable through from `.env` and does not hard-code a token.
- Deploy: one Kubernetes ConfigMap manifest whose data is a placeholder, not the generated token, and which references the same variable name.
- Constant-time comparison of the presented token with the configured value.
- Java tests use a fixed token stored under `services/data-serving-service/src/test/resources`. Tests do not read `.env`.
- Request-header tables in `docs/context/api-mapping/compact.md`, `gallery.md`, `reviews.md`, `features.md`, `experiences.md`, `practical_info.md`, and `amenities.md`: add `Authorization` with Required = `có`. Do not change the Required value of any other field.
- `scope.systems`: `poi-serving-api`.

### Out of scope

- Query text, business DTOs, entities, gold columns, and PostgreSQL DDL.
- Files under `docs/poi-serving-api/`.
- Mapping files whose names start with `(ood)`.
- Task `20261110-serving-poi-read-apis`.
- Committing `.env`, or committing any change in this task until the user asks.
- Writing the generated token into `request.md`, `decision.md`, `resume.md`, mapping docs, tests, the verify log, or `evidence/`.

## Acceptance criteria

- For each current `/api/v1/pois` endpoint (compact, features, gallery, reviews, experiences, practical_info, amenities): missing token and wrong token return HTTP 401 with the existing error envelope; the correct Bearer token keeps the status the endpoint had before this change.
- `GET /actuator/health` returns without a token.
- `python scripts/vv.py verify 20261116-poi-api-dev-auth` passes when Docker is available.
- Reviewers: `app-security-reviewer` and `api-contract-reviewer`.
- `.env` is not committed. The generated token appears only in `.env` and once in the final chat message.

## Constraints

- Do not log the token and do not put it in the response body.
- Compare tokens in constant time.
- A blank or absent configuration must not let `/api/v1/pois` succeed. `GET /actuator/health` must still respond without a token, including when the token is blank, because the healthcheck calls that path. Paths outside `/api/v1/pois` keep their current unauthenticated behavior unless a listed file must change to keep health and the POI routes apart.
- The 401 body is the existing `ApiResponse` error envelope from `GlobalExceptionHandler` (`success`, `code`, `message`, `data`, `meta`, `errors`). `meta` still carries `trace_id` from `RequestIdFilter`.
- One variable name for dev and deploy. `.env.example` and the ConfigMap data value are empty or a non-secret placeholder. The random token is written only to the gitignored `.env`.
- Tests must not read `.env`. The fixed test token lives under `src/test/resources`.
- Do not read `services/data-serving-service/.env` into an artifact. It may already hold local database secrets.
- No `data_model_change`. Do not change query, business DTO, or DDL.
- Runtime proof is a user-run `docker compose` smoke. Main stops before that command. The runbook covers loading `.env`, one POI call with no token, one with a wrong token, one with the correct token, and `GET /actuator/health`.

## Classification rationale

- Complexity: `medium`. The change adds an auth boundary on every POI route, a new Kubernetes manifest, compose wiring, and seven mapping tables. It is still one service and one comparison.
- Risk: `medium`. HTTP behavior changes on every POI endpoint, rollback is removing the filter and the variable, and local tests can prove 401 versus the previous success status. It is not high: there is no CDC, watermark, lock, or data-loss path.
- Architecture: required. The HTTP contract changes, and the same secret is attached in two ways (gitignored `.env` for dev, ConfigMap for deploy). Material design choices remain: how a filter or `SecurityFilterChain` renders the existing envelope (controller advice does not see a filter rejection), how a blank secret closes `/api` while `/actuator/health` stays up, and which paths stay anonymous. `design_tradeoffs` applies. The edit set is also more than eight source files. `data_model_change` does not apply.
- Evidence: not required. Correctness is the configured string and the HTTP contract, both provable from the repository and deterministic tests. No Fabric probe.
- Runtime proof: required. Acceptance includes a user-run compose smoke. `runtime_proof_required` applies. Main does not run `docker compose`.
- Reviewer routing: `app-security-reviewer` because the diff touches `common/web/`, `config/`, `application.yml`, `pom.xml`, and Docker or Kubernetes files. `api-contract-reviewer` because the HTTP status and error envelope of `/api/v1/pois` change and the mapping tables change. `jpa-performance-reviewer` is not required: no repository, service query, entity, or DDL edit. `risk-gate` is not required at `medium` risk.
