# Intelligent X-Ray Image Analysis & Abnormality Detection System
### A Multi-Modal Deep Learning Desktop Application for Automated Chest (Pneumonia), Bone (Fracture), and Dental (Panoramic) Abnormality Detection

---

**Project Documentation Report**  
**Course:** BS Computer Science | Semester 3 | Artificial Intelligence Project  

| Institutional Details | Specification |
|:---|:---|
| **Student Name** | Muhammad Awais Mahroof |
| **Roll Number** | 014 |
| **Project Supervisor** | Sir Wasim Malik |
| **Department** | Department of Computer Science |
| **Institution** | National Excellence Institute |

---

## Executive Summary

The **Intelligent X-Ray Image Analysis & Abnormality Detection System** is an end-to-end clinical decision-support desktop application designed to triage and analyze three primary diagnostic radiograph modalities:
1. **Chest Radiographs:** Automated classification of **Pneumonia** versus **Normal** pulmonary parenchyma using a fine-tuned MobileNetV2 deep convolutional neural network.
2. **Musculoskeletal (Bone) Radiographs:** Automated spatial localization of **Fractures** with body-region categorization (e.g., wrist, forearm, elbow) using YOLOv8 object detection.
3. **Dental Panoramic Radiographs:** Automated per-tooth localization and pathology classification (caries, deep caries, periapical lesions) utilizing YOLOv8 mapped to the standard **FDI Two-Digit Tooth Numbering System**.

The platform is integrated into a unified desktop application built on **PyQt5**, backed by a local **SQLite** relational database with strict role-based access control (**Admin** vs. **Clinician/User**), encrypted authentication using **bcrypt**, real-time bounding box compositing via **OpenCV**, and automated PDF diagnostic report generation powered by **ReportLab**.

---

## Table of Contents

1. [Abstract](#1-abstract)
2. [Introduction & Problem Formulation](#2-introduction--problem-formulation)
   - 2.1 Problem Statement
   - 2.2 Motivation
   - 2.3 Project Objectives
3. [Project Scope](#3-project-scope)
   - 3.1 In-Scope Capabilities
   - 3.2 Out-of-Scope Capabilities
4. [Related Work & Literature Review](#4-related-work--literature-review)
5. [Dataset Specifications](#5-dataset-specifications)
   - 5.1 Chest Radiography Dataset (Pneumonia)
   - 5.2 Bone Radiography Dataset (Fractures & Trauma)
   - 5.3 Dental Panoramic Radiography Dataset (Pathology & FDI Numbering)
   - 5.4 Modality Classification Dataset (Triage)
6. [Proposed System Architecture](#6-proposed-system-architecture)
   - 6.1 Multi-Stage Pipeline
   - 6.2 Architectural Flowchart
7. [AI Methodology & Technical Design](#7-ai-methodology--technical-design)
   - 7.1 Ingestion & Resolution Invariance
   - 7.2 Chest Classification Model (MobileNetV2 CNN)
   - 7.3 Bone Fracture Detection Model (YOLOv8)
   - 7.4 Dental Pathology Detection Model (YOLOv8 & FDI Notation)
   - 7.5 Modality Auto-Detection Classifier
   - 7.6 Training Configurations & Hyperparameters
8. [Application Modules Breakdown](#8-application-modules-breakdown)
9. [Relational Database Design (SQLite)](#9-relational-database-design-sqlite)
   - 9.1 Entity Relationship Model
   - 9.2 Complete Data Schema & DDL
10. [Tools, Libraries & Technology Stack](#10-tools-libraries--technology-stack)
11. [Project Development Timeline](#11-project-development-timeline)
12. [Expected Outcomes & Key Deliverables](#12-expected-outcomes--key-deliverables)
13. [Future Enhancements](#13-future-enhancements)
14. [Implementation Blueprint & Source Code](#14-implementation-blueprint--source-code)
    - 14.1 Implementation Status
    - 14.2 Environment Configuration
    - 14.3 Source Code: `train_model.py` (Chest Pneumonia)
    - 14.4 Source Code: `predict.py` (Inference Verification)
    - 14.5 Full Dependency Manifest: `requirements.txt`
15. [Phased Build Roadmap](#15-phased-build-roadmap)
16. [GUI Design System & Screen Inventory](#16-gui-design-system--screen-inventory)
    - 16.1 Clinical Color Palette
    - 16.2 UI Layout Paradigms
    - 16.3 Screen Inventory & Access Matrix
17. [User Authentication & Security Protocols](#17-user-authentication--security-protocols)
    - 17.1 User Roles & Permissions
    - 17.2 Security Protocols & Data Safeguards
18. [Project File & Directory Structure](#18-project-file--directory-structure)
19. [Conclusion](#19-conclusion)
20. [References](#20-references)

---

## 1. Abstract

Medical projection radiography remains the foundational, most accessible diagnostic imaging modality in contemporary healthcare. However, the diagnostic throughput of medical centers is severely constrained by a global shortage of certified radiologists, leading to diagnostic backlogs, physician fatigue, and potential delays in critical interventions.

This project delivers the **Intelligent X-Ray Image Analysis & Abnormality Detection System**, an AI-driven desktop application engineered to streamline radiological assessment across three high-volume domains:
- **Pneumonia detection** from chest X-rays.
- **Fracture localization** from skeletal bone X-rays.
- **Dental pathology detection** (caries, lesions) from panoramic dental X-rays.

The core architecture introduces a multi-stage intelligent routing pipeline. When a radiograph of arbitrary resolution is uploaded, an automated 3-class modality classifier identifies the anatomical category with a confidence metric and allows immediate clinician confirmation or override. The radiograph is then routed to dedicated AI models:
- A transfer learning **MobileNetV2** deep convolutional network for chest pneumonia classification.
- A **YOLOv8** object detector trained on the FracAtlas and GRAZPEDWRI-DX datasets for bone fracture localization and body-region tagging.
- A specialized **YOLOv8** model trained on the DENTEX panoramic dataset for tooth enumeration and pathology identification using the FDI numbering standard.

The application is deployed as a standalone desktop executable using **PyQt5**, integrated with a local **SQLite** relational database featuring user data partitioning, salted **bcrypt** password encryption, **OpenCV** bounding box rendering, and automated clinical **ReportLab** PDF report generation.

---

## 2. Introduction & Problem Formulation

### 2.1 Problem Statement
In emergency departments, outpatient clinics, and rural medical centers, general practitioners are routinely required to interpret radiographs under intense time pressures without on-demand access to specialized radiologists. Diagnostic oversight in plain radiography—such as subtle non-displaced fractures, early-stage lobar pneumonia, or occult dental root lesions—can precipitate rapid clinical deterioration and increase morbidity. There is a pressing clinical need for an intelligent decision-support application that acts as an assistive "second pair of eyes", automatically triaging incoming studies, flagging abnormal regions, and compiling standardized diagnostic records.

### 2.2 Motivation
Artificial intelligence, particularly deep learning via Convolutional Neural Networks (CNNs) and single-stage object detectors (YOLO), has achieved diagnostic benchmarks comparable to expert clinicians in controlled medical studies. The motivation of this project is to take these cutting-edge algorithms out of theoretical research environments and package them into a practical, secure, offline-capable desktop application. This project unites essential computer science domains—deep learning, computer vision, relational databases, desktop UI engineering, and cryptography—into a cohesive, production-grade clinical tool.

### 2.3 Project Objectives
The specific, measurable objectives of this project are:
1. **Chest Subsystem:** Design, train, and evaluate a transfer-learning CNN (MobileNetV2) capable of classifying chest radiographs as **Normal** or **Pneumonia** with high sensitivity and specificity.
2. **Bone Subsystem:** Train and deploy a **YOLOv8** object detection model to detect, bound, and classify musculoskeletal fractures while categorizing the anatomical body region.
3. **Dental Subsystem:** Train and deploy a **YOLOv8** object detection model on panoramic dental radiographs to detect dental pathologies (caries, periapical lesions, impactions) indexed by FDI two-digit tooth numbers.
4. **Modality Triaging:** Develop an automated, lightweight 3-class CNN that accurately routes uploaded radiographs to their respective specialized model pipelines.
5. **Desktop User Interface:** Construct a responsive, modern graphical user interface using **PyQt5** styled with a clinical design system.
6. **Relational Data Management & Security:** Implement an ACID-compliant **SQLite** database supporting role-based access control (Admin vs. Clinician), bcrypt password hashing, and user-isolated patient history tracking.
7. **Clinical Report Generation:** Implement an automated module utilizing **ReportLab** to generate exportable, print-ready PDF diagnostic summaries containing patient demographics, high-resolution annotated radiographs, and structured finding tables.

---

## 3. Project Scope

```
+-----------------------------------------------------------------------------------------+
|                                    PROJECT BOUNDARIES                                   |
+----------------------------------------------------+------------------------------------+
|                    IN-SCOPE                        |            OUT-OF-SCOPE            |
+----------------------------------------------------+------------------------------------+
| - Automatic 3-class X-ray modality detection       | - Cloud hosting or web SaaS        |
|   (Chest / Bone / Dental) with manual override     |   deployment (runs fully offline)  |
| - Chest Pneumonia binary classification            | - Multi-class chest differential   |
| - Bone fracture localization with body region tags |   (COVID-19, TB, lung nodules)     |
| - Dental pathology detection with FDI numbering    | - 3D CT, MRI, or ultrasound data   |
| - OpenCV bounding-box & label rendering            | - Full PACS/DICOM network servers  |
| - Local SQLite relational database with CRUD       |   (DIMSE C-STORE / C-MOVE)         |
| - Role-based authentication (Admin & Clinician)    | - Automated drug prescribing or    |
| - Automated clinical PDF report generation         |   therapeutic management           |
| - Input dimension invariance (any image size)      | - Hardware-accelerated embedded    |
| - Bcrypt password security & SQL sanitization      |   microcontroller deployment       |
+----------------------------------------------------+------------------------------------+
```

---

## 4. Related Work & Literature Review

Deep learning in plain radiography has evolved rapidly across three distinct clinical specialties:

### 4.1 Chest Radiography Literature
Rajpurkar et al. (2017) introduced **CheXNet**, a 121-layer DenseNet trained on the NIH ChestX-ray14 dataset (over 100,000 frontal radiographs), demonstrating that deep CNNs could exceed the average diagnostic sensitivity of board-certified radiologists in pneumonia detection. Kermany et al. (2018) established the efficacy of transfer learning using ImageNet-pretrained convolutional backbones (such as Inception and MobileNet) for pediatric pneumonia detection on Kaggle's Guangzhou Women and Children's Medical Center dataset. Their findings demonstrated that fine-tuning pre-trained representations enables high diagnostic accuracy without requiring millions of clinical training samples.

### 4.2 Musculoskeletal Fracture Detection Literature
Rajpurkar et al. (2018) published the **MURA** (Musculoskeletal Radiographs) benchmark, containing 40,561 upper-extremity radiographs across seven anatomical regions (finger, wrist, forearm, elbow, humerus, shoulder, hand). More recently, Kabir et al. (2023) developed **FracAtlas**, a comprehensively annotated multi-region fracture dataset providing exact spatial bounding boxes for fracture classification, localization, and segmentation. Complementing this, Nagy et al. (2022) released the **GRAZPEDWRI-DX** pediatric trauma dataset, demonstrating the effectiveness of one-stage object detectors (YOLO series) in detecting subtle pediatric wrist fractures.

### 4.3 Dental Panoramic Radiography Literature
Panoramic dental radiography involves complex anatomical structures with high visual overlap. The **DENTEX Challenge Consortium** (2023) released a standardized benchmark for tooth enumeration and pathology diagnosis on panoramic radiographs. Utilizing the **FDI (Fédération Dentaire Internationale)** two-digit numbering system, researchers proved that modified YOLOv8 architectures can simultaneously detect individual tooth boundaries and classify pathologies such as dental caries, periapical lesions, and tooth impactions with high spatial precision.

---

## 5. Dataset Specifications

Each of the three diagnostic tasks, plus the modality triaging stage, utilizes a dedicated medical dataset:

```
+--------------------------------------------------------------------------------------------------+
|                                    DATASET SPECIFICATIONS                                        |
+---------------------+-------------------------------+--------------------+-----------------------+
| Modality Task       | Source Dataset                | Volume & Format    | Target Classes        |
+---------------------+-------------------------------+--------------------+-----------------------+
| 1. Chest Pneumonia  | Kaggle Guangzhou Medical      | 5,863 JPEG images  | 2 Classes:            |
|    (Classification) | Center Cohort (Paul Mooney)   | Train/Val/Test split| Normal, Pneumonia     |
+---------------------+-------------------------------+--------------------+-----------------------+
| 2. Bone Fracture    | FracAtlas Dataset +           | 4,000+ Annotated   | Bounding Boxes +      |
|    (Object Detect)  | GRAZPEDWRI-DX Pediatric Wrist | Images (YOLO TXT)  | Fractures, Wrist,     |
|                     | + MURA (Supplementary)        |                    | Forearm, Elbow, Hand  |
+---------------------+-------------------------------+--------------------+-----------------------+
| 3. Dental Pathologies| DENTEX Challenge Panoramic   | 1,500+ High-Res    | Bounding Boxes +      |
|    (Object Detect)  | Dental Radiographs            | Panoramic (YOLO TXT)| FDI Tooth (11-48),    |
|                     |                               |                    | Caries, Periapical    |
+---------------------+-------------------------------+--------------------+-----------------------+
| 4. Modality Triage  | Balanced Stratified Sample    | 4,500 Images       | 3 Classes:            |
|    (Classification) | from Chest, Bone, and Dental  | (1,500 per class)  | Chest, Bone, Dental   |
+---------------------+-------------------------------+--------------------+-----------------------+
```

*Ethical & Academic Note: All datasets are open-access, de-identified public cohorts utilized strictly for academic research and educational development. The resulting models serve as clinical decision support prototypes and do not replace professional medical judgment.*

---

## 6. Proposed System Architecture

The application adopts a modular, sequential pipeline architecture. The complete end-to-end execution flow is detailed below:

```
                  +-----------------------------------+
                  |        Clinician / Admin          |
                  |          Authenticates            |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------------------------+
                  |      User Uploads Radiograph      |
                  |   (Arbitrary Resolution JPG/PNG)  |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------------------------+
                  |   Automated Modality Classifier   |
                  |      (3-Class Lightweight CNN)    |
                  +-----------------+-----------------+
                                    |
                  [Display Detected Modality & Confidence]
                  [Clinician Confirms or Overrides]
                                    |
         +--------------------------+-------------------------+
         |                          |                         |
         v                          v                         v
+------------------+      +-------------------+     +------------------+
|  CHEST PIPELINE  |      |   BONE PIPELINE   |     | DENTAL PIPELINE  |
|  (MobileNetV2)   |      |  (YOLOv8 Network) |     | (YOLOv8 Network) |
| Binary Predict:  |      | Locate Fractures; |     | Locate Lesions;  |
| Normal vs Pneumo |      | Tag Body Region   |     | FDI Tooth Number |
+--------+---------+      +---------+---------+     +--------+---------+
         |                          |                         |
         +--------------------------+-------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |      OpenCV Visual Compositor     |
                  |   Renders Bounding Boxes & Badges |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------------------------+
                  |     SQLite Persistence Layer      |
                  |  Saves Patient, Scan & Findings   |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------------------------+
                  |    ReportLab Document Compiler    |
                  |    Generates Formatted PDF File   |
                  +-----------------------------------+
```

### Table 1: System Pipeline Stage Specifications
| Stage # | Pipeline Component | Functional Description |
|:---|:---|:---|
| **Stage 1** | Image Ingestion | User selects or drags a radiograph (JPG/PNG). File is validated for integrity, format, and dimension safety. |
| **Stage 2** | Image Preprocessing | An in-memory scaled copy is normalized (224×224 for CNNs, 640×640 for YOLOv8). The original image remains pristine. |
| **Stage 3** | Modality Triage | Modality CNN predicts probability distribution across `[Chest, Bone, Dental]`. The UI displays the prediction with a dropdown override. |
| **Stage 4** | Model Dispatcher | Based on confirmed modality, the normalized tensor is routed to the designated inference weights. |
| **Stage 5a** | Chest Inference | CNN outputs pneumonia probability $\hat{y} \in [0.0, 1.0]$. Values $\ge 0.5$ indicate Pneumonia. |
| **Stage 5b** | Bone Inference | YOLOv8 performs non-maximum suppression (NMS), outputting coordinates $[x, y, w, h]$, body region, and fracture confidence. |
| **Stage 5c** | Dental Inference | YOLOv8 outputs per-tooth bounding coordinates, condition label (Caries, Periapical), and FDI tooth number (e.g., #36). |
| **Stage 6** | Visual Compositor | OpenCV draws bounding boxes and badges directly onto a render canvas alongside a tabular findings breakdown. |
| **Stage 7** | Database Engine | Commits the record to SQLite (`patients`, `scans`, and `findings` tables) with the creator's `user_id` foreign key. |
| **Stage 8** | Report Generation | Compiles an exportable clinical PDF summary containing hospital branding, patient details, annotated scans, and findings. |

---

## 7. AI Methodology & Technical Design

### 7.1 Ingestion & Resolution Invariance
Hospital radiographs vary greatly in raw dimensions—from $512 \times 512$ up to $3000 \times 2500$ pixels. A fundamental engineering requirement is dimension invariance:
- **Raw Image Preservation:** The source file is never cropped or destructively downsampled on disk. It is stored directly in `dataset/` or `app/assets/`.
- **In-Memory Transformation:** During inference, images are converted in RAM to model-compatible tensors:
  - For MobileNetV2: $224 \times 224 \times 3$ normalized to $[-1, 1]$ via `mobilenet_v2.preprocess_input`.
  - For YOLOv8: $640 \times 640 \times 3$ normalized to $[0, 1]$ with letterbox aspect ratio padding.
- **GUI & PDF Rendering:** The original image is rendered in the PyQt interface using `QPixmap.scaled(..., Qt.KeepAspectRatio, Qt.SmoothTransformation)` and embedded into PDF reports at full fidelity.

### 7.2 Chest Classification Model (MobileNetV2 Transfer Learning)
For pneumonia classification, MobileNetV2 is selected due to its lightweight inverted residual bottleneck architecture, allowing fast inference on consumer CPUs without dedicated GPUs:
- **Base Architecture:** Pre-trained on ImageNet (1.4M images) as a feature extractor. Base convolutional weights are frozen (`trainable = False`) to prevent gradient destruction.
- **Classification Head:**
  $$\mathbf{x} = \text{GlobalAveragePooling2D}(\mathbf{F}) \in \mathbb{R}^{1280}$$
  $$\mathbf{h} = \text{ReLU}(\mathbf{W}_1 \mathbf{x} + \mathbf{b}_1), \quad \mathbf{W}_1 \in \mathbb{R}^{128 \times 1280}$$
  $$\mathbf{h}_{\text{drop}} = \text{Dropout}(0.3)(\mathbf{h})$$
  $$\hat{y} = \sigma(\mathbf{w}_2^T \mathbf{h}_{\text{drop}} + b_2), \quad \hat{y} \in [0, 1]$$
- **Loss Function:** Binary Cross-Entropy with Adam optimization:
  $$\mathcal{L}_{BCE} = -\frac{1}{N} \sum_{i=1}^N \left[ y_i \log(\hat{y}_i) + (1 - y_i) \log(1 - \hat{y}_i) \right]$$

### 7.3 Bone Fracture Detection Model (YOLOv8)
Bone fracture diagnosis requires spatial bounding rather than global classification:
- **Architecture:** Ultralytics YOLOv8 nano/small (`yolov8n.pt` / `yolov8s.pt`), featuring an anchor-free split head that computes classification and regression independently.
- **Bounding Box Parameterization:** Bounding boxes are parameterized as normalized four-element vectors:
  $$\mathbf{b} = \left( \frac{x_{\text{center}}}{W}, \frac{y_{\text{center}}}{H}, \frac{w}{W}, \frac{h}{H} \right), \quad \mathbf{b} \in [0, 1]^4$$
- **Multi-Task Objective:** Combines Task-Aligned Focal Loss (classification) with Complete IoU (CIoU) and Distribution Focal Loss (bounding box localization).
- **Target Classes:** `[Fracture, Wrist, Forearm, Elbow, Hand, Humerus, Shoulder]`.

### 7.4 Dental Pathology Detection Model (YOLOv8 & FDI Notation)
- **Panoramic Mapping:** Panoramic dental radiographs display an entire mandible and maxilla. The model is trained on the DENTEX dataset.
- **FDI Two-Digit Numbering Standard:** 
  - Quadrant 1: Upper Right (Teeth 11–18)
  - Quadrant 2: Upper Left (Teeth 21–28)
  - Quadrant 3: Lower Left (Teeth 31–38)
  - Quadrant 4: Lower Right (Teeth 41–48)
- **Target Pathologies:** `[Healthy, Caries, Deep Caries, Periapical Lesion, Impacted Tooth]`.
- **Inference Output:** Bounding boxes pinpointing affected teeth with the exact FDI identifier (e.g., *"Tooth #36: Deep Caries (Confidence: 89%)"*).

### 7.5 Modality Auto-Detection Classifier
A 3-class convolutional network trained on a balanced composite dataset (1,500 images per category: Chest, Bone, Dental):
- **Softmax Probability:**
  $$P(\text{Class} = k \mid \mathbf{x}) = \frac{e^{z_k}}{\sum_{j=1}^3 e^{z_j}}, \quad k \in \{\text{Chest, Bone, Dental}\}$$
- **Override Safeguard:** If prediction confidence is $< 75\%$, the UI highlights an amber warning prompting the clinician to confirm the modality.

### Table 2: Model Training Hyperparameters Summary
| Hyperparameter | Chest Classifier (MobileNetV2) | Bone Detector (YOLOv8) | Dental Detector (YOLOv8) | Modality Classifier (CNN) |
|:---|:---|:---|:---|:---|
| **Base Architecture** | MobileNetV2 (ImageNet) | YOLOv8n (COCO pre-trained) | YOLOv8s (COCO pre-trained) | Custom 4-block ConvNet |
| **Input Dimensions** | $224 \times 224 \times 3$ | $640 \times 640 \times 3$ | $640 \times 640 \times 3$ | $224 \times 224 \times 3$ |
| **Loss Formulation** | Binary Cross-Entropy | CIoU + DFL + Focal Loss | CIoU + DFL + Focal Loss | Categorical Cross-Entropy |
| **Optimizer** | Adam ($\text{lr} = 10^{-4}$) | AdamW ($\text{lr} = 10^{-3}$) | AdamW ($\text{lr} = 10^{-3}$) | Adam ($\text{lr} = 10^{-4}$) |
| **Batch Size** | 16 (Local CPU) / 32 (GPU) | 16 | 16 | 32 |
| **Epoch Budget** | 10–20 (Early stopping) | 50 | 50 | 15 |
| **Export Format** | `chest_xray_model.h5` | `bone_fracture_model.pt` | `dental_xray_model.pt` | `xray_type_classifier.h5` |

---

## 8. Application Modules Breakdown

### Table 3: Core Application Modules
| Module Code | File Name | Functional Responsibilities |
|:---|:---|:---|
| **MOD-01** | `login_window.py` | Clinician/Admin authentication interface with animated toggle to user registration. |
| **MOD-02** | `signup_window.py` | Account creation dialog with input format validation and bcrypt password hashing. |
| **MOD-03** | `main_window.py` | Shell window managing the top header, navigation sidebar, and dynamic `QStackedWidget` views. |
| **MOD-04** | `new_scan_page.py` | Primary workflow view: file browsing, drag-and-drop, modality auto-detect, inference execution, and result display. |
| **MOD-05** | `patient_history_page.py` | Relational table viewer with search filtering; restricts regular clinicians to their own scans while permitting Admins full visibility. |
| **MOD-06** | `manage_users_page.py` | Admin-only interface for reviewing user accounts, modifying role privileges, and toggling active status. |
| **MOD-07** | `activity_log_page.py` | Admin-only chronological audit log of all system events (logins, uploads, predictions, PDF exports). |
| **MOD-08** | `model_engine.py` | Singleton inference manager that loads model weights once and executes predictions thread-safely. |
| **MOD-09** | `detection_overlay.py` | OpenCV drawing engine that renders anti-aliased bounding boxes, confidence tags, and color-coded labels. |
| **MOD-10** | `database.py` | Thread-safe SQLite abstraction layer managing connections, schema creation, and parameterized queries. |
| **MOD-11** | `report_generator.py` | Document compiler using ReportLab to generate standardized clinical diagnostic PDF reports. |
| **MOD-12** | `theme.py` | Centralized styling stylesheet containing color tokens, typography scales, and QSS style sheets. |

---

## 9. Relational Database Design (SQLite)

The application utilizes an embedded, zero-configuration SQLite relational database (`database/xray_system.db`). The schema is strictly normalized to Third Normal Form (3NF) and includes a `user_id` foreign key on the `scans` table to enforce data isolation between users.

### 9.1 Entity Relationship Diagram

```
+--------------------+              +--------------------+
|       users        |              |      patients      |
+--------------------+              +--------------------+
| user_id (PK)       |              | patient_id (PK)    |
| full_name          |              | name               |
| username (UQ)      |              | age                |
| email (UQ)         |              | gender             |
| password_hash      |              | contact            |
| role (Admin/User)  |              | created_at         |
| is_active          |              +---------+----------+
| created_at         |                        |
+---------+----------+                        |
          |                                   |
          | 1                                 | 1
          |                                   |
          | N                                 | N
+---------v-----------------------------------v----------+
|                         scans                          |
+--------------------------------------------------------+
| scan_id (PK)                                           |
| patient_id (FK -> patients.patient_id)                 |
| user_id (FK -> users.user_id)                          | <-- [Multi-User Isolation]
| scan_type (Chest / Bone / Dental)                      |
| body_region (Wrist, Forearm, etc. - Nullable)          |
| prediction (Primary Diagnostic Finding)                |
| confidence (REAL 0.0 - 1.0)                            |
| raw_image_path (TEXT)                                  |
| annotated_image_path (TEXT)                            |
| scan_date (DATETIME)                                   |
+---------------------------+----------------------------+
                            | 1
                            |
                            | N
+---------------------------v----------------------------+
|                       findings                         |
+--------------------------------------------------------+
| finding_id (PK)                                        |
| scan_id (FK -> scans.scan_id)                          |
| label (Fracture, Deep Caries, Pneumonia)               |
| tooth_number (FDI code: e.g., '36' - Nullable)         |
| confidence (REAL 0.0 - 1.0)                            |
| bbox_x, bbox_y, bbox_w, bbox_h (Normalized REAL)       |
+--------------------------------------------------------+
```

### Table 4: Database Data Schema & Data Dictionary
| Table Name | Column | Data Type | Modifiers / Constraints | Description |
|:---|:---|:---|:---|:---|
| `users` | `user_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique system user ID |
| | `full_name` | TEXT | NOT NULL | User's complete legal name |
| | `username` | TEXT | UNIQUE, NOT NULL | Unique login handle |
| | `email` | TEXT | UNIQUE, NOT NULL | Contact email address |
| | `password_hash` | TEXT | NOT NULL | Salted bcrypt password hash |
| | `role` | TEXT | CHECK(`role` IN ('Admin','User')) | Access privilege role |
| | `is_active` | INTEGER | DEFAULT 1 | Active account status flag |
| | `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| `patients` | `patient_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique patient ID |
| | `name` | TEXT | NOT NULL | Patient's full name |
| | `age` | INTEGER | NOT NULL | Patient's age in years |
| | `gender` | TEXT | CHECK(`gender` IN ('Male','Female','Other')) | Patient's gender |
| | `contact` | TEXT | DEFAULT NULL | Phone or contact info |
| | `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Registration timestamp |
| `scans` | `scan_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique scan record ID |
| | `patient_id` | INTEGER | NOT NULL, REFERENCES `patients` | Associated patient foreign key |
| | `user_id` | INTEGER | NOT NULL, REFERENCES `users` | Submitting clinician foreign key |
| | `scan_type` | TEXT | CHECK(`scan_type` IN ('Chest','Bone','Dental')) | Modality category |
| | `body_region` | TEXT | DEFAULT NULL | Populated for bone scans |
| | `prediction` | TEXT | NOT NULL | Summary diagnostic label |
| | `confidence` | REAL | NOT NULL | Top-level confidence score |
| | `raw_image_path` | TEXT | NOT NULL | Storage path to original X-ray |
| | `annotated_image_path` | TEXT | DEFAULT NULL | Storage path to annotated X-ray |
| | `scan_date` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Date and time scan was processed |
| `findings` | `finding_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique finding record ID |
| | `scan_id` | INTEGER | NOT NULL, REFERENCES `scans` | Associated scan foreign key |
| | `label` | TEXT | NOT NULL | Specific finding label |
| | `tooth_number` | TEXT | DEFAULT NULL | FDI identifier for dental scans |
| | `confidence` | REAL | NOT NULL | Detection confidence score |
| | `bbox_x`, `bbox_y`| REAL | DEFAULT NULL | Normalized upper-left coordinates |
| | `bbox_w`, `bbox_h`| REAL | DEFAULT NULL | Normalized width and height |

---

## 10. Tools, Libraries & Technology Stack

### Table 5: Production Technology Stack
| Layer | Library / Tool | Minimum Version | Engineering Purpose |
|:---|:---|:---|:---|
| **Language** | Python | 3.10 / 3.11 | Core runtime environment |
| **Deep Learning (CNN)** | TensorFlow / Keras | $\ge 2.15.0$ | Training and executing MobileNetV2 chest and modality classifiers |
| **Object Detection (YOLO)**| Ultralytics YOLOv8 | $\ge 8.1.0$ | Real-time object detection for bone fractures and dental pathologies |
| **Computer Vision** | OpenCV (`opencv-python`) | $\ge 4.8.0$ | Reading images, bounding-box compositing, image format conversions |
| **Image Handling** | Pillow (PIL) | $\ge 10.0.0$ | Image loading, high-fidelity rescaling, aspect ratio management |
| **GUI Framework** | PyQt5 / PySide6 | $\ge 5.15.10$ | Desktop user interface, window management, event handling |
| **Relational Database** | SQLite (`sqlite3`) | 3.x (Standard) | Serverless relational data store with foreign key enforcement |
| **Security & Hashing** | `bcrypt` | $\ge 4.1.2$ | Adaptive, salted cryptographic password hashing |
| **Document Compilation** | ReportLab | $\ge 4.0.9$ | Dynamic generation of PDF clinical reports |
| **Numerical Processing** | NumPy & Pandas | Latest stable | Tensor transformations and tabular data formatting |
| **Evaluation Metrics** | Scikit-learn | $\ge 1.3.0$ | Performance evaluation (ROC curves, confusion matrices, F1 scores) |

---

## 11. Project Development Timeline

### Table 6: 8-Week Development Roadmap
| Week | Milestone / Phase | Planned Activities |
|:---|:---|:---|
| **Week 1** | Requirements & Data Acquisition | Setup project folders, obtain Kaggle, FracAtlas, and DENTEX datasets, configure dependencies |
| **Week 2** | Data Preprocessing & Augmentation | Implement data augmentation, organize train/val/test splits, assemble 3-class modality dataset |
| **Week 3** | Chest CNN & Modality Training | Train MobileNetV2 pneumonia classifier, train modality classifier, evaluate and export `.h5` weights |
| **Week 4** | Bone & Dental YOLOv8 Training | Format YOLO annotations, fine-tune YOLOv8 models for bone fractures and dental caries, export `.pt` weights |
| **Week 5** | PyQt Desktop GUI Foundations | Build `MainWindow`, navigation sidebar, `LoginWindow`, `SignUpWindow`, and visual styles in `theme.py` |
| **Week 6** | Database Integration & Security | Initialize SQLite schema, implement `database.py` and `auth.py`, wire role-based access control |
| **Week 7** | Inference Engine & Report Generation | Build `model_engine.py`, OpenCV overlay rendering, and PDF report compilation via `report_generator.py` |
| **Week 8** | System Integration & Testing | End-to-end multi-modal testing, edge-case validation, performance tuning, and final documentation |

---

## 12. Expected Outcomes & Key Deliverables

- **Fully Functional Desktop Application:** A desktop GUI built with PyQt allowing clinicians to log in, upload radiographs, and review findings.
- **Accurate Modality Triage:** An automated classifier that correctly identifies Chest, Bone, and Dental radiographs with $> 95\%$ accuracy.
- **Reliable Pneumonia Detection:** A chest CNN model that provides high sensitivity and specificity in screening for pneumonia.
- **Spatial Abnormality Detection:** Two YOLOv8 models that localize fractures and dental pathologies with clear visual bounding boxes and confidence scores.
- **Robust Multi-User Security:** Complete separation between Admin and User roles, with salted password hashing and private patient records.
- **Professional Clinical Reports:** Automated, print-ready PDF reports compiling patient demographics, scan findings, and annotated images.

---

## 13. Future Enhancements

The following extensions are planned for post-academic and clinical iterations:
1. **Multi-Class Pulmonary Screening:** Expand the chest CNN to detect tuberculosis (TB), COVID-19, pleural effusion, and atelectasis.
2. **DICOM / PACS Protocol Support:** Add native support for hospital DICOM (`.dcm`) formats and direct integration with PACS servers via `pynetdicom`.
3. **Explainable AI (Grad-CAM):** Add gradient-weighted class activation mapping (Grad-CAM) to generate heatmaps illustrating model attention on chest X-rays.
4. **Database Encryption At Rest:** Integrate **SQLCipher** for 256-bit AES encryption of the local SQLite database.
5. **Tele-Radiology Synchronization:** Add optional secure cloud synchronization for multi-clinic data replication and remote second opinions.

---

## 14. Implementation Blueprint & Source Code

### Table 7: Implementation Progress Tracking
| Subsystem Component | Current Status | Description of Completed Artifacts |
|:---|:---|:---|
| **Chest Dataset & Scripts** | Completed | Kaggle dataset configured; `train_model.py` and `predict.py` implemented |
| **Chest Model Training** | Ready for execution | Produces `model/chest/chest_xray_model.h5` |
| **Modality Classifier** | Fully designed | Dataset generation protocol and CNN architecture ready for training |
| **Bone Fracture YOLOv8** | Fully designed | YOLO configuration and dataset mapping prepared |
| **Dental Lesion YOLOv8** | Fully designed | DENTEX FDI numbering taxonomy and dataset mappings established |
| **Authentication & Database**| Fully designed | SQLite 3NF schema and bcrypt hashing model completed |
| **GUI & Visual Theme** | Fully designed | Color palette, screen inventory, and layout patterns established |
| **Desktop Application Code**| Scheduled for Phase 1–5| Application modules to be developed in structured phases |

---

### 14.1 Environment Configuration Guide

```bash
# 1. Create and activate a Python virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows PowerShell / Command Prompt

# 2. Upgrade package manager and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Organize dataset directories
# Ensure dataset/chest_xray contains train/, val/, and test/ subdirectories
# with NORMAL/ and PNEUMONIA/ class folders.

# 4. Train the chest classifier
cd model/chest
python train_model.py

# 5. Verify inference on a sample image
python predict.py path/to/sample_xray.jpg
```

---

### 14.2 Source Code: `train_model.py` (Chest Classifier)

```python
"""
train_model.py
----------------
Trains a binary chest X-ray classifier (Normal vs. Pneumonia) using transfer 
learning with MobileNetV2. Designed to run efficiently on CPU or GPU environments.

Directory Structure Expected:
    dataset/chest_xray/
        train/
            NORMAL/
            PNEUMONIA/
        val/
            NORMAL/
            PNEUMONIA/
        test/
            NORMAL/
            PNEUMONIA/
"""

import os
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# ----------------- Configuration -----------------
DATASET_DIR = os.path.join("..", "..", "dataset", "chest_xray")
TRAIN_DIR = os.path.join(DATASET_DIR, "train")
VAL_DIR = os.path.join(DATASET_DIR, "val")
TEST_DIR = os.path.join(DATASET_DIR, "test")

IMG_SIZE = (224, 224)
BATCH_SIZE = 16  # Optimized for CPU RAM stability
EPOCHS = 10      # Can be increased for GPU training
MODEL_OUT = "chest_xray_model.h5"

# ----------------- Data Augmentation & Generators -----------------
train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=15,
    zoom_range=0.15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
)

val_test_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

train_gen = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=True,
)

val_gen = val_test_datagen.flow_from_directory(
    VAL_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=False,
)

test_gen = val_test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=False,
)

print(f"Class Mapping: {train_gen.class_indices}")

# ----------------- Model Architecture -----------------
base_model = MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet",
)
base_model.trainable = False  # Freeze pre-trained weights

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation="relu")(x)
x = Dropout(0.3)(x)
output = Dense(1, activation="sigmoid")(x)

model = Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer=Adam(learning_rate=1e-4),
    loss="binary_crossentropy",
    metrics=["accuracy"],
)

model.summary()

# ----------------- Training Callbacks -----------------
callbacks = [
    EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True),
    ModelCheckpoint(MODEL_OUT, monitor="val_accuracy", save_best_only=True, verbose=1),
]

# ----------------- Model Training -----------------
history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS,
    callbacks=callbacks,
)

# ----------------- Evaluation -----------------
test_loss, test_acc = model.evaluate(test_gen)
print(f"\nFinal Test Accuracy: {test_acc * 100:.2f}%")
print(f"Final Test Loss: {test_loss:.4f}")

# Save final weights
model.save(MODEL_OUT)
print(f"Model successfully saved to: {MODEL_OUT}")
```

---

### 14.3 Source Code: `predict.py` (Inference Verification)

```python
"""
predict.py
-----------
Loads the trained chest X-ray model and performs standalone inference on a 
single image of arbitrary resolution.
"""

import sys
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

MODEL_PATH = "chest_xray_model.h5"
IMG_SIZE = (224, 224)
CLASS_LABELS = {0: "NORMAL", 1: "PNEUMONIA (Abnormal)"}

def predict_xray(image_path: str):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file '{MODEL_PATH}' not found. Please train the model first.")
    
    # Load model
    model = load_model(MODEL_PATH)
    
    # Load image and resize in memory
    img = image.load_img(image_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    
    # Run prediction
    raw_pred = model.predict(img_array, verbose=0)[0][0]
    predicted_class = int(raw_pred >= 0.5)
    confidence = raw_pred if predicted_class == 1 else (1.0 - raw_pred)
    label = CLASS_LABELS[predicted_class]
    
    print("=" * 45)
    print(f"Image Path : {image_path}")
    print(f"Diagnosis  : {label}")
    print(f"Confidence : {confidence * 100:.2f}%")
    print("=" * 45)
    
    return label, float(confidence)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict.py <path_to_xray_image.jpg>")
        sys.exit(1)
    predict_xray(sys.argv[1])
```

---

### 14.4 Complete Dependency Manifest: `requirements.txt`

```text
# Deep Learning Frameworks
tensorflow>=2.15.0
ultralytics>=8.1.0

# Scientific & Numerical Computing
numpy>=1.24.3
pandas>=2.0.3
scikit-learn>=1.3.0
matplotlib>=3.7.2

# Image Processing & Computer Vision
opencv-python>=4.8.0.76
Pillow>=10.0.0

# Desktop User Interface
PyQt5>=5.15.10

# Security & Authentication
bcrypt>=4.1.2

# Clinical PDF Report Generation
reportlab>=4.0.9
```

---

## 15. Phased Build Roadmap

Development is organized into five sequential phases to ensure smooth integration:

```
[Phase 1: Foundations]
 - Train chest pneumonia classifier (chest_xray_model.h5)
 - Implement database.py (SQLite schema) & auth.py (bcrypt authentication)
 - Build basic PyQt login and user registration windows
        |
        v
[Phase 2: Modality Triaging]
 - Create composite training dataset for Chest, Bone, and Dental X-rays
 - Train and export xray_type_classifier.h5
 - Implement NewScanPage with auto-detection and manual dropdown override
        |
        v
[Phase 3: Musculoskeletal Fracture Detection]
 - Prepare FracAtlas YOLO annotations and bone_dataset.yaml
 - Train YOLOv8 fracture detection model (bone_fracture_model.pt)
 - Implement detection_overlay.py using OpenCV bounding boxes
        |
        v
[Phase 4: Panoramic Dental Diagnostics]
 - Prepare DENTEX panoramic dataset annotations (FDI numbering mapping)
 - Train YOLOv8 dental model (dental_xray_model.pt)
 - Integrate FDI tooth findings table into the UI
        |
        v
[Phase 5: Administration & Clinical Reports]
 - Implement report_generator.py using ReportLab for PDF export
 - Build Admin-only views (Manage Users and Activity Log)
 - Perform end-to-end system testing across all three modalities
```

---

## 16. GUI Design System & Screen Inventory

### Table 8: Clinical Color Palette
| Token Name | Hex Code | Purpose in UI |
|:---|:---|:---|
| **Primary Navy** | `#0B3D66` | Navigation sidebar, primary headers, main action buttons |
| **Secondary Blue** | `#14507D` | Section headers, table borders, selected tabs |
| **Background Light** | `#F4F6F8` | Main application background and view panels |
| **Card Surface** | `#FFFFFF` | Input forms, patient tables, image viewports |
| **Status: Normal** | `#639922` | Badges and indicators for "Normal" results |
| **Status: Abnormal** | `#E24B4A` | Badges and alerts for fractures, pneumonia, and caries |
| **Status: Inconclusive**| `#BA7517` | Warning badges for low-confidence detections ($< 70\%$) |
| **Text Primary** | `#1A202C` | Headings, labels, and primary body typography |
| **Text Muted** | `#718096` | Subtitles, input placeholders, and metadata captions |

### 16.1 UI Layout Patterns
- **Header Bar:** Shows hospital branding, the active view title, database connection status, and logged-in user profile details.
- **Collapsible Sidebar:** Provides quick navigation between views. Options shown dynamically adjust based on user role (Admin vs. Clinician).
- **Card-Based Containers:** Views use rounded white cards (`border-radius: 8px`) on a light gray background for a clean, professional aesthetic.
- **Color-Coded Status Badges:** Diagnostic results are clearly flagged using Green (Normal), Red (Abnormal), or Amber (Low Confidence).

### Table 9: Screen Inventory & Access Matrix
| Screen Name | File Name | Role: User | Role: Admin | Functional Description |
|:---|:---|:---:|:---:|:---|
| **Login** | `login_window.py` | Full | Full | Authenticate existing credentials |
| **Sign Up** | `signup_window.py` | Full | Full | Register new user account (defaults to User role) |
| **Dashboard** | `main_window.py` | Metrics | All Stats | Overview of scan activity, statistics, and shortcuts |
| **New Scan** | `new_scan_page.py` | Full | Full | Upload radiographs, auto-detect modality, run inference |
| **My Records** | `patient_history_page.py` | Own Scans | All Scans | Searchable table of past patient examinations |
| **Manage Users** | `manage_users_page.py` | *No Access* | Full | Admin panel to add, edit, or deactivate user accounts |
| **Activity Log** | `activity_log_page.py` | *No Access* | Full | Chronological audit log of user logins, scans, and exports |
| **Report Viewer**| `report_generator.py` | Full | Full | Preview, print, or export clinical PDF reports |

---

## 17. User Authentication & Security Protocols

### Table 10: Role-Based Access Control (RBAC) Matrix
| Feature / Action | Clinician / User | System Administrator |
|:---|:---:|:---:|
| Upload radiographs and execute AI inference | Yes | Yes |
| Create patient records and save scans | Yes | Yes |
| View own uploaded scan history | Yes | Yes |
| View hospital-wide scan history across all users | No | Yes |
| Export and print diagnostic PDF reports | Yes | Yes |
| Modify or delete existing patient records | No | Yes |
| Manage user accounts and assign roles | No | Yes |
| View system security and activity audit logs | No | Yes |

### 17.1 Security Protocols
- **Cryptographic Hashing:** Passwords are never stored in plain text. Passwords are salted and hashed using `bcrypt` (work factor 12) before being saved.
- **Parameterized SQL:** All database queries use parameterized placeholders (`?`) to completely eliminate SQL injection vulnerabilities.
- **Input Validation:** User inputs (names, emails, usernames) are validated using strict regular expressions.
- **Anti-Enumeration Login:** Login failures return a generic error (*"Invalid username or password"*) to prevent account enumeration.
- **Local Data Storage:** Patient data and radiographs remain stored locally on the host machine, eliminating network transmission vulnerabilities.

---

## 18. Project File & Directory Structure

```
xray_ai_project/
|
|-- dataset/
|   |-- chest_xray/
|   |   |-- train/ (NORMAL/, PNEUMONIA/)
|   |   |-- val/   (NORMAL/, PNEUMONIA/)
|   |   `-- test/  (NORMAL/, PNEUMONIA/)
|   |-- bone_xray/
|   |   |-- images/ (train/, val/)
|   |   `-- labels/ (YOLO TXT format)
|   |-- dental_xray/
|   |   |-- images/ (train/, val/)
|   |   `-- labels/ (YOLO TXT format with FDI classes)
|   `-- xray_type/
|       |-- chest/
|       |-- bone/
|       `-- dental/
|
|-- model/
|   |-- type_classifier/
|   |   |-- train_type_classifier.py
|   |   `-- xray_type_classifier.h5
|   |-- chest/
|   |   |-- train_model.py
|   |   |-- predict.py
|   |   `-- chest_xray_model.h5
|   |-- bone/
|   |   |-- train_bone_yolo.py
|   |   |-- bone_dataset.yaml
|   |   `-- bone_fracture_model.pt
|   `-- dental/
|       |-- train_dental_yolo.py
|       |-- dental_dataset.yaml
|       `-- dental_xray_model.pt
|
|-- app/
|   |-- main.py                     # Application entry point
|   |-- login_window.py             # Login UI and controller
|   |-- signup_window.py            # User registration UI and controller
|   |-- auth.py                     # Bcrypt authentication and session handling
|   |-- main_window.py              # Sidebar navigation and page container
|   |-- new_scan_page.py            # Upload canvas and inference viewer
|   |-- patient_history_page.py     # Searchable patient history table
|   |-- manage_users_page.py        # Admin user management view
|   |-- activity_log_page.py        # Admin audit activity feed
|   |-- model_engine.py             # Model loading and inference controller
|   |-- detection_overlay.py        # OpenCV bounding box and label rendering
|   |-- database.py                 # SQLite relational CRUD operations
|   |-- report_generator.py         # ReportLab PDF report generation
|   |-- theme.py                    # Global styles and color constants
|   `-- assets/
|       |-- icons/                  # Interface icons
|       `-- logo.png                # Hospital branding logo
|
|-- database/
|   `-- xray_system.db              # Local SQLite database file
|
|-- reports/                        # Saved PDF diagnostic reports
|-- logs/
|   `-- app.log                     # Diagnostic and error activity logs
|
|-- requirements.txt                # Unified dependency manifest
`-- README.md                       # Project documentation and setup guide
```

### Table 11: Directory Roles and Responsibilities
| Directory | Primary Function |
|:---|:---|
| `dataset/` | Contains training, validation, and testing images across all modalities (used only during model training). |
| `model/` | Stores training scripts, YAML configs, and exported model weights (`.h5`, `.pt`). |
| `app/` | Main application source code containing UI views, business logic, and database operations. |
| `database/` | Contains the persistent SQLite database file `xray_system.db`. |
| `reports/` | Local directory where generated patient PDF reports are automatically saved. |
| `logs/` | Houses local application and security audit log files. |

---

## 19. Conclusion

The **Intelligent X-Ray Image Analysis & Abnormality Detection System** represents a comprehensive, multi-modal artificial intelligence solution for clinical plain radiography. By unifying three diverse diagnostic domains—**Chest Pneumonia Classification**, **Bone Fracture Localization**, and **Dental Panoramic Abnormality Detection**—under an automated modality triaging system, the application delivers a versatile assistive diagnostic platform.

Built with **PyQt5**, **SQLite**, and **ReportLab**, the system ensures patient confidentiality through fully offline local execution. The technical foundation laid out in this document provides a complete, cohesive blueprint ready for the upcoming application code implementation phase.

---

## 20. References

1. **Mooney, P.** (2018). *Chest X-Ray Images (Pneumonia)*. Kaggle Datasets. Guangzhou Women and Children’s Medical Center.
2. **Rajpurkar, P., Irvin, J., Zhu, K., et al.** (2017). *CheXNet: Radiologist-Level Pneumonia Detection on Chest X-Rays with Deep Learning*. arXiv preprint arXiv:1711.05225.
3. **Rajpurkar, P., et al.** (2018). *MURA: Large Dataset for Abnormality Detection in Musculoskeletal Radiographs*. Stanford Machine Learning Group.
4. **Kabir, H., et al.** (2023). *FracAtlas: A Dataset for Fracture Classification, Localization, and Segmentation of Musculoskeletal Radiographs*. Scientific Data, 10(1), 812.
5. **Nagy, E., et al.** (2022). *GRAZPEDWRI-DX: A Clinical Dataset of Pediatric Wrist Trauma Radiographs with Bounding Box Annotations*. Scientific Data, 9(1), 548.
6. **DENTEX Challenge Consortium.** (2023). *Dental Enumeration and Diagnosis on Panoramic X-rays Dataset*. IEEE International Symposium on Biomedical Imaging (ISBI).
7. **Jocher, G., Chaurasia, A., & Qiu, J.** (2023). *Ultralytics YOLOv8 Architecture and Documentation*. Ultralytics.
8. **Sandler, M., Howard, A., Zhu, M., et al.** (2018). *MobileNetV2: Inverted Residuals and Linear Bottlenecks*. IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 4510–4520.
9. **Riverbank Computing.** (2023). *PyQt5 Reference Guide and API Documentation*.
10. **ReportLab Europe Ltd.** (2023). *ReportLab PDF Generation User Guide*.

---
*End of Finalized Documentation Report*
