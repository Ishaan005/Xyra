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
RUN apt-get update && apt-get install -y supervisor curl libpq-dev gcc weasyprint \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/log/supervisor /etc/supervisor/conf.d
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs
# Configure IPv4 preference to avoid IPv6 localhost issues
RUN echo 'net.ipv6.conf.all.disable_ipv6 = 1' >> /etc/sysctl.conf || true
ENV PYTHONUNBUFFERED=1 \
    APP_MODULE="main:app" \
    HOST="0.0.0.0" \
    PORT="8000" \
    API_V1_STR="/api/v1" \
    PROJECT_NAME="Xyra" \
    NODE_OPTIONS="--dns-result-order=ipv4first" 
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt
COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/.next/standalone ./frontend_standalone
COPY --from=frontend-builder /app/frontend/public ./frontend_standalone/public
COPY --from=frontend-builder /app/frontend/.next/static ./frontend_standalone/.next/static
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
  CMD curl -f http://127.0.0.1:3000/ || exit 1
CMD ["/entrypoint.sh"]
