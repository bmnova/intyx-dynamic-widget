FROM python:3.12-slim

WORKDIR /app

# Install dependencies (build context is server/)
COPY requirements.txt ./server/
RUN pip install --no-cache-dir -r ./server/requirements.txt

# Copy server code into /app/server/ so that
# "from server.X import" works from /app/
COPY . ./server/

ENV PORT=8080
EXPOSE 8080

CMD exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 4 server.app:app --capture-output
