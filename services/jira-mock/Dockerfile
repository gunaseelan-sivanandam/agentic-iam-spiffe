FROM python:3.11-slim

WORKDIR /app
COPY services/jira-mock/server.py /app/server.py
EXPOSE 8080
CMD ["python", "/app/server.py"]
