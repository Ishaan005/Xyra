# Stage 1: Build Next.js standalone app
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
ENV NEXT_PUBLIC_API_BASE_URL=/api/v1
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --frozen-lockfile
COPY frontend/ ./
RUN npm run build

# Stage 2: Setup Python, FastAPI, and Supervisor for the final image
FROM python:3.13-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    supervisor curl libpq-dev gcc \
    libcairo2 \
    pango1.0-tools \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libxml2 \
    libxslt1.1 \
    libjpeg-dev \
    libgobject-2.0-dev \
    fonts-liberation \
    fonts-dejavu \
    fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*
ENV PYTHONUNBUFFERED=1 \
    APP_MODULE="main:app" \
    HOST="0.0.0.0" \
    PORT="8000" \
    API_V1_STR="/api/v1" \
    PROJECT_NAME="Xyra"
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt
COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/.next/standalone ./frontend_standalone
COPY --from=frontend-builder /app/frontend/public ./frontend_standalone/public
COPY --from=frontend-builder /app/frontend/.next/static ./frontend_standalone/.next/static
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
