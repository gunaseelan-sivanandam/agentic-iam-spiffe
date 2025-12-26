FROM ghcr.io/spiffe/spire-server:1.9.0 AS spire

FROM alpine:3.19
COPY --from=spire /opt/spire/bin/spire-server /opt/spire/bin/spire-server
COPY init.sh /opt/spire/bin/init.sh
RUN chmod 0755 /opt/spire/bin/spire-server /opt/spire/bin/init.sh
ENTRYPOINT ["/opt/spire/bin/init.sh"]
