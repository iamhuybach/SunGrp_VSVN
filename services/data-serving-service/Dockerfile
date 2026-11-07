# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM maven:3.9-eclipse-temurin-26 AS builder

WORKDIR /build

# Pre-cache dependencies
COPY pom.xml ./
RUN mvn dependency:go-offline -q || true

# Build application
COPY src ./src
RUN mvn clean package -DskipTests -q

# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM eclipse-temurin:26-jre

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# Non-root app user
RUN groupadd --system app && useradd --system --gid app --home /app app

WORKDIR /app

COPY --from=builder --chown=app:app /build/target/data-serving-service-*.jar app.jar

USER app

EXPOSE 8080

CMD ["java", \
     "-XX:+UseContainerSupport", \
     "-XX:MaxRAMPercentage=75.0", \
     "-XX:+UseZGC", \
     "-XX:+ExitOnOutOfMemoryError", \
     "-jar", "/app/app.jar"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl --fail http://localhost:8080/actuator/health || exit 1

