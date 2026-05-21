# Fanoni Imaging

Web-based DICOM viewer and PACS platform for Fanoni Health. Built on OHIF Viewer v3 + Orthanc, deployed at **[imaging.fanoni.ai](https://imaging.fanoni.ai)**.

**Docs:** [docin.fanoni.ai](https://docin.fanoni.ai) · **Viewer:** [imaging.fanoni.ai](https://imaging.fanoni.ai) · **EHR:** [ehr.fanoni.ai](https://ehr.fanoni.ai)

---

## What's in this repo

| Path | What it is |
|---|---|
| `platform/app/` | OHIF viewer shell — Webpack/Vite build, `config/default.js` |
| `platform/core/` | Services, managers, extension/mode registry |
| `platform/ui/` · `platform/ui-next/` | React component library (Tailwind CSS) |
| `extensions/` | Cornerstone3D, DICOM SR, SEG, RT, TMTV, microscopy |
| `modes/` | Longitudinal (MPR), segmentation, TMTV workflow modes |
| `platform/docs/` | Docusaurus documentation site → docin.fanoni.ai |
| `docker/` | Orthanc PACS container + config |
| `scripts/seed_real_dicoms.py` | Seeds 7 real-pixel demo studies into Orthanc |
| `deploy/nginx-imaging.fanoni.ai.conf` | Production nginx config |
| `.github/workflows/deploy.yml` | CI/CD: build OHIF → rsync to VPS |
| `.github/workflows/build-docs.yml` | CI/CD: build Docusaurus → rsync to VPS |

---

## Live features

- **Multi-planar reconstruction (MPR)** — axial, sagittal, coronal linked views
- **3D volume rendering** — GPU-accelerated via Cornerstone3D
- **Segmentation** — DICOM SEG import/export, label map overlay
- **Hanging protocols** — configurable display rules per modality
- **Measurements & annotations** — length, angle, ROI, Hounsfield units
- **DICOMweb** — QIDO-RS study list, WADO-RS retrieval, STOW-RS upload
- **Orthanc PACS** — on-premise DICOM storage, C-STORE/C-FIND/C-MOVE
- **Fanoni branding** — custom logo, no investigational use banner
- **7 demo studies** — Brain MRI (80 instances), CT Abdomen (80), Knee MRI (64), CXR, US, Mammogram, Shoulder X-Ray — all with real pixel data

---

## Infrastructure

| Service | URL | VPS path |
|---|---|---|
| Fanoni Imaging viewer | `imaging.fanoni.ai` | `/var/www/imaging.fanoni.ai/` |
| Fanoni Imaging docs | `docin.fanoni.ai` | `/var/www/docin.fanoni.ai/` |
| Orthanc PACS | internal port 8042/4242 | `/opt/fanoni/imaging/docker/` |

nginx proxies `/dicomweb/` → `http://localhost:8042/dicom-web/` and serves the OHIF SPA with an SPA fallback.

---

## Local development

```bash
# Clone
git clone https://github.com/Fanoni-ai/fanoni-imaging.git
cd fanoni-imaging

# Install
yarn install --frozen-lockfile

# Start Orthanc PACS locally
cd docker && docker compose up -d && cd ..

# Seed demo studies into local Orthanc
python3 scripts/seed_real_dicoms.py

# Run OHIF dev server (proxies /dicomweb → localhost:8042)
cd platform/app
PROXY_DOMAIN=http://localhost:8042 \
PROXY_PATH_REWRITE_FROM=/dicomweb \
PROXY_PATH_REWRITE_TO=/dicom-web \
yarn dev
# → http://localhost:3000
```

### Docs dev server

```bash
cd platform/docs
bun install
bun run dev
# → http://localhost:8001
```

---

## Deploy

**Viewer** — push to `master` → GitHub Actions builds OHIF (~15 min) → rsync to `/var/www/imaging.fanoni.ai/`.

**Docs** — same push → separate job builds Docusaurus (~10 min) → rsync to `/var/www/docin.fanoni.ai/`.

Both jobs use `VPS_HOST` and `VPS_SSH_KEY` secrets. Manual trigger: GitHub → Actions → Run workflow.

---

## Orthanc on VPS

```bash
# Start (first time)
ssh root@147.93.86.15
cd /opt/fanoni/imaging/docker && docker compose up -d

# Seed demo studies
python3 scripts/seed_real_dicoms.py  # run locally, points to port 8042
```

Orthanc web UI: `http://147.93.86.15:8042` (restrict in production via nginx `allow/deny`).

---

## Configuration

All viewer config lives in `platform/app/public/config/default.js`:

- `defaultDataSourceName: 'orthanc'` — points to local Orthanc via relative `/dicomweb` path
- `investigationalUseDialog: { option: 'never' }` — banner suppressed
- `whiteLabeling.createLogoComponentFn` — Fanoni Imaging logo (cyan grid + wordmark)

---

## License

Built on [OHIF Viewers](https://github.com/OHIF/Viewers) — MIT license.
Fanoni customizations © Fanoni Health.
