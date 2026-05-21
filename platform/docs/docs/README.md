---
id: Introduction
slug: /
sidebar_position: 1
---

# Fanoni Imaging

Fanoni Imaging is a web-based DICOM viewer and clinical imaging platform built for modern radiology workflows. It connects directly to your PACS via DICOMweb and delivers advanced visualization — MPR, 3D rendering, segmentation, and hanging protocols — in the browser with no plugins required.

## Key capabilities

- **Multi-planar reconstruction (MPR)** — axial, sagittal, coronal views with linked cursor
- **3D volume rendering** — GPU-accelerated with Cornerstone3D
- **Segmentation** — DICOM SEG import/export, label map overlay
- **Hanging protocols** — configurable display rules per modality and study type
- **Measurements & annotations** — length, angle, ROI, Hounsfield units, saved per study
- **DICOMweb native** — QIDO-RS study list, WADO-RS pixel retrieval, STOW-RS upload
- **Orthanc PACS** — ships with a bundled Orthanc container for on-premise storage

## Quick links

| | |
|---|---|
| **Open the viewer** | [imaging.fanoni.ai](https://imaging.fanoni.ai) |
| **Getting started** | [Development setup](development/getting-started) |
| **Configuration** | [Config files](configuration/configurationFiles) |
| **Deploy** | [Production deployment](deployment/build-for-production) |
| **User guide** | [Using the viewer](user-guide/viewer/index) |
| **GitHub** | [Fanoni-ai/fanoni-imaging](https://github.com/Fanoni-ai/fanoni-imaging) |

## Architecture overview

Fanoni Imaging is composed of:

- **`platform/app`** — the application shell, Vite/Webpack config, and `config/default.js`
- **`platform/core`** — services, managers, and the extension/mode registry
- **`platform/ui` / `platform/ui-next`** — React component library (Tailwind CSS)
- **`extensions/`** — modality-specific capabilities (Cornerstone3D, DICOM SR, SEG, RT)
- **`modes/`** — workflow compositions (longitudinal, segmentation, TMTV)

See [Architecture](development/architecture) for a full breakdown.
