FROM ghcr.io/spiffe/spire-agent:1.9.0 AS spire

FROM alpine:3.19

RUN apk add --no-cache curl openssl coreutils
COPY --from=spire /opt/spire/bin/spire-agent /opt/spire/bin/spire-agent

WORKDIR /app
COPY rogue.sh /app/rogue.sh
RUN chmod +x /app/rogue.sh
CMD ["/app/rogue.sh"]
