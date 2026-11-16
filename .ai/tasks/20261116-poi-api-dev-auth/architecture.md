RESULT: PASS

## Main brief

### Decision
Protect `/api/v1/pois` and `/api/v1/pois/**` with a Spring Security `SecurityFilterChain`. An `AuthorizationManager` compares SHA-256 digests with `MessageDigest.isEqual`, and every other path uses `anyRequest().permitAll()`.
A custom `BearerTokenAuthenticationEntryPoint` writes the 401 as `ApiResponse.error(UNAUTHORIZED, "Missing or invalid bearer token.", "ERR_UNAUTHORIZED")` with `WWW-Authenticate: Bearer`.
The env var `POI_API_BEARER_TOKEN` binds to `app.security.poi-api.bearer-token` through `${POI_API_BEARER_TOKEN:}`. A blank value means every POI call returns 401, and the app still starts.
The test token is fixed in `src/test/resources/application.yml`. `poi-api-bearer-token.txt` is NOT created, because `@DynamicPropertySource` would block the blank-config override test.
`.env.example` and the ConfigMap value stay empty. The design recommends a Secret at deploy time as a follow-up; this does not block the task.

### Invariants Main must preserve
- Without a valid token, any method on any `/api/v1/pois/**` path (mapped or not) returns 401 before routing: `GET /compact` returns 401, not 405. `PoiService` is never called.
- With the correct token, every existing `PoiControllerIntegrationTest` expectation is unchanged after adding only the header.
- Blank, whitespace, or absent config rejects every POI request (including `Bearer ` with an empty value). The app still starts, and `/actuator/health` returns 200 without a token.
- The 401 body has `success=false`, `code=401`, the fixed message, `data=null`, `errors=null`, `meta.error_code=ERR_UNAUTHORIZED`, and `meta.trace_id` equal to the incoming `X-Request-Id`. It is the same for every failure reason.
- Write the 401 directly to the response. Never call `response.sendError`.
- No token in any log, body, exception message, or `toString`. Do not use `@EnableWebSecurity(debug=true)` or a request-logging filter.
- No `UserDetailsService` bean, so Boot never logs "Using generated security password".
- Do not change `RequestIdFilter`'s order or `spring.security.filter.order`.
- Tests never read `.env`. The generated token appears only in `.env` and once in the final chat message.
- `.env.example` and `k8s/configmap.yaml` have an empty `POI_API_BEARER_TOKEN`. A non-empty placeholder is forbidden.

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| 1 | services/data-serving-service/pom.xml | `<dependencies>` | Add `spring-boot-starter-security`, and `spring-boot-starter-security-test` (test scope; if it does not resolve, use `org.springframework.security:spring-security-test`) | `mvnw.cmd -q -B test-compile` passes |
| 2 | .../config/ApiBearerTokenProperties.java (new) | record | Per "Code: ApiBearerTokenProperties"; `toString` masks the value | compiles; `propertiesToStringNeverContainsToken` passes |
| 3 | .../common/web/BearerTokenAuthenticationEntryPoint.java (new) | class | Per "Code: BearerTokenAuthenticationEntryPoint": implements `AuthenticationEntryPoint` and `AccessDeniedHandler`; static Jackson 2 `ObjectMapper`; not a `@Component` | 401 envelope tests pass |
| 4 | .../config/SecurityConfig.java (new) | `securityFilterChain`, `noLoginAuthenticationManager`, `PoiBearerTokenVerifier`, `Outcome` | Per "Code: SecurityConfig" | ApiBearerAuthTest passes |
| 5 | .../config/OpenApiConfig.java | `dataServingApiOpenApi` | Add `bearerAuth` HTTP bearer scheme and a global security item; keep the signature | `openApiDocsDeclareBearerAuthAndStayOpen` passes; OpenApiConfigTest still passes |
| 6 | .../config/OpenApiConfig.java | `problemResponsesCustomizer` | Iterate `(path, pathItem)`; `putIfAbsent("401", ...)` for paths starting with `/api/v1/pois` | the 401 response exists in api-docs |
| 7 | src/main/resources/application.yml | new top-level `app:` after `springdoc:` | `app.security.poi-api.bearer-token: ${POI_API_BEARER_TOKEN:}` | `mainApplicationYmlBindsBearerTokenFromPoiApiBearerTokenEnv` passes |
| 8 | src/test/resources/application.yml | end of file | `app.security.poi-api.bearer-token: test-only-poi-api-token-not-a-secret` | tests inject it via `@Value` |
| 9 | .../api/PoiControllerIntegrationTest.java | `@Import` + every `perform(...)` | Add `SecurityConfig.class`; `@Value` token; `authorized(...)` helper wraps every builder; no expectation changes | all 21 existing tests pass |
| 10 | .../config/ApiBearerAuthTest.java (new) | class | Per "Tests: ApiBearerAuthTest" | all named tests pass |
| 11 | .../DataServingApplicationTests.java | class | Add the 4 tests from "Tests: DataServingApplicationTests"; existing health and OpenAPI tests keep no token | passes with Docker |
| 12 | services/data-serving-service/docker-compose.yml | `data-serving-service.environment` | `POI_API_BEARER_TOKEN: ${POI_API_BEARER_TOKEN:-}` (not `:?`) | no hard-coded token |
| 13 | services/data-serving-service/.env.example (new) | whole file | Save the FILE block verbatim | empty values |
| 14 | services/data-serving-service/k8s/configmap.yaml (new) | whole file | Save the FILE block verbatim | data value `""` |
| 15 | services/data-serving-service/AGENTS.md | `## Contract` | New auth bullet per "Docs: AGENTS.md" | text present |
| 16 | services/data-serving-service/AGENTS.md | `## Commands` (Local run) | `.env.example` + token generation hint | text present |
| 17 | services/data-serving-service/AGENTS.md | `## Environment variables` | Add `POI_API_BEARER_TOKEN`, the ConfigMap/Secret note, and the deploy ordering | text present |
| 18 | services/data-serving-service/AGENTS.md | `## Layout` | Test token location; `@WebMvcTest` imports `SecurityConfig` | text present |
| 19 | 7 mapping docs (compact, gallery, reviews, features, experiences, practical_info, amenities) | `## Request header` | Append a last `Authorization` row, Required `có`, next Stt, no renumbering | 7 files changed; no other Required value changed |
| 20 | same 7 docs | `## Status code` | Insert a `401 | ERR_UNAUTHORIZED` row in numeric order | present in 7 files |
| 21 | same 7 docs | `## Sample request` | Add `Authorization: Bearer <token>` (literal placeholder) | present in 7 files |
| 22 | services/data-serving-service/.env (gitignored, not committed) | append | Run the "Dev token generation" script | prints `appended`; never printed the token |
| 23 | task runtime-runbook.md | whole file | Content from "Runtime runbook content" | runbook ready |
No change: GlobalExceptionHandler.java, RequestIdFilter.java, GlobalExceptionHandlerTest.java, RequestIdFilterTest.java, .gitignore.

### Order and stop points
1. Row 1. Run `mvnw.cmd -q -B test-compile`. STOP (evidence) if neither security test artifact resolves; report the Maven error.
2. Rows 2–6. Compile. If a Spring Security 7 or Boot 4 API name differs, adjust the spelling only and keep the invariants.
3. Rows 7–11. Run the targeted tests. STOP (evidence) if the slice tests show the security chain is not applied (missing-token requests return 200), or if `meta.trace_id` does not match `X-Request-Id` (filter order). Report the output and do not reorder filters.
4. Rows 12–21.
5. Full `mvnw.cmd -q -B test`, then `python scripts/vv.py verify 20261116-poi-api-dev-auth`.
6. Row 22. STOP (user decision) if the script reports the key already exists: ask whether to keep or replace it.
7. Run the leak check. STOP if any file is listed.
8. Row 23. STOP (evidence, user-run) for the `docker compose` smoke. Main does not run docker.
9. Do not commit. In the final message, print the token once, read immediately before the message, and only there.

### Tests and verification
- `cd services/data-serving-service && mvnw.cmd -q -B test -Dtest=ApiBearerAuthTest,PoiControllerIntegrationTest,OpenApiConfigTest`
- `cd services/data-serving-service && mvnw.cmd -q -B test`
- `python scripts/vv.py verify 20261116-poi-api-dev-auth`
- ApiBearerAuthTest: `missingAuthorizationReturns401Envelope`, `wrongTokenReturns401`, `nonBearerSchemeReturns401`, `correctTokenReachesController` (all parameterized over 7 endpoints), `bearerSchemeIsCaseInsensitive`, `emptyBearerTokenReturns401`, `duplicateAuthorizationHeadersReturn401`, `unauthorizedBodyCarriesTraceIdAndNeverEchoesToken`, `authPrecedesRoutingForWrongMethodAndUnknownPath`, `pathsOutsidePoiApiStayAnonymous`; nested `BlankTokenConfiguration`: `blankConfigurationRejectsEveryPoiRequest`, `blankConfigurationKeepsNonPoiPathsOpen`; unit tests: `verifierTreatsNullBlankAndWhitespaceConfigAsNotConfigured`, `verifierStripsConfiguredWhitespace`, `verifierOutcomes`, `propertiesToStringNeverContainsToken`, `mainApplicationYmlBindsBearerTokenFromPoiApiBearerTokenEnv`.
- DataServingApplicationTests: `poiEndpointWithoutTokenReturns401Envelope`, `poiEndpointWithTokenReturns200`, `openApiDocsDeclareBearerAuthAndStayOpen`, `noDefaultUserDetailsServiceIsCreated`, and the existing `healthEndpointReturnsUp` (no token).
- PoiControllerIntegrationTest: all existing tests, with the token added and no expectation changes.
- Leak check script (full document); `git check-ignore services/data-serving-service/.env`.
- User-run runbook steps 1–8. Expected: health 200; no token 401; wrong token 401; correct token 200; log reasons `MISSING_HEADER` and `TOKEN_MISMATCH`.

### Read only if needed
- Scope / Non-goals → rows 1–23 boundaries, "No change" list
- Invariants → all rows
- Ordering → rows 3, 4, stop 3
- Security → rows 4, 12, 14, 17 (CSRF disabled, firewall, headers, ConfigMap vs Secret)
- Alternatives and trade-off → rows 3, 4, 8 (why no .txt, why no HandlerExceptionResolver)
- Observability → row 4 log lines
- Rollout / Rollback and forward recovery → row 17
- Implementation plan: Code: pom.xml → 1; Code: ApiBearerTokenProperties → 2; Code: BearerTokenAuthenticationEntryPoint → 3; Code: SecurityConfig → 4; Code: OpenApiConfig → 5, 6; Config sections → 7, 8, 12; Tests sections → 9, 10, 11; Docs sections → 15–21; Dev token generation → 22; Leak check → stop 7; Runtime runbook content → 23
- Proposed decision ledger rows → record D-1..D-6 in decision.md

# Architecture: Bearer token for /api/v1/pois (20261116-poi-api-dev-auth)

Risk medium. No `data_model_change`. `model-design.md` is not needed: no table, column, grain, or key changes.

## Scope

- Add Spring Security to `services/data-serving-service`. Use one `SecurityFilterChain`. Paths `/api/v1/pois` and `/api/v1/pois/**` require `Authorization: Bearer <token>`, and the token must equal the configured secret. Every other path uses `permitAll()`.
- One variable name for dev and deploy: `POI_API_BEARER_TOKEN`. It binds to `app.security.poi-api.bearer-token` through `${POI_API_BEARER_TOKEN:}` in the main `application.yml`.
- The 401 response is the existing `ApiResponse` error envelope, built with `ApiResponse.error(...)` (the same factory `GlobalExceptionHandler` uses), with `meta.error_code = ERR_UNAUTHORIZED` and `meta.trace_id` from `RequestIdFilter`.
- Files: `pom.xml`, the new `SecurityConfig`, `ApiBearerTokenProperties`, and `BearerTokenAuthenticationEntryPoint`, `OpenApiConfig` (bearer scheme and 401), both `application.yml` files, `docker-compose.yml`, the new `.env.example`, the new `k8s/configmap.yaml`, the service `AGENTS.md`, three test classes, and seven mapping docs.
- Files in scope that need no change: `GlobalExceptionHandler.java`, `RequestIdFilter.java`, `GlobalExceptionHandlerTest.java`, `RequestIdFilterTest.java`, `.gitignore` (it already ignores `.env` and does not ignore `.env.example`), and `src/test/resources/poi-api-bearer-token.txt`. That last file is **not created**; the reason is under "Alternatives" item 4.

## Non-goals

- No users, roles, JWT, OAuth2, rate limiting, or multiple simultaneous tokens (zero-downtime rotation).
- No auth on actuator, `/v3/api-docs`, or `/swagger-ui.html`. `metrics` and `prometheus` remain anonymous as today. That exposure already exists, so it is a separate follow-up.
- No change to queries, DTOs, entities, DDL, `docs/poi-serving-api/`, or `(ood)` mapping files.
- No Kubernetes Deployment manifest. Only the ConfigMap the request names.
- No fix for the existing mismatch where OpenAPI documents error bodies as `application/problem+json`.
- No commit, and no `docker compose` run by Main.

## Invariants

- I1. Under `/api/v1/pois/**` (any method, any sub-path, including unmapped ones), a request with no valid Bearer token gets HTTP 401 before routing. That means 401 and not 405/415/404/422, and the controller, service, and database are never called.
- I2. A request with the correct token gets exactly the status and body it gets today. Every existing `PoiControllerIntegrationTest` assertion passes once the token header is added.
- I3. A blank, whitespace-only, or absent configured token rejects every POI request, including `Bearer ` with an empty value. The application still starts, and `/actuator/health` returns without a token.
- I4. Paths outside `/api/v1/pois/**` keep anonymous access. Only the generic Spring Security response headers and firewall rejection of malformed URLs are new (see Security).
- I5. The 401 body has the fields `success=false`, `code=401`, `message="Missing or invalid bearer token."`, `data=null`, `errors=null`, `meta.timestamp`, `meta.trace_id` (equal to an incoming `X-Request-Id` when present), and `meta.error_code=ERR_UNAUTHORIZED`. The response has `WWW-Authenticate: Bearer` and `X-Request-Id`. All failure reasons get the same body, so the response does not reveal why a request failed.
- I6. The comparison is SHA-256 of the presented token and of the configured token, compared with `MessageDigest.isEqual`. The time does not depend on the secret's length or content.
- I7. No log line, response body, exception message, or `toString()` contains the configured or presented token. Do not enable `@EnableWebSecurity(debug = true)`, and do not add a request-logging filter.
- I8. The 401 is written directly to the response. Never call `response.sendError(401)`, because that dispatches to Boot's `/error` and changes the body.
- I9. Tests never read `.env`. The test token is fixed in `src/test/resources/application.yml`. The generated token exists only in the gitignored `.env` and once in the final chat message.
- I10. `.env.example` and the ConfigMap value are **empty**. A non-empty placeholder would become a working credential if nobody replaced it.

## State ownership

- The secret's source of truth is the process environment: dev `.env` → compose interpolation → container env. Deploy: ConfigMap (or whatever the pipeline injects) → container env.
- The application reads it once at startup into an immutable SHA-256 digest held by `PoiBearerTokenVerifier`. Nothing is persisted, and nothing is in the database or a session.
- Rotation means changing the env value and restarting. Nothing reloads it at runtime.

## Grain and keys

Not applicable: no table, column, grain, or key changes.

## Ordering

Servlet filter order (lower runs first):
1. `RequestIdFilter` (`Ordered.HIGHEST_PRECEDENCE`) sets the request attribute and MDC `trace_id`, and sets the `X-Request-Id` response header.
2. Boot `OrderedRequestContextFilter` (-105) populates `RequestContextHolder`, which `ApiResponse.error` reads. MDC is the fallback.
3. `springSecurityFilterChain` (-100, Boot default `spring.security.filter.order`). Inside it: firewall, headers, anonymous authentication, `AuthorizationFilter`. When the token is invalid, `ExceptionTranslationFilter` calls `BearerTokenAuthenticationEntryPoint`.
4. `DispatcherServlet`. Handler mapping runs here, which is why 405/415/404 only happen after authorization passes.

Do not change `RequestIdFilter`'s order or `spring.security.filter.order`. The 401 `trace_id` test catches a regression.

## Transaction and commit boundaries

Not applicable: authorization finishes before any handler runs. Rejected requests open no transaction and use no database connection.

## Idempotency

- HTTP: authorization is a pure function of the header and the startup digest. Repeating a call gives the same outcome.
- `.env` generation (Main): the script appends the key only when it is absent. If the key exists, the script exits non-zero without overwriting it, which is a stop point for the user.

## Concurrency

The verifier is immutable. Each call creates its own `MessageDigest`, because a shared instance is not thread-safe. There are no shared mutable fields. This is safe with `spring.threads.virtual.enabled=true`.

## Retry and recovery

A client cannot recover from a 401 by retrying. It must send the correct token. Server recovery from a blank or wrong config means setting `POI_API_BEARER_TOKEN` and restarting the container or pod. Health stays green meanwhile (I3), so the orchestrator does not restart-loop, and the startup WARN shows the cause.

## Partial failure

- Missing config: fail closed (I3) with a WARN at startup.
- Serializing the envelope in the entry point throws `IOException`. That propagates to the container and the client sees a 500 with no body. No secret is involved, and Jackson can always serialize the envelope, a fixed record with string fields.
- Dev `.env` is CRLF-encoded: the configured value is `strip()`ed before hashing, so a trailing `\r` or whitespace does not lock users out.

## Observability

- Startup: one WARN `poi_api_auth token_configured=false; every /api/v1/pois request returns 401 until POI_API_BEARER_TOKEN is set` when the token is blank. Nothing is logged when it is set.
- Each rejection logs INFO `poi_api_auth_rejected reason={NOT_CONFIGURED|MISSING_HEADER|MULTIPLE_HEADERS|NOT_BEARER|EMPTY_TOKEN|TOKEN_MISMATCH} method=<m> trace_id=<id>`. It logs no path, header, or token. The reason is logged server-side only and never returned.
- `http.server.requests` metrics include 401s, because the observation filter is ordered before security. The `uri` tag may be `UNKNOWN` for rejections that happen before handler mapping.

## Security

- Threats addressed: unauthenticated access, timing oracle (I6), secret leakage through logs, body, or `toString` (I7, and the record overrides `toString`), path-normalization bypass, and placeholder-as-credential (I10).
- Path bypass: Spring MVC strips `;params` from path segments. A hand-written `startsWith("/api/v1/pois")` would therefore miss `/api/v1;x/pois/compact`, which still routes to `PoiController`. Spring Security's `StrictHttpFirewall` rejects `;`, `//`, encoded `/`, `%25`, `..`, backslashes, and encoded CR/LF before matching. `PathPatternRequestMatcher` then matches `/api/v1/pois/**`, including trailing-slash and unmapped sub-paths.
- CSRF is disabled. That is safe here: the service uses no cookies and no sessions (`STATELESS`), and browsers never attach the Bearer header automatically. If CSRF stayed on, Spring Security would reject `POST /compact` with 403.
- HTTP Basic, form login, logout, and request cache are disabled. The `AuthenticationManager` bean rejects everything, so Boot does not build its `InMemoryUserDetailsManager` and does not log "Using generated security password". A test proves no `UserDetailsService` bean exists.
- Default security headers now appear on all responses: `Cache-Control: no-cache, no-store, max-age=0, must-revalidate`, `Pragma`, `Expires: 0`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 0`, and HSTS on HTTPS only. Bodies and statuses are unchanged. `no-store` is correct for authorized responses.
- ConfigMap versus Secret: a bearer token is a secret, and ConfigMaps are readable by anyone who can read the namespace's ConfigMaps. The request names a ConfigMap, so this design follows it with an empty value. I recommend the deploy pipeline inject the real value from a Kubernetes `Secret` or a secret manager under the same variable name. That is a deploy follow-up and does not block this task. `api-contract-reviewer` and `app-security-reviewer` should see this note.
- `docker inspect` and `/proc/<pid>/environ` show the env var. That is inherent to env-based secrets and acceptable for dev.

## Alternatives and trade-off

1. **Spring Security `SecurityFilterChain` + `AuthorizationManager` + custom entry point (selected).** It is standard and reviewable, the firewall closes the path-normalization hole, auth runs before routing, and no principal class is needed. Cost: a new dependency, plus the generic headers and firewall applied to all paths. Both are security-positive and leave bodies unchanged.
2. Plain `OncePerRequestFilter` with a prefix check. No dependency, but it is vulnerable to the `;` bypass described above unless it reimplements normalization or denies by default, and deny-by-default violates "other paths unchanged". Rejected.
3. MVC `HandlerInterceptor` that throws into `GlobalExceptionHandler`. It reuses the advice, but handler mapping runs first: an unauthenticated `GET /compact` returns 405, 415 and 404 also leak, and unmapped paths are never covered. Rejected.
4. Test token source. The selected option sets the fixed value in `src/test/resources/application.yml`. It goes through the same binding as production, and a `@TestPropertySource` can override it to blank for the blank-config tests. A `.txt` loaded with `@DynamicPropertySource` cannot be overridden, because dynamic properties take precedence over `@TestPropertySource`, so the blank-config test would be impossible in the same file. It would also duplicate the reader in three classes. So `poi-api-bearer-token.txt` is not created.
5. Envelope rendering. The selected option builds `ApiResponse.error(...)` and serializes it with a static Jackson 2 `ObjectMapper`. `StoredJsonParser` already uses that pattern in main code, so it is on the runtime classpath. Delegating to `HandlerExceptionResolver` does not work: with `@RestControllerAdvice(basePackages=...)`, a `null` handler does not match the advice, so `GlobalExceptionHandler` is skipped. Looking up the MVC converters inside the entry point adds coupling for no gain. Tests assert the envelope fields, so drift is caught.
6. A custom authentication filter that sets an `Authentication`. It needs more classes and has no consumer for a principal. Rejected in favor of `AuthorizationManager`.

## Rollout

1. Local dev (this task): `.env` gets a generated token, then the user runs the compose smoke in `runtime-runbook.md`.
2. Deploy (outside this task, documented in `AGENTS.md`): (a) provision the real value under `POI_API_BEARER_TOKEN` in the deploy environment. (b) Give it to every caller (gateway or BFF) and have them start sending the header. That is harmless against the old server, which ignores `Authorization`. (c) Then deploy this version. Reversing (b) and (c) causes an outage: every POI call returns 401 until callers update.

## Rollback and forward recovery

- Rollback: revert the change. That removes the dependency, the three classes, and the yml key, and the endpoints are open again. The leftover env var is harmless.
- Forward recovery: wrong or blank token → fix the env value and restart. Leaked token → generate a new one, update `.env` or the deploy environment and the callers, and restart. Callers holding the old token get 401 until they update, because only one token is supported.

## Implementation plan

Reference code below. Main may adjust Spring Security 7 or Boot 4 API spelling to compile, but must keep the invariants. Use the `FILE` blocks verbatim.

### Code: pom.xml

After `spring-boot-starter-webmvc`, add `org.springframework.boot:spring-boot-starter-security`. After `spring-boot-starter-webmvc-test`, add `org.springframework.boot:spring-boot-starter-security-test` with `<scope>test</scope>`. If the test starter does not resolve, use `org.springframework.security:spring-security-test` (test scope) instead.

### Code: ApiBearerTokenProperties

```java
package vn.visitvietnam.dataserving.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/** Shared secret for /api/v1/pois. Bound from POI_API_BEARER_TOKEN via application.yml. */
@ConfigurationProperties(prefix = "app.security.poi-api")
public record ApiBearerTokenProperties(String bearerToken) {

    @Override
    public String toString() {
        boolean set = bearerToken != null && !bearerToken.isBlank();
        return "ApiBearerTokenProperties[bearerToken=" + (set ? "<set>" : "<blank>") + "]";
    }
}
```

### Code: BearerTokenAuthenticationEntryPoint

`package vn.visitvietnam.dataserving.common.web;` A `public final class` that implements both `AuthenticationEntryPoint` and `AccessDeniedHandler`. Both methods call `writeUnauthorized(response)`. It is not a `@Component`; `SecurityConfig` creates it.

```java
static final String MESSAGE = "Missing or invalid bearer token.";
static final String ERROR_CODE = "ERR_UNAUTHORIZED";
private static final ObjectMapper MAPPER = new ObjectMapper(); // com.fasterxml.jackson.databind, as in StoredJsonParser

private void writeUnauthorized(HttpServletResponse response) throws IOException {
    if (response.isCommitted()) {
        return;
    }
    ApiResponse<Void> body = ApiResponse.error(HttpStatus.UNAUTHORIZED, MESSAGE, ERROR_CODE, null);
    response.setStatus(HttpStatus.UNAUTHORIZED.value());
    response.setHeader(HttpHeaders.WWW_AUTHENTICATE, "Bearer");
    response.setContentType(MediaType.APPLICATION_JSON_VALUE);
    response.setCharacterEncoding(StandardCharsets.UTF_8.name());
    response.getOutputStream().write(MAPPER.writeValueAsBytes(body));
}
```

### Code: SecurityConfig

```java
@Configuration(proxyBeanMethods = false)
@EnableWebSecurity
@EnableConfigurationProperties(ApiBearerTokenProperties.class)
public class SecurityConfig {

    static final String[] POI_API_PATHS = {"/api/v1/pois", "/api/v1/pois/**"};
    private static final Logger log = LoggerFactory.getLogger(SecurityConfig.class);

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http, ApiBearerTokenProperties properties) throws Exception {
        PoiBearerTokenVerifier verifier = new PoiBearerTokenVerifier(properties.bearerToken());
        if (!verifier.configured()) {
            log.warn("poi_api_auth token_configured=false; every /api/v1/pois request returns 401 until POI_API_BEARER_TOKEN is set");
        }
        BearerTokenAuthenticationEntryPoint unauthorized = new BearerTokenAuthenticationEntryPoint();
        AuthorizationManager<RequestAuthorizationContext> poiAccess = (authentication, context) -> {
            HttpServletRequest request = context.getRequest();
            Outcome outcome = verifier.verify(request);
            if (outcome != Outcome.ACCEPTED) {
                log.info("poi_api_auth_rejected reason={} method={} trace_id={}",
                        outcome, request.getMethod(), request.getAttribute(RequestContext.TRACE_ID_KEY));
            }
            return new AuthorizationDecision(outcome == Outcome.ACCEPTED);
        };
        http
                .csrf(AbstractHttpConfigurer::disable)
                .httpBasic(AbstractHttpConfigurer::disable)
                .formLogin(AbstractHttpConfigurer::disable)
                .logout(AbstractHttpConfigurer::disable)
                .requestCache(AbstractHttpConfigurer::disable)
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .exceptionHandling(e -> e.authenticationEntryPoint(unauthorized).accessDeniedHandler(unauthorized))
                .authorizeHttpRequests(a -> a
                        .requestMatchers(POI_API_PATHS).access(poiAccess)
                        .anyRequest().permitAll());
        return http.build();
    }

    /** No login mechanism exists. This bean stops Boot from creating a default user and logging its password. */
    @Bean
    public AuthenticationManager noLoginAuthenticationManager() {
        return authentication -> {
            throw new ProviderNotFoundException("No login mechanism is configured");
        };
    }

    enum Outcome { ACCEPTED, NOT_CONFIGURED, MISSING_HEADER, MULTIPLE_HEADERS, NOT_BEARER, EMPTY_TOKEN, TOKEN_MISMATCH }

    static final class PoiBearerTokenVerifier {
        private final byte[] expectedDigest; // null = not configured

        PoiBearerTokenVerifier(String configuredToken) {
            String token = configuredToken == null ? "" : configuredToken.strip();
            this.expectedDigest = token.isEmpty() ? null : sha256(token);
        }

        boolean configured() {
            return expectedDigest != null;
        }

        Outcome verify(HttpServletRequest request) {
            if (expectedDigest == null) return Outcome.NOT_CONFIGURED;
            Enumeration<String> headers = request.getHeaders(HttpHeaders.AUTHORIZATION);
            List<String> values = headers == null ? List.of() : Collections.list(headers);
            if (values.isEmpty()) return Outcome.MISSING_HEADER;
            if (values.size() > 1) return Outcome.MULTIPLE_HEADERS;
            String value = values.getFirst();
            int space = value.indexOf(' ');
            if (space < 0 || !"Bearer".equalsIgnoreCase(value.substring(0, space))) return Outcome.NOT_BEARER;
            String presented = value.substring(space + 1).strip();
            if (presented.isEmpty()) return Outcome.EMPTY_TOKEN;
            return MessageDigest.isEqual(sha256(presented), expectedDigest) ? Outcome.ACCEPTED : Outcome.TOKEN_MISMATCH;
        }

        private static byte[] sha256(String value) {
            try {
                return MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8));
            } catch (NoSuchAlgorithmException e) {
                throw new IllegalStateException("SHA-256 is unavailable", e);
            }
        }
    }
}
```

### Code: OpenApiConfig

- In `dataServingApiOpenApi(String)`, keep the signature (`OpenApiConfigTest` depends on it). Add `public static final String BEARER_AUTH = "bearerAuth";`. Chain `.components(new Components().addSecuritySchemes(BEARER_AUTH, new SecurityScheme().type(SecurityScheme.Type.HTTP).scheme("bearer").description("Send Authorization: Bearer <token>. Required for /api/v1/pois.")))` and `.addSecurityItem(new SecurityRequirement().addList(BEARER_AUTH))`. The `serving` group contains only `PoiController`.
- In `problemResponsesCustomizer`: iterate `openApi.getPaths().forEach((path, pathItem) -> ...)`. For `path.startsWith("/api/v1/pois")`, call `op.getResponses().putIfAbsent("401", new ApiResponse().description("Unauthorized: missing or invalid bearer token"))` before the existing content-fill loop. The 401 then gets the same documented content as the other error codes, which is the existing convention.

### Config: application.yml (main)

Insert a new top-level block after `springdoc:`:
```yaml
app:
  security:
    poi-api:
      # Shared secret for /api/v1/pois. Empty means every POI call returns 401. Never commit a value.
      bearer-token: ${POI_API_BEARER_TOKEN:}
```
Do not add `logging.level.org.springframework.security`.

### Config: application.yml (test)

Append:
```yaml
app:
  security:
    poi-api:
      # Fixed test-only token, not a secret. Tests never read .env.
      bearer-token: test-only-poi-api-token-not-a-secret
```
This file replaces the main `application.yml` on the test classpath, so the test value is the only one tests see.

### Config: docker-compose.yml

Under `services.data-serving-service.environment`, after `LOG_LEVEL: INFO`, add `POI_API_BEARER_TOKEN: ${POI_API_BEARER_TOKEN:-}`. Use `:-`, not `:?`: a blank token must still start the app so health works.

### Tests: ApiBearerAuthTest (new, package `config`)

- `@WebMvcTest(PoiController.class)` and `@Import({SecurityConfig.class, GlobalExceptionHandler.class, LanguageResolver.class, RequestIdFilter.class})`. Fields: `@MockitoBean PoiService poiService`, `@Autowired MockMvc mvc`, `@Value("${app.security.poi-api.bearer-token}") String token`.
- `@BeforeEach` stubs every service method with an empty result, so a correct token gives 200: `getCompactPois` → `List.of()`; `getFeatures(any(), any(), anyInt(), any(), any(), anyInt(), anyInt())` → `new PoiService.FeaturePage(List.of(), 0)`; `getGallery` → `PageResponse.of(List.of(), 0, 20, 0)`; `getReviews` → `new PoiService.ReviewsPage(PageResponse.of(List.of(), 0, 10, 0), List.of())`; `getExperiences` → `new PoiExperiencesResponse(List.of())`; `getPracticalInfo` → `null` is fine (200, data null); `getAmenities` → `List.of()`.
- `static Stream<Arguments> poiEndpoints()` yields `(name, Supplier<MockHttpServletRequestBuilder>)` for `post("/api/v1/pois/compact").contentType(APPLICATION_JSON).content("{\"ids\":[\"poi_01\"]}")`, `get("/api/v1/pois/features")`, and `get("/api/v1/pois/poi_01/{gallery|reviews|experiences|practical_info|amenities}")`.
- Shared assertion `expect401(ResultActions)`: status 401, header `WWW-Authenticate` = `Bearer`, header `X-Request-Id` exists, `$.success` false, `$.code` 401, `$.message` = `Missing or invalid bearer token.`, `$.data` null, `$.errors` null, `$.meta.error_code` = `ERR_UNAUTHORIZED`, `$.meta.trace_id` not empty.
- Tests:
  - `missingAuthorizationReturns401Envelope`, `wrongTokenReturns401`, `nonBearerSchemeReturns401` (each `@ParameterizedTest @MethodSource("poiEndpoints")`). Use `"Basic " + token`, `"Token " + token`, and the raw `token` with no scheme. In each, call `verifyNoInteractions(poiService)`.
  - `correctTokenReachesController`, parameterized: status 200.
  - `bearerSchemeIsCaseInsensitive`: `bearer <token>` → 200.
  - `emptyBearerTokenReturns401`: `"Bearer "` and `"Bearer    "`.
  - `duplicateAuthorizationHeadersReturn401`: correct token sent twice → 401.
  - `unauthorizedBodyCarriesTraceIdAndNeverEchoesToken`: `X-Request-Id: auth-trace-1` plus `Bearer <token>x` → `meta.trace_id` = `auth-trace-1`, and the response body does not contain `token`.
  - `authPrecedesRoutingForWrongMethodAndUnknownPath`: no token on `GET /api/v1/pois/compact`, on `/api/v1/pois/poi_01/unknown`, and on `POST /api/v1/pois/compact` with `text/plain` → all 401.
  - `pathsOutsidePoiApiStayAnonymous`: `GET /actuator/health` and `GET /api/v1/other` without a token return 404 in this slice (no handler), not 401.
  - `@Nested @TestPropertySource(properties = "app.security.poi-api.bearer-token=") class BlankTokenConfiguration` with its own `@Autowired MockMvc`: `blankConfigurationRejectsEveryPoiRequest`, parameterized with `@MethodSource("vn.visitvietnam.dataserving.config.ApiBearerAuthTest#poiEndpoints")`, sends `Bearer ` and `Bearer anything` → 401. `blankConfigurationKeepsNonPoiPathsOpen`: `GET /actuator/health` → 404, not 401.
  - Plain unit tests: `verifierTreatsNullBlankAndWhitespaceConfigAsNotConfigured` checks `null`, `""`, and `"  \r\n"` → `configured()` false and `verify` returns `NOT_CONFIGURED`. `verifierStripsConfiguredWhitespace` checks that `"abc\r\n"` accepts `Bearer abc`. `verifierOutcomes` covers each `Outcome` value with a `MockHttpServletRequest`. `propertiesToStringNeverContainsToken`. `mainApplicationYmlBindsBearerTokenFromPoiApiBearerTokenEnv`: load `src/main/resources/application.yml` with `YamlPropertySourceLoader` and assert that the raw value of `app.security.poi-api.bearer-token` is `${POI_API_BEARER_TOKEN:}`.

### Tests: PoiControllerIntegrationTest

- Add `SecurityConfig.class` to `@Import`. Add `@Value("${app.security.poi-api.bearer-token}") private String bearerToken;` and a helper `private <B extends MockHttpServletRequestBuilder> B authorized(B b) { b.header(HttpHeaders.AUTHORIZATION, "Bearer " + bearerToken); return b; }`.
- Wrap every `mockMvc.perform(...)` builder with `authorized(...)`. Do not change any expected status or `jsonPath`. This proves I2 for 200, 400, 404, 405, 415, and 422.

### Tests: DataServingApplicationTests

Add `@Value("${app.security.poi-api.bearer-token}") String bearerToken` and `@Autowired ApplicationContext context`. Keep `healthEndpointReturnsUp` and the OpenAPI test without a token. New tests:
- `poiEndpointWithoutTokenReturns401Envelope`: `GET /api/v1/pois/no-such-poi/amenities` → 401, `$.meta.error_code` = `ERR_UNAUTHORIZED`.
- `poiEndpointWithTokenReturns200`: same path with the token → 200 and `$.data` empty. Amenities returns 200 for an unknown POI.
- `openApiDocsDeclareBearerAuthAndStayOpen`: `/v3/api-docs` without a token → 200, `components.securitySchemes.bearerAuth.scheme` = `bearer`, and `paths./api/v1/pois/{poi_id}/amenities.get.responses.401` exists.
- `noDefaultUserDetailsServiceIsCreated`: `context.getBeanNamesForType(UserDetailsService.class)` is empty.

### Docs: AGENTS.md (service)

- `## Contract`: new bullet: "`/api/v1/pois/**` requires `Authorization: Bearer <token>` equal to `POI_API_BEARER_TOKEN` (SHA-256 + constant-time compare, `config/SecurityConfig`). Missing or blank config returns 401 on every POI call; the app still starts. Other paths, including `/actuator/health`, `/v3/api-docs`, and `/swagger-ui.html`, stay anonymous. The 401 body is the `ApiResponse` envelope with `meta.error_code=ERR_UNAUTHORIZED`, written by `common/web/BearerTokenAuthenticationEntryPoint`. Never log or echo the token."
- `## Commands`, Local run: "copy `.env.example` to `.env` and fill `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POI_API_BEARER_TOKEN` (e.g. `python -c \"import secrets; print(secrets.token_urlsafe(32))\"`)".
- `## Environment variables`: add `POI_API_BEARER_TOKEN`. Add: "Kubernetes: `k8s/configmap.yaml` carries an empty placeholder; the deploy pipeline injects the real value, preferably from a Secret. Provision the token to callers before deploying a build that enforces it."
- `## Layout`: "Tests use the fixed token in `src/test/resources/application.yml`; tests import `SecurityConfig` in `@WebMvcTest`."

### Docs: mapping files (compact, gallery, reviews, features, experiences, practical_info, amenities)

- `## Request header`: append a last row with the next `Stt` (do not renumber other rows): `| N | Authorization | string | có | `Bearer <token>`. Token khớp biến môi trường `POI_API_BEARER_TOKEN` của server. Thiếu header, scheme khác `Bearer`, hoặc token sai trả HTTP 401. |`
- `## Status code`: insert in numeric order: `| 401 | ERR_UNAUTHORIZED | Thiếu `Authorization`, scheme khác `Bearer`, token sai, hoặc server chưa cấu hình token. Kiểm tra trước mọi mã khác. Message `Missing or invalid bearer token.` Header `WWW-Authenticate: Bearer`. |`
- `## Sample request`: add the line `Authorization: Bearer <token>` after the request line. Use the literal `<token>`, never a real value.
- Do not touch the Required value of any other row.

### Dev token generation (Main; writes only gitignored .env)

Run from the repo root with Bash. The script prints no token.
```bash
python -I - <<'PY'
import pathlib, secrets, sys
p = pathlib.Path('services/data-serving-service/.env')
text = p.read_text(encoding='utf-8') if p.exists() else ''
if any(l.split('=', 1)[0].strip() == 'POI_API_BEARER_TOKEN' for l in text.splitlines()):
    sys.exit('POI_API_BEARER_TOKEN already present in .env; not overwritten')
sep = '' if text == '' or text.endswith(('\n', '\r')) else '\n'
with p.open('a', encoding='utf-8', newline='\n') as f:
    f.write(sep + 'POI_API_BEARER_TOKEN=' + secrets.token_urlsafe(32) + '\n')
print('POI_API_BEARER_TOKEN appended')
PY
```
If the script exits non-zero, stop and ask the user whether to keep or replace the token.

### Leak check (Main; prints file names only)

```bash
python -I - <<'PY'
import pathlib, subprocess, sys
lines = pathlib.Path('services/data-serving-service/.env').read_text(encoding='utf-8').splitlines()
tok = next((l.split('=', 1)[1].strip() for l in lines if l.split('=', 1)[0].strip() == 'POI_API_BEARER_TOKEN'), '')
if not tok:
    sys.exit('token missing in .env')
r = subprocess.run(['git', 'grep', '--untracked', '-l', '-F', '-f', '-'], input=tok + '\n', capture_output=True, text=True)
print('token_leak_files=', r.stdout.split())
sys.exit(1 if r.stdout.strip() else 0)
PY
```
Pass: `token_leak_files= []`, and `git check-ignore services/data-serving-service/.env` prints the path.

### Runtime runbook content (Main writes it into the task's runtime-runbook.md; user runs it)

PowerShell, in `services/data-serving-service`. Prerequisite: `.env` has `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POI_API_BEARER_TOKEN`; the `apps` DDL was applied once (see `AGENTS.md`). Do not run `docker compose config`, because it prints the token.
1. `docker compose up -d --build`
2. `docker compose exec data-serving-service sh -c 'test -n "$POI_API_BEARER_TOKEN" && echo token=set || echo token=EMPTY'` → expect `token=set`.
3. `$t = ((Select-String -Path .env -Pattern '^POI_API_BEARER_TOKEN=(.*)$').Matches[0].Groups[1].Value).Trim()`
4. `curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:8080/actuator/health` → `200`.
5. `curl.exe -s -i http://localhost:8080/api/v1/pois/smoke-poi/amenities` → `401`, `WWW-Authenticate: Bearer`, and a body with `"success":false,"code":401` and `"error_code":"ERR_UNAUTHORIZED"`.
6. `curl.exe -s -i -H "Authorization: Bearer wrong-token" http://localhost:8080/api/v1/pois/smoke-poi/amenities` → `401`, same body.
7. `curl.exe -s -i -H "Authorization: Bearer $t" http://localhost:8080/api/v1/pois/smoke-poi/amenities` → `200`, `"success":true`, `"data":[]`.
8. `docker compose logs data-serving-service | Select-String poi_api_auth_rejected` → two lines, `MISSING_HEADER` and `TOKEN_MISMATCH`, and neither shows a token.
Do not use `curl -v`, and do not paste output that contains `$t`. Report only the status codes and the log reasons.

## Verification

- Targeted: `cd services/data-serving-service && mvnw.cmd -q -B test -Dtest=ApiBearerAuthTest,PoiControllerIntegrationTest,OpenApiConfigTest`
- Full: `cd services/data-serving-service && mvnw.cmd -q -B test` (JDK 26 and Docker). This includes `DataServingApplicationTests` and `PoiRepositoryIntegrationTest`, which must stay green with the token from the test yml.
- Gate: `python scripts/vv.py verify 20261116-poi-api-dev-auth`
- Secret hygiene: the leak check above; `git status --porcelain` shows no `.env`; and `.env.example` plus `k8s/configmap.yaml` contain `POI_API_BEARER_TOKEN=` and `POI_API_BEARER_TOKEN: ""` with empty values.
- Runtime: the user-run runbook above (gate `runtime`).
- Reviewers: `app-security-reviewer` (SecurityConfig, entry point, pom, compose, ConfigMap) and `api-contract-reviewer` (401 envelope, OpenAPI, mapping docs).

## Proposed decision ledger rows (Main records)

- D-1: Spring Security `SecurityFilterChain` + `AuthorizationManager` on `/api/v1/pois/**`, `anyRequest().permitAll()`. Source: Alternatives 1–3.
- D-2: Variable `POI_API_BEARER_TOKEN` → `app.security.poi-api.bearer-token`. Blank fails closed and the app still starts.
- D-3: 401 = `ApiResponse.error(UNAUTHORIZED, "Missing or invalid bearer token.", "ERR_UNAUTHORIZED")` plus `WWW-Authenticate: Bearer`, the same for every reason.
- D-4: SHA-256 + `MessageDigest.isEqual`, and the configured value is `strip()`ed.
- D-5: Test token lives in `src/test/resources/application.yml`, and `poi-api-bearer-token.txt` is not created (Alternatives 4).
- D-6: ConfigMap value empty. Recommend Secret injection at deploy (follow-up, not blocking).

FILE: services/data-serving-service/.env.example
# Copy to .env next to docker-compose.yml and fill in locally. .env is gitignored; never commit it.
# docker compose reads .env automatically for variable interpolation.

# PostgreSQL credentials for the local compose database.
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_PORT=55432

# Shared bearer token for /api/v1/pois. Empty means every POI call returns HTTP 401.
# Generate one locally, for example: python -c "import secrets; print(secrets.token_urlsafe(32))"
POI_API_BEARER_TOKEN=
END_FILE

FILE: services/data-serving-service/k8s/configmap.yaml
# Placeholder only. The deploy pipeline must supply the real POI_API_BEARER_TOKEN, preferably from a Kubernetes Secret
# or secret manager under the same variable name. Never commit a real value here.
# Keep the value empty: an empty token makes every /api/v1/pois call return HTTP 401 (fail closed).
# A non-empty placeholder would become a working credential if nobody replaced it.
# Consume with: envFrom: [{ configMapRef: { name: data-serving-service-config } }]
apiVersion: v1
kind: ConfigMap
metadata:
  name: data-serving-service-config
  labels:
    app.kubernetes.io/name: data-serving-service
data:
  POI_API_BEARER_TOKEN: ""
END_FILE
