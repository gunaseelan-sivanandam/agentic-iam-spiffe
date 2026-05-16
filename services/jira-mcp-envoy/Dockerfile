FROM ghcr.io/spiffe/spire-agent:1.9.0 AS spire

FROM envoyproxy/envoy:v1.29.2

USER root
COPY --from=spire /opt/spire/bin/spire-agent /opt/spire/bin/spire-agent
COPY entrypoint.sh /app/entrypoint.sh
COPY envoy.yaml /etc/envoy/envoy.yaml
RUN chmod 0755 /opt/spire/bin/spire-agent /app/entrypoint.sh
EXPOSE 11443
ENTRYPOINT ["/app/entrypoint.sh"]
