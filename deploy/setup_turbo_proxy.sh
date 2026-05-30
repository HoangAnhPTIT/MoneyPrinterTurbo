#!/usr/bin/env bash
# Idempotent HTTPS + Basic-Auth reverse-proxy setup for the turbo
# (MoneyPrinterTurbo) Streamlit WebUI, behind an existing containerized nginx
# managed by another docker-compose project on the same host.
#
# Required env vars (set by .github/workflows/deploy-turbo.yml):
#   TURBO_DOMAIN            e.g. turbo.callmaster.site
#   LETSENCRYPT_EMAIL       contact email for the LE account
#   NGINX_PROJECT_DIR       compose dir of the existing nginx, e.g. /root/callmaster/infrastructure
#   NGINX_CONTAINER         name of the existing nginx container, e.g. callmaster-nginx
#   TURBO_BASIC_AUTH_USER   basic-auth username
#   TURBO_BASIC_AUTH_PASS   basic-auth password
#
# Optional:
#   TURBO_CONTAINER         our webui container name (default: moneyprinterturbo-webui)
#   NGINX_CONF_DIR          host dir holding site files (default: /opt/callmaster/nginx)
#   NGINX_NETWORK           docker network name (auto-detected if empty)

set -euo pipefail

: "${TURBO_DOMAIN:?TURBO_DOMAIN is required}"
: "${LETSENCRYPT_EMAIL:?LETSENCRYPT_EMAIL is required}"
: "${NGINX_PROJECT_DIR:?NGINX_PROJECT_DIR is required}"
: "${NGINX_CONTAINER:?NGINX_CONTAINER is required}"
: "${TURBO_BASIC_AUTH_USER:?TURBO_BASIC_AUTH_USER is required}"
: "${TURBO_BASIC_AUTH_PASS:?TURBO_BASIC_AUTH_PASS is required}"
TURBO_CONTAINER="${TURBO_CONTAINER:-moneyprinterturbo-webui}"
NGINX_CONF_DIR="${NGINX_CONF_DIR:-/opt/callmaster/nginx}"
COMPOSE_FILE="$NGINX_PROJECT_DIR/docker-compose.yml"
SITE_CONF_HOST="$NGINX_CONF_DIR/${TURBO_DOMAIN}.conf"
SITE_CONF_GUEST="/etc/nginx/conf.d/${TURBO_DOMAIN}.conf"
HTPASSWD_HOST="$NGINX_CONF_DIR/${TURBO_DOMAIN}.htpasswd"
HTPASSWD_GUEST="/etc/nginx/conf.d/${TURBO_DOMAIN}.htpasswd"
# Generated videos live in MoneyPrinterTurbo's storage dir on the host (mounted
# into the webui container at /MoneyPrinterTurbo/storage). To let nginx serve
# them at /videos/, the same host dir is bind-mounted read-only into the nginx
# container as well.
TURBO_STORAGE_DIR="${TURBO_STORAGE_DIR:-/opt/turbo/storage}"
STORAGE_MOUNT_GUEST="/var/www/${TURBO_DOMAIN}-videos"

log() { printf '\n\033[1;36m== %s ==\033[0m\n' "$*"; }

# ── Preconditions ────────────────────────────────────────────────────────────
[ -f "$COMPOSE_FILE" ] || { echo "ERROR: $COMPOSE_FILE not found" >&2; exit 1; }
docker inspect "$TURBO_CONTAINER" >/dev/null 2>&1 || { echo "ERROR: $TURBO_CONTAINER not running" >&2; exit 1; }
docker inspect "$NGINX_CONTAINER" >/dev/null 2>&1 || { echo "ERROR: $NGINX_CONTAINER not running" >&2; exit 1; }

# ── 1. Detect / select the shared docker network ─────────────────────────────
log "Detecting shared docker network"
if [ -z "${NGINX_NETWORK:-}" ]; then
  NGINX_NETWORK=$(
    docker inspect "$NGINX_CONTAINER" \
      --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' \
      | tr ' ' '\n' | grep -iE 'dev|public|proxy|web' | head -1
  )
  if [ -z "$NGINX_NETWORK" ]; then
    NGINX_NETWORK=$(
      docker inspect "$NGINX_CONTAINER" \
        --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' \
        | tr ' ' '\n' | grep -v '^$' | head -1
    )
  fi
fi
[ -n "$NGINX_NETWORK" ] || { echo "ERROR: no network found on $NGINX_CONTAINER" >&2; exit 1; }
echo "Using network: $NGINX_NETWORK"

if docker inspect "$TURBO_CONTAINER" \
     --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{"\n"}}{{end}}' \
   | grep -qx "$NGINX_NETWORK"; then
  echo "$TURBO_CONTAINER already on $NGINX_NETWORK"
else
  docker network connect "$NGINX_NETWORK" "$TURBO_CONTAINER"
  echo "Connected $TURBO_CONTAINER → $NGINX_NETWORK"
fi

# ── 2. Generate htpasswd (apr1 — no apache2-utils needed) ─────────────────────
log "Writing htpasswd for Basic Auth"
mkdir -p "$NGINX_CONF_DIR"
HASH=$(openssl passwd -apr1 "$TURBO_BASIC_AUTH_PASS")
printf '%s:%s\n' "$TURBO_BASIC_AUTH_USER" "$HASH" > "$HTPASSWD_HOST"
chmod 644 "$HTPASSWD_HOST"

# ── 3. Ensure bind-mounts (conf + htpasswd + videos) in the nginx compose ─────
log "Ensuring site-config + htpasswd + videos bind-mounts in $COMPOSE_FILE"
mkdir -p "$TURBO_STORAGE_DIR"
RECREATE_NGINX=0
for PAIR in "${SITE_CONF_HOST}:${SITE_CONF_GUEST}:ro" "${HTPASSWD_HOST}:${HTPASSWD_GUEST}:ro" "${TURBO_STORAGE_DIR}:${STORAGE_MOUNT_GUEST}:ro"; do
  GUEST="${PAIR#*:}"; GUEST="${GUEST%:ro}"
  if grep -qF "$GUEST" "$COMPOSE_FILE"; then
    echo "Mount already present: $GUEST"
  else
    echo "Adding mount: $PAIR"
    python3 - "$COMPOSE_FILE" "$PAIR" <<'PYEOF'
import re, sys
path, mount_value = sys.argv[1], sys.argv[2]
with open(path) as f:
    lines = f.read().splitlines()
in_nginx = in_volumes = False
volume_indent = None; last_volume_idx = -1; nginx_service_indent = None
for i, line in enumerate(lines):
    stripped = line.lstrip(); indent = len(line) - len(stripped)
    if re.match(r'^(\s*)nginx:\s*$', line):
        in_nginx = True; in_volumes = False; nginx_service_indent = indent; continue
    if in_nginx and indent <= (nginx_service_indent or 0) and stripped \
       and not stripped.startswith('#') and stripped != 'volumes:':
        if not in_volumes:
            in_nginx = False; continue
    if in_nginx and re.match(r'^\s+volumes:\s*$', line) and indent > (nginx_service_indent or 0):
        in_volumes = True; volume_indent = None; continue
    if in_volumes:
        if stripped.startswith('- '):
            if volume_indent is None: volume_indent = indent
            if indent == volume_indent: last_volume_idx = i
        elif stripped.startswith('#') or not stripped:
            pass
        elif indent <= (nginx_service_indent or 0) + 2:
            in_volumes = False
if last_volume_idx < 0:
    print("ERROR: could not locate nginx volumes block", file=sys.stderr); sys.exit(1)
lines.insert(last_volume_idx + 1, ' ' * volume_indent + '- ' + mount_value)
with open(path, 'w') as f:
    f.write('\n'.join(lines) + '\n')
print(f"Inserted after line {last_volume_idx + 1}")
PYEOF
    RECREATE_NGINX=1
  fi
done

# ── 4. HTTP-only config (ACME challenge) if cert not yet present ──────────────
log "Writing site config"
CERT_DIR="/etc/letsencrypt/live/${TURBO_DOMAIN}"
if [ ! -f "${CERT_DIR}/fullchain.pem" ]; then
  cat > "$SITE_CONF_HOST" <<EOF
# Auto-generated by turbo/setup_turbo_proxy.sh — do not hand-edit.
server {
    listen 80;
    server_name ${TURBO_DOMAIN};
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 200 'cert pending'; add_header Content-Type text/plain; }
}
EOF
  echo "HTTP-only config written (cert not yet issued)"
else
  echo "Cert already exists; will write full HTTPS config below"
fi

# ── 5. Apply mounts: recreate nginx if needed, else reload ────────────────────
log "Applying nginx changes"
if [ "${RECREATE_NGINX:-0}" = "1" ]; then
  (cd "$NGINX_PROJECT_DIR" && docker compose up -d nginx)
  sleep 3
else
  docker exec "$NGINX_CONTAINER" nginx -t
  docker exec "$NGINX_CONTAINER" nginx -s reload
fi

# ── 6. Issue cert via certbot webroot (only if missing) ───────────────────────
if [ ! -f "${CERT_DIR}/fullchain.pem" ]; then
  log "Issuing Let's Encrypt certificate"
  if ! command -v certbot >/dev/null 2>&1; then
    apt-get update -qq
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq certbot
  fi
  mkdir -p /var/www/certbot
  certbot certonly --webroot -w /var/www/certbot -d "$TURBO_DOMAIN" \
    --non-interactive --agree-tos -m "$LETSENCRYPT_EMAIL" --keep-until-expiring
  echo "Cert issued at ${CERT_DIR}/"
else
  log "Certificate already present — skipping issuance"
fi

# ── 7. Full HTTPS config with Basic Auth + WebSocket upgrade ──────────────────
log "Writing final HTTPS config"
cat > "$SITE_CONF_HOST" <<EOF
# Auto-generated by turbo/setup_turbo_proxy.sh — do not hand-edit.
server {
    listen 80;
    server_name ${TURBO_DOMAIN};
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://\$host\$request_uri; }
}

server {
    listen 443 ssl;
    http2 on;
    server_name ${TURBO_DOMAIN};

    ssl_certificate     ${CERT_DIR}/fullchain.pem;
    ssl_certificate_key ${CERT_DIR}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    auth_basic           "turbo";
    auth_basic_user_file ${HTPASSWD_GUEST};

    # Generated videos: browse + stream MoneyPrinterTurbo's storage dir.
    # e.g. https://${TURBO_DOMAIN}/videos/tasks/<task-id>/final-1.mp4
    # Inherits the Basic Auth above. autoindex lets you browse task folders.
    location /videos/ {
        alias ${STORAGE_MOUNT_GUEST}/;
        autoindex on;
        autoindex_localtime on;
        autoindex_exact_size off;
        add_header Accept-Ranges bytes;          # byte-range requests → seekable playback
        sendfile on;
        tcp_nopush on;
    }

    location / {
        proxy_pass http://${TURBO_CONTAINER}:8501;
        proxy_http_version 1.1;
        # Streamlit uses websockets for the live UI.
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Renders can take minutes; keep the upgraded connection open.
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        proxy_buffering off;
        client_max_body_size 200M;
    }
}
EOF

docker exec "$NGINX_CONTAINER" nginx -t
docker exec "$NGINX_CONTAINER" nginx -s reload
echo "Full HTTPS config applied"

# ── 8. Install renewal hook (reload containerized nginx on auto-renew) ────────
log "Ensuring renewal hook"
HOOK_DIR=/etc/letsencrypt/renewal-hooks/deploy
mkdir -p "$HOOK_DIR"
HOOK_FILE="$HOOK_DIR/reload-${NGINX_CONTAINER}.sh"
if [ ! -f "$HOOK_FILE" ]; then
  cat > "$HOOK_FILE" <<EOF
#!/usr/bin/env bash
docker exec ${NGINX_CONTAINER} nginx -s reload
EOF
  chmod +x "$HOOK_FILE"
  echo "Installed $HOOK_FILE"
else
  echo "Renewal hook already present"
fi

log "✓ HTTPS + Basic Auth setup complete for https://${TURBO_DOMAIN}/"
