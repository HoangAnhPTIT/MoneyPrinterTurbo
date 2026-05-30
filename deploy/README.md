# deploy — our MoneyPrinterTurbo deployment kit

Deploys **this repo** (our fork) to https://turbo.callmaster.site behind nginx
Basic Auth. Driven by `.github/workflows/deploy-turbo.yml`.

## What's different from upstream's deploy
The original deploy (in the `makevideo` repo) cloned **upstream**
`harry0703/MoneyPrinterTurbo` at a pinned tag. This one ships **our own source** —
the workflow rsyncs this repo into `/opt/turbo/src` on the server and builds it
there. No clone, no pinned tag: whatever is on `main` is what deploys.

## Flow (per push to `main` or manual dispatch)
1. rsync `deploy/` → `/opt/turbo/` (this kit)
2. rsync repo source → `/opt/turbo/src/` (our app, webui, Dockerfile, …)
3. `gen_config.py` patches our `config.example.toml` with secrets → `config.toml`
4. `docker compose -f docker-compose.turbo.yml up -d --build` (builds `./src`)
5. wait for WebUI on `127.0.0.1:8501`
6. `setup_turbo_proxy.sh` configures nginx HTTPS + Basic Auth
7. smoke-test auth enforcement

## CPU-only
Server has no GPU. `subtitle_provider = "edge"` (never `whisper`). Heavy work is
CPU (FFmpeg / Manim render) or off-host (DeepSeek, Pexels, Edge-TTS).

## Required GitHub config
Secrets: `SSH_HOST`, `SSH_PRIVATE_KEY`, `TURBO_DEEPSEEK_API_KEY`,
`TURBO_PEXELS_API_KEY`, `TURBO_BASIC_AUTH_USER`, `TURBO_BASIC_AUTH_PASS`,
`LETSENCRYPT_EMAIL`.
Variables: `TURBO_DOMAIN=turbo.callmaster.site`, `NGINX_PROJECT_DIR`,
`NGINX_CONTAINER`, optionally `SSH_PORT`, `SSH_USER`, `TURBO_DEPLOY_PATH`,
`NGINX_CONF_DIR`.

These mirror the names already configured for the original deploy, so the same
repo/org secrets can be reused — just set them on **this** repo.
