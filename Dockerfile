# Multi-stage build: frontend + backend
# Stage 1: Build Vue frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim
WORKDIR /app

# System deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server/ ./server/

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

EXPOSE 8000

# Copy built frontend into shared volume on startup, then start the server.
# The shared volume (/srv/frontend-dist) is mounted by docker-compose so
# nginx can serve static assets directly instead of proxying through Python.
CMD ["sh", "-c", "cp -a /app/frontend/dist/* /srv/frontend-dist/ 2>/dev/null; exec uvicorn server.main:app --host 0.0.0.0 --port 8000 --workers 2"]
