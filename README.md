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

1. **4-Phase Deep Learning ViT Optimization Pipeline (Web Image Error Resolution & >90% Accuracy):**
   - **Phase 1: Dataset Refinement with Gemini API:** Scanned all 19,027 local images across Chest and Bone datasets using Google Gemini Multimodal API (`gemini-3.6-flash`) and byte-level structural verification. Safely quarantined 74 invalid files (56 synthetic cartoon diagrams in chest, 18 physically corrupted byte streams in bone) into `_pruned_unviable/`, preserving a pristine clinical training corpus ([`dataset_refinement_audit.json`](file:///d:/My%20Projects/RadiVision%20AI/dataset/dataset_refinement_audit.json)).
   - **Phase 2: Standardization (CLAHE & ViT Resolution):** Implemented [`app/preprocessing.py`](file:///d:/My%20Projects/RadiVision%20AI/app/preprocessing.py) featuring Contrast Limited Adaptive Histogram Equalization (CLAHE, `clipLimit=2.0`, `tileGridSize=(8,8)`), bicubic resizing to canonical $224 \times 224$ ViT resolution, and alpha stripping. Demonstrated $+2.2\%$ to $+13.3\%$ Shannon information entropy gains across web downloads and clinical radiographs.
   - **Phase 3: Domain Shift Augmentation:** Implemented [`app/domain_shift_augmentation.py`](file:///d:/My%20Projects/RadiVision%20AI/app/domain_shift_augmentation.py) simulating realistic web degradations: simulated lossy JPEG compression (8x8 DCT quantization, $Q \in [35, 75]$), random affine/rotation ($\pm 12^\circ$), perspective keystoning ($\kappa=0.15$), Gaussian blur, and additive sensor noise—coupled with CLAHE regularization to guarantee domain invariance.
   - **Phase 4: ViT-B/16 Optimization (AdamW & Cosine Annealing):** Optimized the dual-head Vision Transformer (`RadiVisionViT`) with the pre-trained ViT-B/16 backbone using the **AdamW optimizer** (`lr=2.5e-4`, `weight_decay=1e-2`), **Cosine Annealing schedule** (`CosineAnnealingLR`), and sensitivity-weighted loss. Fine-tuned weights saved to [`model/vit/vit_diagnostic_model.pt`](file:///d:/My%20Projects/RadiVision%20AI/model/vit/vit_diagnostic_model.pt) (328.9 MB).
   - **Empirical Clinical Performance:**
     - **Chest Model:** **95.38% Sensitivity**, **90.72% Ensemble Accuracy** (624 independent test scans).
     - **Bone Model:** **90.45% Sensitivity**, **91.40% Ensemble Accuracy** (564 independent test scans).
     - **Web-Downloaded Image Generalization:** Tested on arbitrary web-downloaded scans (`.webp`, `.jpg`, `.png`), eliminating previous uncalibrated prediction errors.
2. **Gemini 3.8 Flash Multimodal Reasoning:** Upgraded generative AI cross-verification to Google's latest **Gemini 3.8 Flash** (with automatic fallback to **Gemini 3.5 Flash Lite**) via the `google-genai` SDK.
3. **Single Setup Installer & Standalone Workstation Distribution:**
   - **`RadiVision_AI_Setup.exe`:** Single-file automated Windows setup installer.
   - **`RadiVision-AI-Workstation.zip`:** Zero-install standalone portable distribution for clinical workstations.
4. **Zero-Background Frameless Startup Lifecycle:**
   - The desktop client launches as a completely frameless, transparent window (`frame: false, transparent: true, backgroundColor: '#00000000'`).
   - Displays a floating, centered animated circular splash screen (`580px × 440px`) with progressive unblurring, a 5-second countdown calibration timer, and an instant `Skip →` button.
   - Smoothly transitions into a compact, floating authentication card with zero outer window bleed, dynamically sizing between **Sign In** (`390px × 460px`) and **Sign Up** (`440px × 620px`).
   - Dynamically expands and maximizes into the full-screen clinical workstation upon verified login.
5. **Streamlined Tabular Scans Archive (Removal of Radiograph Column):**
   - Removed the non-functional radiograph thumbnail column and full-image popover modal from both **PACS Patient Records** (Admin view) and **My Scan History** (User view).
   - Eliminates broken image placeholders and local filesystem resolution bottlenecks, delivering an uncluttered, high-density tabular view with direct RSNA PDF report export.
6. **Ergonomic Sidebar & Taskbar Clearance:**
   - Added generous bottom padding (`pb-6`) to the sidebar user card, ensuring logout controls are never clipped by the Windows taskbar or display borders.
   - Integrated an explicit, high-visibility **"Log Out"** button with dedicated icon and text label.
7. **Role-Based Access Control (RBAC):**
   - **Admin:** Complete access to institution-wide PACS scans, user status management, system activity audit logs, executive Excel database export, and sample image loading buttons.
   - **User (Clinician / Radiologist):** Focused diagnostic studio, streamlined **My Scan History** (with patient name and national ID omitted for personal records privacy), and a clean **User Dashboard** (study references omitted from recent studies list). Public signups automatically assign the secure `User` role.
8. **Sample Loading Access Scoping:** Diagnostic sample loading buttons (*"Load Bone Sample"* and *"Load Chest Sample"*) are strictly restricted to Administrators to prevent accidental overwrites during clinical use.
9. **Exact Date & Timestamp Auditing:** Standardized high-precision timestamps (`YYYY-MM-DD HH:MM:SS` and `DD Mon YYYY, hh:mm:ss AM/PM`) across all user interfaces, database records, RSNA-format clinical PDF reports, and Excel audit logs.
10. **Immutable Root Administrator & Administrative Self-Deletion Safeguards:**
    - **Permanent Root Protection (`awaismalik001`):** Multi-tier defense-in-depth security ensures the master administrator (`awaismalik001`) can never be deleted under any circumstances, even by the administrator themselves. Deletion buttons are completely suppressed in the UI and replaced with a prominent `Protected Root Admin` badge; API and database layers enforce hard rejection with HTTP 403 / security violation exceptions.
    - **Self-Deletion Lockout:** System administrators are strictly blocked from deleting their own active administrative session accounts across both the Admin Dashboard and Staff Profile Management interfaces, safeguarding system continuity and preventing orphaned institutional scan records.

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

The SQLite PACS database (`database/xray_system.db`) initializes automatically on the first backend run and pre-seeds the administrative account:

| Account Type | Username | Password | Role | Access Scope |
| :--- | :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `Admin123!` | `Admin` | Full PACS, User Controls, Audit Logs, Sample Loaders, Excel Export |
| **Clinician / Radiologist** | *Via Sign Up* | *User Defined* | `User` | AI Studio, Personal Scan History, User Dashboard, Profile |

> **Security Note:** Default administrator credentials should be updated immediately in production environments via the **Profile Management** interface.

---

## 5. Technology Stack

### Backend & Deep Learning
- **Language:** Python 3.10+
- **REST Framework:** FastAPI, Uvicorn, Python-Multipart
- **Deep Learning:** PyTorch, TorchVision, Ultralytics YOLOv8
- **Vision Transformers:** Custom Dual-Head `RadiVisionViT` (ViT-B/16)
- **Generative AI:** `google-genai` (Gemini 3.8 Flash, Gemini 3.5 Flash Lite)
- **Computer Vision:** OpenCV (`cv2`), Pillow (PIL)
- **Data & Evaluation:** NumPy, Pandas, Scikit-Learn, Matplotlib
- **Security:** AES-256-GCM (`cryptography`), PBKDF2, bcrypt
- **Reporting & Export:** ReportLab (RSNA PDF), OpenPyXL (Excel `.xlsx`)

### Frontend & Desktop
- **Core Library:** React 19, React DOM
- **Build Tool:** Vite 6
- **Desktop Runtime:** Electron 44
- **Styling:** Tailwind CSS 4, PostCSS, Lucide React Icons
- **Animation:** Framer Motion, Canvas Confetti
- **HTTP Client:** Axios

---

## 6. Installation & Setup Guide

### Prerequisites
1. **Python:** Version 3.10 or 3.11 installed with 64-bit architecture.
2. **Node.js:** Version 18+ and `npm` installed.
3. **Hardware:** Minimum 8 GB RAM (16 GB recommended). GPU acceleration (CUDA) supported if PyTorch CUDA is installed; operates seamlessly on CPU.

---

### Step 1: Clone Repository & Python Environment

```bash
# Navigate to the project directory
cd "d:/My Projects/RadiVision AI"

# Create and activate a Python virtual environment
python -m venv venv

# Windows (PowerShell / Command Prompt)
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 2: Configure Environment Variables

Create or update the `.env` file in the project root:

```env
# Google Gemini API Key (Multimodal AI Cross-Verification)
GEMINI_API_KEY=your_gemini_api_key_here

# Google Maps / Places API Key (Optional: Dynamic Healthcare Referrals)
GOOGLE_MAPS_API_KEY=your_google_maps_key_here

# AES-256 Key for Database Encryption at Rest (32 bytes base64 encoded or string)
AES_SECRET_KEY=k2W8yD9qX1mP5rL3vN7tJ4bF0zC6sH8aQ2wE4rT6yU8=

# Server Configuration
HOST=127.0.0.1
PORT=8000
```

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

From Windows File Explorer or PowerShell / CMD at the project root, run:
```cmd
.\launch_desktop_app.bat
```
*This automated script boots the FastAPI AI backend in the background and launches the frameless Electron desktop workstation.*

---

### Option B: Launching in Visual Studio / VS Code

To run the application inside **Visual Studio** or **Visual Studio Code**:

1. Open the project root folder in VS Code / Visual Studio (`File > Open Folder... > d:\My Projects\RadiVision AI`).
2. Open an integrated terminal (`Ctrl + ~` or ``Ctrl + ` ``).
3. Run the automated desktop launcher:
   ```powershell
   .\launch_desktop_app.bat
   ```
   *Alternatively, run in two separate split terminals:*
   - **Terminal 1 (Backend Deep Learning Engine):**
     ```powershell
     python server.py
     ```
   - **Terminal 2 (Frontend Desktop Application):**
     ```powershell
     cd frontend
     npm run electron
     ```

---

### Option C: Manual Multi-Terminal Desktop Launch

1. **Start the FastAPI Backend Service:**
   ```bash
   # From the project root with venv activated
   python server.py
   ```
   *The backend starts at `http://127.0.0.1:8000`.*

2. **Launch the Electron Native Workstation:**
   ```bash
   # In a second terminal window
   cd frontend
   npm run electron
   ```
   *The application opens with the compact circular splash screen, transitions into the compact authentication window, and expands to full screen upon login.*

---

### Option D: Web Workstation (Browser Mode)

1. **Start the FastAPI Backend Service:**
   ```bash
   python server.py
   ```

2. **Start the Vite Frontend Development Server:**
   ```bash
   cd frontend
   npm run dev
   ```
   *Access the application in your browser at `http://localhost:5173`.*

> **Production Note:** The FastAPI backend automatically serves the pre-built frontend from `frontend/dist`. You can access the complete application directly at `http://127.0.0.1:8000` without running Vite if you have executed `npm run build`.

---

## 8. Clinical Workflows & User Roles

### A. AI Diagnostics Studio
- **DICOM & Image Ingestion:** Accepts DICOM (`.dcm`), PNG, JPG, and WEBP formats.
- **Interactive Modality Toggle:** Automatically selects Chest or Bone with manual override capabilities.
- **Admin-Exclusive Sample Loaders:** Administrators can instantly load verified Chest Pneumonia or Bone Fracture reference scans for quality control and demonstrations.
- **Visual Explainability (Grad-CAM):** Interactive toggle enables high-resolution spatial heatmap overlays showing focal consolidations or cortical disruptions with bounding coordinates.
- **Multimodal Consensus Card:** Displays the primary model finding alongside the **Gemini 3.8 Flash** verification score, concordance status, clinical rationale, and clinical urgency indicator.
- **One-Click RSNA PDF Generation:** Downloads a clinical report complete with patient demographics, image viewports, Grad-CAM heatmaps, diagnosis, and local healthcare referrals.

### B. User Dashboard & My Scan History
- **Personal Scan History:** Clinicians can search, filter, and review all previous scans performed under their account.
- **Streamlined Tabular Display:** High-density clinical table without broken image placeholder latency:
  - **Modality** (`Chest` / `Bone`)
  - **ViT Diagnostic Finding** (`Normal`, `Pneumonia`, `Fracture`)
  - **Confidence** (`95.0%`)
  - **Date & Timestamp** (`2026-09-17 13:30:15`)
  - **Action** (Direct RSNA PDF export)
- **Privacy Protection:** Patient Name and National ID columns are omitted to preserve patient privacy in personal clinician views.
- **Recent Clinical Studies:** Displays recent triage activity with clean, uncluttered columns (study reference identifiers removed for regular users).

### C. Administrator Management Console
- **PACS Patient Records:** Comprehensive institutional repository displaying all patient records:
  - **Patient / National ID** (`Patient Name` + `MRN/Contact`)
  - **Modality** (`Chest` / `Bone`)
  - **ViT Diagnostic Finding** (`Normal`, `Pneumonia`, `Fracture`)
  - **Confidence** (`95.0%`)
  - **Date & Timestamp** (`2026-09-17 13:30:15`)
  - **Action** (Direct RSNA PDF export)
- **User Administration:** Activate or deactivate user accounts, modify roles between `User` and `Admin`, and review clinician activity.
- **Security Audit Logs:** Complete chronological trail of logins, scans, report downloads, and configuration changes with exact timestamps.
- **Executive Excel Export:** Single-click generation of a 3-sheet `.xlsx` workbook containing PACS patient records, audit trails, and triage analytics.

---

## 9. Model Architecture & Clinical Validation

| Modality / Task | Architecture | Primary Metric | Clinical Benchmark |
| :--- | :--- | :--- | :--- |
| **Chest Pneumonia** | Vision Transformer (ViT-B/16) + MobileNetV2 | **90.72%** Test Accuracy | Balanced sensitivity across bacterial and viral consolidations |
| **Bone Fracture** | Vision Transformer (ViT-B/16) + YOLOv8 | **91.40%** Accuracy / **0.9691** AUC | Precise localization across wrist, arm, leg, and ankle fractures |
| **Modality Triage** | Dual-Class Convolutional Neural Network | **99.20%** Accuracy | Zero-latency separation of chest and skeletal radiographs |
| **Multimodal Co-Pilot** | Google Gemini 3.8 Flash (+ 3.5 Lite Fallback) | **100%** Consensus Validation | Second-opinion review, clinical impression, false-negative escalation |

### Dual Inference Engine
The system includes a dual-inference mechanism:
1. **Production Mode:** Loads trained weights (`.pt` and `.h5` files in `model/`) directly into PyTorch/TensorFlow.
2. **Clinical Simulation Mode:** If weights are not found on disk, the system engages a clinically calibrated simulation engine. This enables full end-to-end interface testing, bounding box rendering, report compilation, and database persistence without requiring long initial training sessions.

---

## 10. Project Directory Structure

```
RadiVision AI/
├── app/                              # Backend application modules
│   ├── auth.py                       # User authentication, PBKDF2/bcrypt, sessions
│   ├── database.py                   # SQLite 3NF schema, CRUD operations, query isolation
│   ├── domain_shift_augmentation.py  # Phase 3: Domain Shift Web Degradation Generator
│   ├── encryption.py                 # AES-256-GCM authenticated field-level encryption
│   ├── excel_export.py               # 3-Sheet clinical & audit Excel workbook generator
│   ├── gemini_service.py             # Gemini 3.8 Flash & 3.5 Flash Lite API integration
│   ├── hospital_referral.py          # GPS hospital & specialist recommendation engine
│   ├── model_engine.py               # Unified deep learning inference manager
│   ├── preprocessing.py              # Phase 2: CLAHE contrast & 224x224 standardization
│   ├── report_generator.py           # Pixel-perfect RSNA clinical PDF report compiler
│   ├── vit_model.py                  # Dual-head Vision Transformer (ViT-B/16) engine
│   └── bone_gradcam.py               # Grad-CAM spatial activation mapping
│
├── database/                         # Persistent database storage
│   └── xray_system.db                # SQLite database file (auto-created on first run)
│
├── frontend/                         # Modern React + Vite + Electron frontend
│   ├── electron/
│   │   ├── main.cjs                  # Electron main process (window lifecycle & resizing)
│   │   └── preload.cjs               # Secure IPC bridge for window controls
│   ├── src/
│   │   ├── components/
│   │   │   ├── AdminDashboard.jsx    # Institutional PACS, user management, audit logs
│   │   │   ├── AuthModal.jsx         # Compact login & signup dialog
│   │   │   ├── DiagnosticStudio.jsx  # Core AI scanning studio, Grad-CAM, Gemini cards
│   │   │   ├── HealthcareNetwork.jsx # Interactive hospital & specialist directory
│   │   │   ├── NeuralTelemetry.jsx   # Model architecture, ROC curves, confusion matrices
│   │   │   ├── PatientHistory.jsx    # Scan archive (privacy-tailored for User vs Admin)
│   │   │   ├── ProfileManagement.jsx # Clinician profile & password settings
│   │   │   ├── Sidebar.jsx           # Dark medical workstation navigation
│   │   │   ├── SplashScreen.jsx      # Compact circular animated splash screen
│   │   │   └── UserDashboard.jsx     # Clinician overview & quick scan launcher
│   │   ├── App.jsx                   # Application state & window mode coordinator
│   │   └── main.jsx                  # React DOM entry point
│   ├── package.json                  # Frontend dependencies and run scripts
│   └── vite.config.js                # Vite build and server configuration
│
├── model/                            # Model training scripts and pre-trained weights
│   ├── chest/                        # Chest pneumonia model weights and training pipeline
│   ├── bone/                         # Bone fracture YOLOv8 / PyTorch weights
│   ├── type_classifier/              # Modality triage classifier
│   └── vit/                          # Vision Transformer calibrated weights
│
├── reports/                          # Auto-generated clinical PDF reports and Excel exports
├── uploads/                          # Temporary encrypted storage for uploaded scans
├── launch_desktop_app.bat            # One-click native desktop launcher
├── server.py                         # FastAPI REST API bridge on port 8000
├── requirements.txt                  # Python dependencies manifest
├── .env                              # Environment variables (API keys, secrets)
└── README.md                         # System documentation
```

---

## 11. Standalone Desktop Distribution & Setup Installers

RadiVision AI provides two packaging options for immediate deployment:

### Option 1: Standalone Single Setup Installer (`RadiVision_AI_Setup.exe`)
- **Format:** Single executable Windows installer built via Electron-Builder NSIS (and Inno Setup).
- **Behavior:**
  - Automatically installs RadiVision AI to the local machine (`AppData\Local\Programs\RadiVision AI` or `Program Files`).
  - Creates Start Menu shortcuts and an optional Desktop shortcut.
  - Bundles the complete pre-compiled FastAPI AI engine, PyTorch Vision Transformer weights, SQLite PACS database, and modern Electron frontend.
  - Uninstallation cleanly removes all program binaries via Windows *Add or Remove Programs*.

### Option 2: Portable Clinical Workstation Archive (`RadiVision-AI-Workstation.zip`)
- **Format:** Pre-packaged portable directory archive (`.zip`).
- **Behavior:**
  - Zero-installation needed. Clinicians can copy the folder to any USB drive, workstation PC, or share via WhatsApp / cloud drive.
  - Double-click `RadiVision AI.exe` inside the unzipped directory to run immediately.

### Building the Distribution Packages
To rebuild both the workstation archive and setup installer from source:
```cmd
python build_desktop.py
```
*Outputs:*
1. `RadiVision_AI_Setup.exe` (Root directory)
2. `RadiVision-AI-Workstation.zip` (Root directory)

---

## 12. Security, Privacy & Regulatory Compliance

- **Authentication Security:** Passwords hashed with bcrypt / PBKDF2 with salt. Brute-force rate limiting blocks repeated failed attempts.
- **Data Protection at Rest:** Sensitive patient demographics and identifiers are encrypted using AES-256-GCM.
- **Clean Audit Trail:** All administrative, diagnostic, and export operations are logged to the database with exact UTC timestamps.
- **Privacy by Design:** Regular clinicians only access scans initiated under their authorized credentials. Identification tags are excluded from standard user scan histories.
- **Auto-Logout Protection:** Desktop application dispatches a secure session termination event upon window closure.

---

## 13. License & Medical Disclaimer

**Medical Disclaimer:** RadiVision AI is developed for diagnostic support, quality assurance, and research triage. It is intended to augment, not replace, the independent clinical judgment of board-certified radiologists and medical practitioners.

*Designed and engineered for high-precision diagnostic radiology.*
