#!/bin/bash
# Bootstrap script for EC2 instance.
# Installs Docker, clones the project, builds and starts all services,
# ingests SPY data, and sets up SSL.
#
# Variables injected by Terraform templatefile():
#   ${repo_url}    — Git repository URL
#   ${domain_name} — Domain for the app (and SSL cert)
#   ${admin_email} — Email for Let's Encrypt

set -euo pipefail
exec > /var/log/user-data.log 2>&1
echo "=== Bootstrap started at $(date) ==="

# ── Install Docker ───────────────────────────────────────────────

yum update -y
yum install -y docker git
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

# ── Clone project ────────────────────────────────────────────────

cd /opt
git clone ${repo_url} pineback
cd pineback

echo "Project cloned from ${repo_url}"

# ── Build and start all services ─────────────────────────────────

docker compose -f docker-compose.prod.yml up -d --build

echo "Services started. Waiting for database to be ready..."
sleep 25

# ── Ingest SPY data ──────────────────────────────────────────────

echo "Ingesting SPY data..."
docker compose -f docker-compose.prod.yml exec -T app python -m server.ingest

echo "Data ingestion complete."

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
