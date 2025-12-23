FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn
COPY server.py /app/server.py
EXPOSE 8443
