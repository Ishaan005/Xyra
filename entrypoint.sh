#!/bin/bash
set -e

# Ensure we're using standard output and error streams
exec 1>&2

# Clear startup marker - this should appear in logs
echo "##################################################"
echo "### XYRA ENTRYPOINT.SH SCRIPT IS RUNNING ###"
echo "##################################################"
echo "Script started at: $(date)"
echo "Current working directory: $(pwd)"
echo "Current user: $(whoami)"
echo ""

# Debug: Print environment variables for troubleshooting
echo "=== CONTAINER STARTUP DEBUG INFORMATION ==="
echo "Container started at: $(date)"
echo ""
echo "Environment Variables:"
echo "POSTGRES_SERVER: ${POSTGRES_SERVER:-NOT_SET}"
echo "POSTGRES_USER: ${POSTGRES_USER:-NOT_SET}"
echo "POSTGRES_PORT: ${POSTGRES_PORT:-NOT_SET}"
echo "POSTGRES_DB: ${POSTGRES_DB:-NOT_SET}"
echo "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:+***SET***}"
echo "POSTGRES_OPTIONS: ${POSTGRES_OPTIONS:-NOT_SET}"
echo "FIRST_SUPERUSER: ${FIRST_SUPERUSER:-NOT_SET}"
echo "FIRST_SUPERUSER_PASSWORD: ${FIRST_SUPERUSER_PASSWORD:+***SET***}"
echo "NEXTAUTH_SECRET: ${NEXTAUTH_SECRET:+***SET***}"
echo "NEXTAUTH_URL: ${NEXTAUTH_URL:-NOT_SET}"
echo "NEXT_PUBLIC_API_BASE_URL: ${NEXT_PUBLIC_API_BASE_URL:-NOT_SET}"
echo "INTERNAL_BACKEND_URL: ${INTERNAL_BACKEND_URL:-NOT_SET}"
echo "AZURE_AI_AGENT_PROJECT_CONNECTION_STRING: ${AZURE_AI_AGENT_PROJECT_CONNECTION_STRING:+***SET***}"
echo "AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME: ${AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME:-NOT_SET}"
echo "STRIPE_API_KEY: ${STRIPE_API_KEY:+***SET***}"
echo "STRIPE_WEBHOOK_SECRET: ${STRIPE_WEBHOOK_SECRET:+***SET***}"
echo "============================================="
echo ""

# Print all environment variables (sanitized)
echo "=== ALL ENVIRONMENT VARIABLES (SANITIZED) ==="
env | sort | while IFS='=' read -r key value; do
  case "$key" in
    *PASSWORD*|*SECRET*|*KEY*)
      echo "$key=***REDACTED***"
      ;;
    *)
      echo "$key=$value"
      ;;
  esac
done | grep -E "^(POSTGRES_|NEXTAUTH_|FIRST_|AZURE_|STRIPE_|NODE_|API_|PROJECT_|INTERNAL_|NEXT_PUBLIC_)" || true
echo "============================================="
echo ""

# Run database migrations before starting services
echo "=== RUNNING DATABASE MIGRATIONS ==="
echo "About to run database migrations..."
cd /app/backend
python scripts/migrate_and_init.py
if [ $? -ne 0 ]; then
    echo "ERROR: Database migration failed"
    exit 1
fi
echo "Database migrations completed successfully!"
echo ""

# Generate supervisord configuration with environment variables
echo "=== GENERATING SUPERVISORD CONFIGURATION ==="
# Ensure the supervisor directory exists
mkdir -p /etc/supervisor/conf.d
cat > /etc/supervisor/conf.d/supervisord.conf << EOF
[supervisord]
nodaemon=true
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid
user=root

[program:fastapi]
command=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
directory=/app/backend
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
environment=PYTHONUNBUFFERED=1,POSTGRES_SERVER="${POSTGRES_SERVER}",POSTGRES_USER="${POSTGRES_USER}",POSTGRES_PORT="${POSTGRES_PORT}",POSTGRES_PASSWORD="${POSTGRES_PASSWORD}",POSTGRES_DB="${POSTGRES_DB}",POSTGRES_OPTIONS="${POSTGRES_OPTIONS}",FIRST_SUPERUSER="${FIRST_SUPERUSER}",FIRST_SUPERUSER_PASSWORD="${FIRST_SUPERUSER_PASSWORD}"
startsecs=5
priority=100

[program:nextjs]
command=node server.js
directory=/app/frontend_standalone
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
environment=PORT=3000,NODE_ENV="production",INTERNAL_BACKEND_URL="http://127.0.0.1:8000",API_V1_STR="/api/v1",NEXT_PUBLIC_API_BASE_URL="http://127.0.0.1:8000/api/v1",NODE_OPTIONS="--dns-result-order=ipv4first",NEXTAUTH_SECRET="${NEXTAUTH_SECRET:-nextauth-secret-key}",NEXTAUTH_URL="${NEXTAUTH_URL:-http://localhost:3000}"
startsecs=10
priority=200
EOF

echo "=== SUPERVISORD CONFIGURATION GENERATED ==="
echo "Configuration written to: /etc/supervisor/conf.d/supervisord.conf"
echo ""
echo "=== CONFIGURATION CONTENT ==="
cat /etc/supervisor/conf.d/supervisord.conf
echo "=== END CONFIGURATION ==="
echo ""

echo "=== STARTING SUPERVISORD ==="
echo "About to execute: /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf"

# Check if supervisord exists and is executable
if command -v /usr/bin/supervisord >/dev/null 2>&1; then
    echo "supervisord found and is executable"
else
    echo "ERROR: supervisord not found or not executable"
    exit 1
fi

# Start supervisord
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
