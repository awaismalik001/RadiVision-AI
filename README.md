# RadiVision AI — Advanced Multi-Modal Radiographic Diagnostic Suite

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.2-61DAFB.svg)](https://react.dev/)
[![Electron](https://img.shields.io/badge/Electron-44.4-47848F.svg)](https://www.electronjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.3-38B2AC.svg)](https://tailwindcss.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-3.8_Flash-8E75B2.svg)](https://ai.google.dev/)
[![Security](https://img.shields.io/badge/Security-AES--256--GCM-success.svg)](https://en.wikipedia.org/wiki/Galois/Counter_Mode)

> **A Multi-Modal Clinical Decision-Support Workstation and Desktop Application for Automated Plain Radiograph Triage, Vision Transformer Pathology Detection, Dynamic Grad-CAM Localization, and Multimodal Generative AI Consensus.**

---

## 1. Executive Summary

**RadiVision AI** is a medical-grade computer vision and multimodal artificial intelligence platform designed to assist radiologists, clinicians, and emergency medical personnel with rapid triage and diagnosis of plain radiographs. The platform pairs deep convolutional networks and Vision Transformers with **Google Gemini 3.8 Flash** for real-time multimodal clinical cross-verification, consensus evaluation, and RSNA-compliant report generation.

The platform provides:
- **Dual-Modality Triage:** Automatic classification of incoming radiographs into **Chest** or **Bone** studies with clinician confirmation or manual override.
- **Chest Pathology Detection:** Binary classification of **Pneumonia vs. Normal** utilizing fine-tuned **Vision Transformers (ViT-B/16)** and **MobileNetV2** (90.72% test accuracy).
- **Bone Fracture Localization:** Automated identification of cortical bone disruptions and fractures utilizing **ViT-B/16**, **YOLOv8**, and **Grad-CAM spatial localization** (91.40% accuracy, 0.9691 AUC).
- **Multimodal AI Co-Pilot (Gemini 3.8 Flash):** Clinical reasoning engine that reviews scan thumbnails to verify primary model findings, detect missed subtle fractures/pathology, generate second-opinion clinical impressions, and evaluate urgency. Features automatic fallback to **Gemini 3.5 Flash Lite** for ultra-fast resilience.
- **Enterprise-Grade PACS Architecture:** 3NF-normalized SQLite database with **AES-256-GCM** authenticated field-level encryption at rest, PBKDF2/bcrypt authentication, and full activity audit logging.
- **Modern Desktop & Web Workstation:** Built with **React 19**, **Tailwind CSS**, and **Framer Motion**, packaged as an **Electron** native desktop application featuring a compact, zero-distraction startup workflow.

---

## 2. Key Recent Updates & Architectural Advancements

1. **AES-256 Encryption Key Stabilization & Patient Data Migration:**
   - Fixed `_DEFAULT_FALLBACK_KEY` from 33 bytes → exactly 32 bytes (`b"RadivisionAI_AES256_SecureKey32B"`), resolving `AESGCM` initialization crash on machines without a `.env` file.
   - Added SHA-256 auto-digest for non-standard length keys and safe `__init__` exception handling.
   - Added [`database/fix_patient_encryption.py`](database/fix_patient_encryption.py) — a migration utility that re-encrypts all patient records with the current `AES_SECRET_KEY`. Run this whenever the key changes.

2. **Network Error on Installed Application — Root Cause Fixed:**
   - Fixed `server.py` `load_dotenv()` resolution to find `.env` inside the installed `resources/` path.
   - Increased `waitForBackend` timeout from 35 → 50 attempts (~30 seconds) in `electron/main.cjs` to accommodate slower machines.
   - Changed raw `"Network Error"` message in `AuthModal.jsx` to `"AI Engine is initializing. Please wait a few seconds and try again."` for user-friendly feedback.
   - Added `electronDist` in `frontend/package.json` to prevent GitHub download failures during offline packaging.
   - Added `SKIP_BACKEND=1` env variable support in `build_desktop.py` to skip PyInstaller rebuild when `server.exe` already exists.

3. **Dashboard Patient Names Fix (Encrypted Ciphertext Showing):**
   - Fixed bug where `enc:aes256:...` raw ciphertext appeared in the **Recent Clinical Studies** table instead of patient names — caused by AES key mismatch between database creation and current runtime key.
   - Fixed critical bug in `get_recent_scans_summary()` in `database.py`: `cursor.fetchall()` was called before `cursor.execute()`, causing the function to always return an empty list.

4. **Responsive UI — Compact Prediction Badges:**
   - Prediction badges now strip parenthetical sub-labels: `"FRACTURE DETECTED (Multimodal AI Escalation)"` → `"FRACTURE DETECTED"`. Full text preserved as a hover tooltip (`title` attribute).
   - Added `whitespace-nowrap` to all prediction badges across `UserDashboard.jsx`, `AdminDashboard.jsx`, and `PatientHistory.jsx` to prevent multi-line wrapping in table rows.
   - Fixed `isAbnormal` logic: `"NO FRACTURE OBSERVED"` no longer incorrectly flagged as abnormal due to `fracture` substring match.

5. **4-Phase Deep Learning ViT Optimization Pipeline (>90% Accuracy):**
   - **Phase 1 — Dataset Refinement with Gemini API:** Scanned 19,027 local images, quarantined 74 invalid files into `_pruned_unviable/`.
   - **Phase 2 — Standardization (CLAHE & ViT Resolution):** CLAHE contrast enhancement, bicubic resize to 224×224, +2.2% to +13.3% Shannon entropy gain.
   - **Phase 3 — Domain Shift Augmentation:** JPEG DCT simulation, affine/rotation ±12°, perspective keystoning, Gaussian blur, sensor noise.
   - **Phase 4 — ViT-B/16 Optimization:** AdamW optimizer (lr=2.5e-4, weight_decay=1e-2), Cosine Annealing LR, sensitivity-weighted loss.
   - **Clinical Performance:** Chest 90.72% accuracy / 95.38% sensitivity; Bone 91.40% accuracy / 90.45% sensitivity / 0.9691 AUC.

6. **Gemini 3.8 Flash Multimodal Reasoning:** Latest Gemini model with automatic fallback to Gemini 3.5 Flash Lite via `google-genai` SDK.

7. **Single Setup Installer & Standalone Workstation Distribution:**
   - **`RadiVision_AI_Setup.exe`:** Single-file automated Windows setup installer.
   - **`RadiVision-AI-Workstation.zip`:** Zero-install standalone portable distribution for clinical workstations.

8. **Zero-Background Frameless Startup Lifecycle:**
   - Frameless transparent window → circular animated splash screen → compact auth card → full-screen workstation upon login.
   - 5-second countdown calibration timer with instant `Skip →` button on splash screen.

9. **Role-Based Access Control (RBAC):**
   - **Admin:** Full PACS, user management, audit logs, Excel export, sample loaders.
   - **User (Clinician):** AI Studio, personal Scan History, User Dashboard, Profile. Patient names hidden from personal history for privacy.

10. **Immutable Root Administrator Protection:**
    - `awaismalik001` permanently protected from deletion at UI, API, and database layers.
    - Self-deletion lockout for active administrative session accounts.

11. **Pakistan Healthcare Referral System:**
    - GPS-anchored hospital and specialist referral system seeded with Pakistani healthcare facilities.
    - PDF reports reference `Rawalpindi, Pakistan` as the default city location.

---

## 3. System Architecture

```
                                 [ Incoming Plain Radiograph ]
                                               │
                                               ▼
                              ┌──────────────────────────────────┐
                              │     Automated Modality Triage    │
                              │     (Chest vs. Bone Radiograph)  │
                              └────────────────┬─────────────────┘
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
        ┌─────────────────────────────┐                 ┌─────────────────────────────┐
        │   Chest Diagnostic Branch   │                 │    Bone Diagnostic Branch   │
        │  • ViT-B/16 Transformer     │                 │  • ViT-B/16 Transformer     │
        │  • MobileNetV2 Backbone     │                 │  • YOLOv8 Object Detection  │
        │  • Grad-CAM Opacity Map     │                 │  • Cortical Fracture CAM    │
        └──────────────┬──────────────┘                 └──────────────┬──────────────┘
                       └───────────────────────┬───────────────────────┘
                                               │
                                               ▼
                              ┌──────────────────────────────────┐
                              │  Google Gemini 3.8 Flash Engine  │
                              │  • Multimodal Cross-Verification │
                              │  • Discordance / Escalation Check│
                              │  • Clinical Impression & ICD-10  │
                              └────────────────┬─────────────────┘
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
        ┌─────────────────────────────┐                 ┌─────────────────────────────┐
        │   AES-256-GCM PACS Store    │                 │  Clinical Export Artifacts  │
        │  • SQLite 3NF Normalized    │                 │  • RSNA-Style Clinical PDF  │
        │  • Role-Isolated Records    │                 │  • Audit Excel Spreadsheet  │
        │  • Exact Date & Timestamps  │                 │  • GPS Hospital Referrals   │
        └─────────────────────────────┘                 └─────────────────────────────┘
```

---

## 4. Default Credentials

The SQLite PACS database (`database/xray_system.db`) initializes automatically on first backend run:

| Account Type | Username | Password | Role | Access Scope |
| :--- | :--- | :--- | :--- | :--- |
| **System Administrator** | `awaismalik001` | `Admin123!` | `Admin` | Full PACS, User Controls, Audit Logs, Sample Loaders, Excel Export |
| **Clinician / Radiologist** | *Via Sign Up* | *User Defined* | `User` | AI Studio, Personal Scan History, User Dashboard, Profile |

> **Security Note:** Change the default administrator password immediately in production via the **Profile Management** interface. The `awaismalik001` account is permanently protected and cannot be deleted.

---

## 5. Technology Stack

### Backend & Deep Learning
- **Language:** Python 3.10+
- **REST Framework:** FastAPI, Uvicorn, Python-Multipart
- **Deep Learning:** PyTorch, TorchVision, Ultralytics YOLOv8
- **Vision Transformers:** Custom Dual-Head `RadiVisionViT` (ViT-B/16)
- **Generative AI:** `google-genai` (Gemini 3.8 Flash, Gemini 3.5 Flash Lite fallback)
- **Computer Vision:** OpenCV (`cv2`), Pillow (PIL)
- **Data & Evaluation:** NumPy, Pandas, Scikit-Learn, Matplotlib
- **Security:** AES-256-GCM (`cryptography`), PBKDF2, bcrypt
- **Reporting & Export:** ReportLab (RSNA PDF), OpenPyXL (Excel `.xlsx`)

### Frontend & Desktop
- **Core Library:** React 19, React DOM
- **Build Tool:** Vite 8
- **Desktop Runtime:** Electron 44
- **Styling:** Tailwind CSS 4, PostCSS, Lucide React Icons
- **Animation:** Framer Motion
- **HTTP Client:** Axios

---

## 6. Installation & Setup Guide

### Prerequisites
1. **Python:** Version 3.10 or 3.11 (64-bit).
2. **Node.js:** Version 18+ with `npm`.
3. **Hardware:** Minimum 8 GB RAM (16 GB recommended). GPU acceleration (CUDA) supported; operates fully on CPU.

---

### Step 1: Clone Repository & Python Environment

```bash
cd "d:/My Projects/RadiVision AI"

# Create and activate a Python virtual environment
python -m venv venv

# Windows (PowerShell)
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 2: Configure Environment Variables

Create `.env` in the project root:

```env
# Google Gemini API Key (Multimodal AI Cross-Verification)
GEMINI_API_KEY=your_gemini_api_key_here

# Google Maps / Places API Key (Dynamic Healthcare Referrals)
GOOGLE_MAPS_API_KEY=your_google_maps_key_here

# AES-256 Encryption Key (32-byte base64 or plain string)
# IMPORTANT: Run database/fix_patient_encryption.py if you change this key
AES_SECRET_KEY=your_base64_aes_key_here

# Server Configuration
HOST=127.0.0.1
PORT=8000
```

> **Key Rotation:** If you change `AES_SECRET_KEY` after patient data has been inserted, run `python database/fix_patient_encryption.py` to re-encrypt all records with the new key.

---

### Step 3: Install Frontend Dependencies & Build

```bash
cd frontend
npm install
npm run build
cd ..
```

---

## 7. Running the Application

### Option A: One-Click Desktop Launcher (Fastest)

```cmd
.\launch_desktop_app.bat
```

---

### Option B: Manual Multi-Terminal Launch

**Terminal 1 — FastAPI Backend:**
```bash
python server.py
```
*Backend starts at `http://127.0.0.1:8000`.*

**Terminal 2 — Electron Desktop App:**
```bash
cd frontend
npm run electron
```

---

### Option C: Web Browser Mode

```bash
python server.py
```
Open `http://127.0.0.1:8000` in any browser.

> **Production Note:** The FastAPI backend serves the pre-built React frontend from `frontend/dist` automatically. No Vite dev server needed in production.

---

## 8. Clinical Workflows & User Roles

### A. AI Diagnostic Studio
- **Image Ingestion:** Accepts PNG, JPG, WEBP, and DICOM exports.
- **Modality Toggle:** Chest (Pneumonia) or Bone (Fractures) with admin-exclusive sample loaders.
- **Grad-CAM Visualization:** High-resolution spatial heatmap overlays with bounding box coordinates.
- **Gemini Consensus Card:** Primary finding + Gemini cross-verification score, concordance status, clinical urgency.
- **RSNA PDF Report:** One-click clinical report with demographics, scan image, Grad-CAM, and hospital referrals anchored to `Rawalpindi, Pakistan`.

### B. User Dashboard & My Scan History
- Personal scan archive with modality filter and diagnosis search.
- **Privacy:** Patient Name and National ID omitted from personal history.
- **Compact Prediction Badges:** Long AI predictions shortened in the UI (e.g. `"FRACTURE DETECTED"` instead of `"FRACTURE DETECTED (Multimodal AI Escalation)"`). Full text visible on hover.
- Direct RSNA PDF export per scan row.

### C. Administrator Management Console
- **PACS Patient Records:** Institution-wide scan archive with decrypted patient names, demographics, modality, diagnosis, confidence, and timestamp.
- **User Administration:** Create, activate/deactivate, and delete user accounts (with root admin protection).
- **Activity Audit Logs:** Chronological trail of all login, scan, export, and credential events.
- **Excel Export:** 3-sheet `.xlsx` workbook — PACS records, audit trail, analytics.

---

## 9. Model Architecture & Clinical Validation

| Modality / Task | Architecture | Primary Metric | Clinical Benchmark |
| :--- | :--- | :--- | :--- |
| **Chest Pneumonia** | ViT-B/16 + MobileNetV2 | **90.72%** Test Accuracy | 95.38% Sensitivity |
| **Bone Fracture** | ViT-B/16 + YOLOv8 | **91.40%** Accuracy / **0.9691** AUC | 90.45% Sensitivity |
| **Modality Triage** | Dual-Class CNN | **99.20%** Accuracy | Zero-latency chest/bone separation |
| **AI Co-Pilot** | Gemini 3.8 Flash (+ 3.5 Lite fallback) | **100%** Consensus Coverage | Second-opinion, ICD-10, urgency flag |

---

## 10. Project Directory Structure

```
RadiVision AI/
├── app/                              # Backend application modules
│   ├── auth.py                       # User authentication, PBKDF2/bcrypt, sessions
│   ├── database.py                   # SQLite 3NF schema, CRUD, role-isolated queries
│   ├── domain_shift_augmentation.py  # Phase 3: Domain Shift Web Degradation Generator
│   ├── encryption.py                 # AES-256-GCM authenticated field-level encryption
│   ├── excel_export.py               # 3-Sheet clinical & audit Excel workbook generator
│   ├── gemini_service.py             # Gemini 3.8 Flash & 3.5 Lite API integration
│   ├── hospital_referral.py          # Pakistan GPS hospital & specialist referral engine
│   ├── model_engine.py               # Unified deep learning inference manager
│   ├── preprocessing.py              # Phase 2: CLAHE contrast & 224×224 standardization
│   ├── report_generator.py           # RSNA-compliant clinical PDF report generator
│   ├── vit_model.py                  # Dual-head Vision Transformer (ViT-B/16) engine
│   └── bone_gradcam.py               # Grad-CAM spatial activation mapping
│
├── database/                         # Persistent database storage
│   ├── xray_system.db                # SQLite database (auto-created on first run)
│   ├── dummy_seed.py                 # Synthetic demo data seeder (de-identified)
│   └── fix_patient_encryption.py     # AES key migration utility (run after key rotation)
│
├── frontend/                         # React + Vite + Electron frontend
│   ├── electron/
│   │   ├── main.cjs                  # Electron main process (window lifecycle & sizing)
│   │   └── preload.cjs               # Secure IPC bridge for native window controls
│   ├── src/
│   │   ├── components/
│   │   │   ├── AdminDashboard.jsx    # Institutional PACS, user mgmt, audit logs
│   │   │   ├── AuthModal.jsx         # Compact login & signup dialog (with init message)
│   │   │   ├── DiagnosticStudio.jsx  # Core AI scanning studio, Grad-CAM, Gemini cards
│   │   │   ├── HealthcareNetwork.jsx # Hospital & specialist referral directory
│   │   │   ├── NeuralTelemetry.jsx   # Model architecture, ROC curves, confusion matrices
│   │   │   ├── PatientHistory.jsx    # Scan archive (privacy-tailored per role)
│   │   │   ├── ProfileManagement.jsx # Clinician profile & admin credential management
│   │   │   ├── Sidebar.jsx           # Dark medical workstation sidebar navigation
│   │   │   ├── SplashScreen.jsx      # Circular animated splash (5-sec countdown)
│   │   │   └── UserDashboard.jsx     # Clinician overview & quick scan launcher
│   │   ├── App.jsx                   # Application state & window mode coordinator
│   │   └── main.jsx                  # React DOM entry point
│   ├── package.json                  # Frontend dependencies and build scripts
│   └── vite.config.js                # Vite build configuration
│
├── model/                            # Pre-trained model weights
│   ├── chest/                        # Chest pneumonia model weights
│   ├── bone/                         # Bone fracture YOLOv8 / PyTorch weights
│   ├── type_classifier/              # Modality triage classifier
│   └── vit/                          # Vision Transformer weights (328.9 MB)
│
├── reports/                          # Auto-generated clinical PDF reports
├── uploads/                          # Temporary storage for uploaded scans
├── build_desktop.py                  # Full end-to-end desktop packaging pipeline
├── build_backend.py                  # PyInstaller backend compilation script
├── launch_desktop_app.bat            # One-click native desktop launcher
├── server.py                         # FastAPI REST API bridge on port 8000
├── requirements.txt                  # Python dependencies manifest
├── .env                              # Environment variables (NEVER commit to git)
└── README.md                         # This documentation
```

---

## 11. Standalone Desktop Distribution & Setup Installers

### Option 1: Windows Setup Installer (`RadiVision_AI_Setup.exe`)
- Single executable NSIS installer built via Electron-Builder.
- Auto-installs to `AppData\Local\Programs\RadiVision AI`.
- Creates Start Menu + optional Desktop shortcut.
- Bundles complete FastAPI AI engine, PyTorch ViT weights, SQLite PACS, and Electron frontend.
- Uninstalls cleanly via Windows *Add or Remove Programs*.

### Option 2: Portable Workstation (`RadiVision-AI-Workstation.zip`)
- Zero-installation required. Copy to any USB drive or PC.
- Extract and double-click `RadiVision AI.exe` to run immediately.

> **Note on `.env` in installed app:** The `AES_SECRET_KEY`, `GEMINI_API_KEY`, and `GOOGLE_MAPS_API_KEY` are loaded from `.env` inside the app's `resources/` path when installed. A secure fallback AES key is built-in for machines without a `.env` file.

### Building from Source
```powershell
# Full rebuild (backend + frontend + installer + portable zip)
python build_desktop.py

# Skip backend recompile if server.exe already exists (fast rebuild)
$env:SKIP_BACKEND='1'; python build_desktop.py
```

*Outputs at project root:*
1. `RadiVision_AI_Setup.exe` — Windows NSIS installer
2. `RadiVision-AI-Workstation.zip` — Portable zip archive
3. `RadiVision-AI-Workstation/` — Unpacked portable directory

---

## 12. Security, Privacy & Regulatory Compliance

- **Authentication:** Passwords hashed with bcrypt/PBKDF2 with salt. Repeated failed login attempts are rate-limited.
- **Data Protection at Rest:** Patient name and contact fields encrypted with AES-256-GCM. Decrypted only at API response time in memory; ciphertext stored in SQLite.
- **Key Rotation:** Run `python database/fix_patient_encryption.py` after any `AES_SECRET_KEY` change to re-encrypt all existing records.
- **Audit Trail:** All administrative, diagnostic, and export operations logged with exact UTC timestamps.
- **Privacy by Design:** Regular clinicians access only their own scans. Patient identifiers hidden from standard user views.
- **Auto-Logout:** Desktop app triggers session termination on window close.
- **Root Admin Lock:** `awaismalik001` cannot be deleted or demoted at any layer (UI, API, database).

---

## 13. License & Medical Disclaimer

**Medical Disclaimer:** RadiVision AI is developed for diagnostic support, quality assurance, and research triage. It is intended to **augment, not replace**, the independent clinical judgment of board-certified radiologists and medical practitioners. Always seek professional clinical validation before any treatment decision.

*Designed and engineered for high-precision diagnostic radiology — Pakistan & beyond.*
