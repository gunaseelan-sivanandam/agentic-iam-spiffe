FROM alpine:3.19

RUN apk add --no-cache curl

WORKDIR /app
COPY client.sh /app/client.sh
RUN chmod +x /app/client.sh
CMD ["/app/client.sh"]
