FROM ghcr.io/spiffe/spire-agent:1.9.0 AS spire

FROM python:3.11-slim

WORKDIR /app
COPY --from=spire /opt/spire/bin/spire-agent /opt/spire/bin/spire-agent
COPY services/codex-jira-mcp-adapter/server.py /app/server.py
COPY services/codex-jira-mcp-adapter/entrypoint.sh /app/entrypoint.sh
RUN chmod 0755 /opt/spire/bin/spire-agent /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
