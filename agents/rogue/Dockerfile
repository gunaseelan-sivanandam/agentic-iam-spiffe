FROM alpine:3.19

RUN apk add --no-cache curl

WORKDIR /app
COPY rogue.sh /app/rogue.sh
RUN chmod +x /app/rogue.sh
CMD ["/app/rogue.sh"]
