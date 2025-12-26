FROM ghcr.io/spiffe/spire-agent:1.9.0 AS spire

FROM alpine:3.19
COPY --from=spire /opt/spire/bin/spire-agent /opt/spire/bin/spire-agent
COPY entrypoint.sh /opt/spire/bin/entrypoint.sh
RUN chmod 0755 /opt/spire/bin/spire-agent /opt/spire/bin/entrypoint.sh
ENTRYPOINT ["/opt/spire/bin/entrypoint.sh"]
