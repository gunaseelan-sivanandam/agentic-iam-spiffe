FROM ghcr.io/spiffe/spire-agent:1.9.0 AS spire

FROM docker:27.0.3-cli
RUN apk add --no-cache openssl coreutils curl
COPY --from=spire /opt/spire/bin/spire-agent /opt/spire/bin/spire-agent
COPY scripts/rogue_node_tests.sh /opt/rogue_node_tests.sh
RUN chmod 0755 /opt/spire/bin/spire-agent /opt/rogue_node_tests.sh
ENTRYPOINT ["/opt/rogue_node_tests.sh"]
