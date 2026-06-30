# Fanoni Imaging — Production Deployment

This document is the runbook for deploying **imaging.fanoni.ai**: the OHIF-based
viewer (static SPA) plus the Orthanc PACS behind it.

## Architecture

```
                      ┌─────────────────────────── VPS ───────────────────────────┐
   Browser ──HTTPS──► │  nginx (TLS, host)                                          │
                      │   ├─ /            → static OHIF in /var/www/imaging.fanoni.ai│
                      │   └─ /dicomweb/   → 127.0.0.1:8042/dicom-web/  (READ-ONLY)   │
                      │                     (+ injects Orthanc Basic auth)           │
                      │                                                             │
                      │  Docker: orthancteam/orthanc                                │
                      │   ├─ 127.0.0.1:8042  REST + DICOMweb (auth required)        │
                      │   └─ 127.0.0.1:4242  DICOM (internal only)                  │
                      └─────────────────────────────────────────────────────────────┘
```

**Security model**

- nginx is the **only** public entrypoint. Orthanc's ports are bound to `127.0.0.1`.
- The public `/dicomweb` route is **read-only** — `limit_except GET` blocks STOW/DELETE,
  and the viewer also has `dicomUploadEnabled`/`supportsReject` disabled.
- Orthanc **requires authentication**; credentials live only in `docker/.env` and an
  uncommitted nginx snippet. With no users defined it fails closed (denies all).
- The Orthanc admin API is **not** exposed publicly — reach it via SSH tunnel.

> The seed data is synthetic. If real PHI is ever introduced, add user-level auth in
> front of the viewer (OHIF OpenID) — DICOMweb read is otherwise public by design.

## One-time server setup

### 1. Orthanc (Docker)

```bash
cd docker
cp .env.example .env
# Edit .env: set a strong ORTHANC_PASSWORD, and the FHIR bot URL/token if used.

docker compose up -d        # run from docker/ so .env resolves for both
docker compose logs -f orthanc
```

### 2. nginx (host)

```bash
cp deploy/nginx-imaging.fanoni.ai.conf /etc/nginx/sites-available/imaging.fanoni.ai
ln -s /etc/nginx/sites-available/imaging.fanoni.ai /etc/nginx/sites-enabled/

# Orthanc Basic-auth snippet (NOT committed — holds credentials).
# Values must match docker/.env:
export ORTHANC_USERNAME=fanoni ORTHANC_PASSWORD='<the same password>'
mkdir -p /etc/nginx/snippets
printf 'proxy_set_header Authorization "Basic %s";\n' \
  "$(printf '%s' "$ORTHANC_USERNAME:$ORTHANC_PASSWORD" | base64)" \
  > /etc/nginx/snippets/fanoni-orthanc-auth.conf

certbot --nginx -d imaging.fanoni.ai
nginx -t && systemctl reload nginx
```

### 3. Deploy user + CI secrets

Create a non-root `deploy` user that owns `/var/www/imaging.fanoni.ai` and may reload
nginx without a password:

```bash
useradd -m -s /bin/bash deploy
mkdir -p /var/www/imaging.fanoni.ai && chown -R deploy:deploy /var/www/imaging.fanoni.ai
echo 'deploy ALL=(root) NOPASSWD: /usr/sbin/nginx -t, /bin/systemctl reload nginx' \
  > /etc/sudoers.d/deploy-nginx
# add the CI public key to /home/deploy/.ssh/authorized_keys
```

GitHub repo secrets used by `.github/workflows/deploy.yml`:

| Secret        | Purpose                                   |
|---------------|-------------------------------------------|
| `VPS_HOST`    | server hostname/IP                        |
| `VPS_SSH_KEY` | private key for the `deploy` user         |
| `VPS_USER`    | optional; defaults to `deploy`            |

## Continuous deployment

Pushes to `master` trigger `Deploy to imaging.fanoni.ai`, which:

1. installs the **whole workspace from the repo root** (`yarn install --frozen-lockfile`),
2. builds the viewer (`platform/app` → `yarn build:viewer`, `APP_CONFIG=config/default.js`),
3. scp's `platform/app/dist/*` to `/var/www/imaging.fanoni.ai/`,
4. `sudo nginx -t && sudo systemctl reload nginx`.

Concurrency is capped so a newer push cancels an in-flight deploy.

## Seeding demo studies

`scripts/seed_real_dicoms.py` loads 7 synthetic studies. Paths resolve relative to the
repo, and it authenticates with Orthanc:

```bash
pip install pydicom
export ORTHANC_USERNAME=fanoni ORTHANC_PASSWORD='<password>'
# Local Orthanc is on 8042; from the VPS use an SSH tunnel or run on the host.
python3 scripts/seed_real_dicoms.py --wipe   # --wipe clears existing studies first
```

`--wipe` is required to delete existing data; without it the script only adds studies.

## Local development

```bash
cd docker && docker compose up -d        # Orthanc on 127.0.0.1:8042
yarn install                             # repo root
yarn dev                                 # OHIF on http://localhost:3000
```

The dev server proxies `/dicomweb` → `http://localhost:8042` by default. Override with
`ORTHANC_PROXY_TARGET=http://host:port`.

## Operations

- **Admin UI / REST:** `ssh -L 8042:127.0.0.1:8042 deploy@imaging.fanoni.ai`, then open
  `http://localhost:8042/` (Basic auth = `ORTHANC_USERNAME`/`ORTHANC_PASSWORD`).
- **Backups:** the `orthanc-storage` Docker volume holds all studies — snapshot it.
- **Rotate credentials:** update `docker/.env`, `docker compose up -d`, then regenerate
  `/etc/nginx/snippets/fanoni-orthanc-auth.conf` and `systemctl reload nginx`.
