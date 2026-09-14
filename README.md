# Intelligent X-Ray Image Analysis & Abnormality Detection System

### A Multi-Modal Deep Learning Desktop Application for Automated Chest (Pneumonia), Bone (Fracture), and Dental (Panoramic) Abnormality Detection

**System Information**
- **Application:** RadiVision AI
- **Framework:** Desktop GUI (PyQt5)
- **Deep Learning:** PyTorch, TorchVision, Ultralytics YOLOv8
- **Database:** SQLite (3NF Normalized, Role-Based Access)

---

## 1. Overview
The **Intelligent X-Ray Image Analysis & Abnormality Detection System** is a medical decision-support desktop application designed to screen and triage three primary plain radiograph modalities:
1. **Chest X-Rays:** Detection and binary classification of **Pneumonia** vs. **Normal** using MobileNetV2 transfer learning.
2. **Bone X-Rays:** Object detection and localization of **Fractures** with body-region categorization using YOLOv8.
3. **Dental Panoramic X-Rays:** Object detection and localization of **Dental Pathologies** (caries, deep caries, periapical lesions) mapped to the **FDI Two-Digit Tooth Numbering System** (11–48) using YOLOv8.
4. **Modality Triage:** An automated 3-class CNN that classifies incoming scans as Chest, Bone, or Dental with real-time clinician confirmation or manual override.

---

## 2. Default Administrator Credentials
The SQLite database automatically initializes on first launch and seeds an administrator account:
- **Username:** `admin`
- **Password:** `Admin123!`
- **Role:** `Admin`

*Clinicians and technicians can also register their own accounts via the **Sign Up** interface.*

---

## 3. Installation & Environment Setup

### Prerequisites
- Python 3.10 or 3.11 installed
- Windows / Linux / macOS

### Quick Start
```bash
# 1. Clone or navigate to the project directory
cd "d:/My Projects/RadiVision AI"

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows Command Prompt / PowerShell

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Launch the Desktop Application
python app/main.py
```

---

## 4. AI Model Architecture & Dual Inference Mode
The application implements a robust **Dual Inference Mode**:
- **Real Weights Inference:** If pre-trained model files (`.h5` and `.pt`) are present in the `model/` folders, the engine loads them directly into memory for deep learning prediction.
- **Intelligent Simulation Mode:** If weights have not yet been trained on disk, the application automatically engages a smart clinical simulation mode. This allows examiners, supervisors, and students to thoroughly test the full desktop interface, bounding box rendering, database persistence, and PDF report compilation immediately without waiting for long dataset downloads and multi-hour GPU training sessions.

---

## 5. Model Training Pipelines

### A. Chest Pneumonia Model (MobileNetV2)
```bash
cd model/chest
python train_model.py
# Exports: model/chest/chest_xray_model.h5
```

### B. Bone Fracture Model (YOLOv8)
```bash
cd model/bone
python train_bone_yolo.py
# Exports: model/bone/bone_fracture_model.pt
```

### C. Dental Abnormality Model (YOLOv8 & FDI)
```bash
cd model/dental
python train_dental_yolo.py
# Exports: model/dental/dental_xray_model.pt
```

### D. Modality Classifier (3-Class CNN)
```bash
cd model/type_classifier
python train_type_classifier.py
# Exports: model/type_classifier/xray_type_classifier.h5
```

---

## 6. Directory Structure
```
xray_ai_project/
├── app/                  # Desktop application source code (PyQt5, DB, Auth, Engine)
├── database/             # Persistent SQLite database (xray_system.db)
├── dataset/              # Training datasets for Chest, Bone, Dental, and Modality
├── logs/                 # System and audit event logs (app.log)
├── model/                # Training scripts and exported weights (.h5, .pt)
├── reports/              # Auto-generated clinical PDF reports
├── requirements.txt      # Dependency manifest
└── README.md             # Project documentation
```
