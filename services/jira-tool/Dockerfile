FROM ghcr.io/spiffe/spire-agent:1.9.0 AS spire

FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir biscuit-python redis
COPY --from=spire /opt/spire/bin/spire-agent /opt/spire/bin/spire-agent
COPY services/jira-tool/server.py /app/server.py
COPY services/jira-tool/entrypoint.sh /app/entrypoint.sh
COPY services/shared /app/shared
RUN chmod 0755 /opt/spire/bin/spire-agent /app/entrypoint.sh
EXPOSE 8080
ENTRYPOINT ["/app/entrypoint.sh"]
