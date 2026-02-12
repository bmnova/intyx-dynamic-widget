# Backend (Flask) for intyx-dynamic-widget — Cloud Run / generic container
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY server/requirements.txt ./server/
RUN pip install --no-cache-dir -r server/requirements.txt

# Application
COPY server/ ./server/

# Cloud Run sets PORT; default 8080
ENV PORT=8080
EXPOSE 8080

# Run with gunicorn (production). For local debug use: python server/app.py
CMD exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 4 server.app:app --capture-output
