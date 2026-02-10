#!/bin/bash
# Bootstrap script for EC2 instance.
# Installs Docker, clones the project, builds and starts all services,
# ingests SPY data, and sets up SSL.
#
# Variables injected by Terraform templatefile():
#   ${repo_url}           — Git repository URL
#   ${domain_name}        — Domain for the app (and SSL cert)
#   ${admin_email}        — Email for Let's Encrypt
#   ${aws_region}         — AWS region (for Secrets Manager)
#   ${openai_secret_name} — Secrets Manager secret name

set -euo pipefail
exec > /var/log/user-data.log 2>&1
echo "=== Bootstrap started at $(date) ==="

# ── Install Docker + Git LFS ─────────────────────────────────────

yum update -y
yum install -y docker git git-lfs
systemctl enable docker
systemctl start docker
usermod -aG docker ec2-user

# ── Install Docker Compose v2 ───────────────────────────────────

COMPOSE_VERSION="v2.24.0"
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL "https://github.com/docker/compose/releases/download/$${COMPOSE_VERSION}/docker-compose-linux-x86_64" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

echo "Docker Compose installed: $(docker compose version)"

# ── Clone project (with LFS data) ────────────────────────────────

cd /opt
git lfs install
git clone ${repo_url} pineback
cd pineback
git lfs pull

echo "Project cloned from ${repo_url}"

# ── Build and start all services ─────────────────────────────────

export AWS_DEFAULT_REGION="${aws_region}"
export OPENAI_SECRET_NAME="${openai_secret_name}"

docker compose -f docker-compose.prod.yml up -d --build

echo "Services started. Waiting for database to be ready..."

# Poll until PgBouncer can accept connections (up to 120s)
for i in $(seq 1 24); do
  if docker compose -f docker-compose.prod.yml exec -T app \
    python -c "import psycopg2, os; psycopg2.connect(os.environ['DATABASE_URL'])" 2>/dev/null; then
    echo "Database is ready (after ~$((i * 5))s)"
    break
  fi
  echo "  Waiting for database... ($((i * 5))s)"
  sleep 5
done

# ── Ingest SPY data ──────────────────────────────────────────────

echo "Ingesting SPY data..."
docker compose -f docker-compose.prod.yml exec -T app python -m server.ingest \
  || echo "WARNING: Data ingestion failed. Run manually: docker compose -f docker-compose.prod.yml exec app python -m server.ingest"

echo "Data ingestion step complete."

# ── SSL Certificate (Let's Encrypt via certbot) ──────────────────

echo "Setting up SSL for ${domain_name}..."
docker compose -f docker-compose.prod.yml exec -T nginx sh -c "
  apk add --no-cache certbot certbot-nginx 2>/dev/null &&
  certbot --nginx \
    -d ${domain_name} \
    --non-interactive \
    --agree-tos \
    -m ${admin_email} \
    --redirect
" || echo "WARNING: SSL setup failed. DNS may not have propagated yet. Run manually later."

echo "=== Bootstrap complete at $(date) ==="
echo "App URL: https://${domain_name}"
