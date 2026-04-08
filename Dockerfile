FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Make entrypoint executable
RUN chmod +x docker-entrypoint.sh

# SQLite database will live in /data volume
ENV DATABASE_PATH=/data/db.sqlite3

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
