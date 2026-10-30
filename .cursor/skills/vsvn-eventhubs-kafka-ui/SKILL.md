---
name: vsvn-eventhubs-kafka-ui
description: Fast-open the local Kafka UI for the VSVN Dev Event Hubs namespace. Use when the user says "Mở Kafka UI cho dự án VSVN môi trường Dev", or asks to open, start, or stop Kafka UI, kafbat, or local/eventhubs-kafka-ui. Do not use for notebooks, pipelines, DDL, ctrl tables, or Fabric probes.
---

# Event Hubs Kafka UI

This is a local Docker shortcut, not an engineering task. Do not run `python scripts/vv.py`, do not create a task, and do not read notebooks, pipelines, DDL, or task artifacts.

Facts live in `docs/context/EVENTHUBS_KAFKA_UI.md`. The fast path does not need that file.

## Open

1. Run `powershell -NoProfile -ExecutionPolicy Bypass -File local/eventhubs-kafka-ui/up.ps1`.
2. If it prints the UI URL, reply with http://127.0.0.1:8080 and the cluster name `dev-visitvn-evhns-sg-01`. Then check `http://127.0.0.1:8080/api/clusters` and report status and topic names only.
3. If Docker is not running, say so and stop.
4. If `.env` is missing or `EVENTHUB_CONNECTION_STRING` is empty, stop. Tell the user to paste the namespace Listen connection string into `local/eventhubs-kafka-ui/.env` only. Do not recreate compose files and do not copy a real key into `.env.example`.
5. Do not open `.env`. Do not run `docker compose config` or `docker inspect`. Redact `SharedAccessKey` and `password="Endpoint=` before quoting logs.

## Close

When the user is done viewing, run `powershell -NoProfile -ExecutionPolicy Bypass -File local/eventhubs-kafka-ui/down.ps1`. Leave `.env` in place so the next open stays one command.
