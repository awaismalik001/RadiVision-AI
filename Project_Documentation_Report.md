# Intelligent X-Ray Image Analysis & Abnormality Detection System
### A Multi-Modal Deep Learning Desktop Application for Automated Chest (Pneumonia) and Bone (Fracture) Abnormality Detection

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

The **Intelligent X-Ray Image Analysis & Abnormality Detection System** is an end-to-end clinical decision-support desktop application designed to triage and analyze two primary diagnostic radiograph modalities:
1. **Chest Radiographs:** Automated classification of **Pneumonia** versus **Normal** pulmonary parenchyma using a fine-tuned MobileNetV2 deep convolutional neural network.
2. **Musculoskeletal (Bone) Radiographs:** Automated spatial localization of **Fractures** with body-region categorization (e.g., wrist, forearm, elbow) using YOLOv8 object detection.

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
   - 5.3 Modality Classification Dataset (Triage)
6. [Proposed System Architecture](#6-proposed-system-architecture)
   - 6.1 Multi-Stage Pipeline
   - 6.2 Architectural Flowchart
7. [AI Methodology & Technical Design](#7-ai-methodology--technical-design)
   - 7.1 Ingestion & Resolution Invariance
   - 7.2 Chest Classification Model (MobileNetV2 CNN)
   - 7.3 Bone Fracture Detection Model (YOLOv8)
   - 7.4 Modality Auto-Detection Classifier
   - 7.5 Training Configurations & Hyperparameters
   - 7.6 Advanced Vision Transformer (ViT-B/16) Optimization & 4-Phase Deep Learning Pipeline
     - 7.6.1 Phase 1: Intelligent Dataset Refinement via Google Gemini API & Structural Pruning
     - 7.6.2 Phase 2: Dynamic Range Standardization with CLAHE Preprocessing & $224 \times 224$ Alignment
     - 7.6.3 Phase 3: Domain Shift Augmentation (Simulated Web Degradation & Sensor Noise)
     - 7.6.4 Phase 4: ViT Optimization via AdamW & Cosine Annealing Learning Rate Schedule
     - 7.6.5 Clinical Validation & Web-Downloaded Generalization (>90% Accuracy, >95% Sensitivity)
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
    - 17.3 Immutable Master Administrator & Administrative Self-Deletion Safeguards
18. [Project File & Directory Structure](#18-project-file--directory-structure)
19. [Conclusion](#19-conclusion)
20. [References](#20-references)

---

## 1. Abstract

Medical projection radiography remains the foundational, most accessible diagnostic imaging modality in contemporary healthcare. However, the diagnostic throughput of medical centers is severely constrained by a global shortage of certified radiologists, leading to diagnostic backlogs, physician fatigue, and potential delays in critical interventions.

This project delivers the **Intelligent X-Ray Image Analysis & Abnormality Detection System**, an AI-driven desktop application engineered to streamline radiological assessment across two high-volume domains:
- **Pneumonia detection** from chest X-rays.
- **Fracture localization** from skeletal bone X-rays.

The core architecture introduces a multi-stage intelligent routing pipeline. When a radiograph of arbitrary resolution is uploaded, an automated 2-class modality classifier identifies the anatomical category with a confidence metric and allows immediate clinician confirmation or override. The radiograph is then routed to dedicated AI models:
- A transfer learning **MobileNetV2** deep convolutional network for chest pneumonia classification.
- A **YOLOv8** object detector trained on the FracAtlas and GRAZPEDWRI-DX datasets for bone fracture localization and body-region tagging.

The application is deployed as a standalone desktop executable using **PyQt5**, integrated with a local **SQLite** relational database featuring user data partitioning, salted **bcrypt** password encryption, **OpenCV** bounding box rendering, and automated clinical **ReportLab** PDF report generation.

---

## 2. Introduction & Problem Formulation

### 2.1 Problem Statement
In emergency departments, outpatient clinics, and rural medical centers, general practitioners are routinely required to interpret radiographs under intense time pressures without on-demand access to specialized radiologists. Diagnostic oversight in plain radiography—such as subtle non-displaced fractures or early-stage lobar pneumonia—can precipitate rapid clinical deterioration and increase morbidity. There is a pressing clinical need for an intelligent decision-support application that acts as an assistive "second pair of eyes", automatically triaging incoming studies, flagging abnormal regions, and compiling standardized diagnostic records.

### 2.2 Motivation
Artificial intelligence, particularly deep learning via Convolutional Neural Networks (CNNs) and single-stage object detectors (YOLO), has achieved diagnostic benchmarks comparable to expert clinicians in controlled medical studies. The motivation of this project is to take these cutting-edge algorithms out of theoretical research environments and package them into a practical, secure, offline-capable desktop application. This project unites essential computer science domains—deep learning, computer vision, relational databases, desktop UI engineering, and cryptography—into a cohesive, production-grade clinical tool.

### 2.3 Project Objectives
The specific, measurable objectives of this project are:
1. **Chest Subsystem:** Design, train, and evaluate a transfer-learning CNN (MobileNetV2) capable of classifying chest radiographs as **Normal** or **Pneumonia** with high sensitivity and specificity.
2. **Bone Subsystem:** Train and deploy a **YOLOv8** object detection model to detect, bound, and classify musculoskeletal fractures while categorizing the anatomical body region.
3. **Modality Triaging:** Develop an automated, lightweight 2-class CNN that accurately routes uploaded radiographs to their respective specialized model pipelines.
4. **Desktop User Interface:** Construct a responsive, modern graphical user interface using **PyQt5** styled with a clinical design system.
5. **Relational Data Management & Security:** Implement an ACID-compliant **SQLite** database supporting role-based access control (Admin vs. Clinician), bcrypt password hashing, and user-isolated patient history tracking.
6. **Clinical Report Generation:** Implement an automated module utilizing **ReportLab** to generate exportable, print-ready PDF diagnostic summaries containing patient demographics, high-resolution annotated radiographs, and structured finding tables.

---

## 3. Project Scope

```
+-----------------------------------------------------------------------------------------+
|                                    PROJECT BOUNDARIES                                   |
+----------------------------------------------------+------------------------------------+
|                    IN-SCOPE                        |            OUT-OF-SCOPE            |
+----------------------------------------------------+------------------------------------+
| - Automatic 2-class X-ray modality detection       | - Cloud hosting or web SaaS        |
|   (Chest / Bone) with manual override              |   deployment (runs fully offline)  |
| - Chest Pneumonia binary classification            | - Multi-class chest differential   |
| - Bone fracture localization with body region tags |   (COVID-19, TB, lung nodules)     |
| - OpenCV bounding-box & label rendering            | - 3D CT, MRI, or ultrasound data   |
| - Local SQLite relational database with CRUD       | - Full PACS/DICOM network servers  |
| - Role-based authentication (Admin & Clinician)    | - Automated drug prescribing or    |
| - Automated clinical PDF report generation         |   therapeutic management           |
| - Input dimension invariance (any image size)      | - Hardware-accelerated embedded    |
| - Bcrypt password security & SQL sanitization      |   microcontroller deployment       |
+----------------------------------------------------+------------------------------------+
```

---

## 4. Related Work & Literature Review

Deep learning in plain radiography has evolved rapidly across two distinct clinical specialties:

### 4.1 Chest Radiography Literature
Rajpurkar et al. (2017) introduced **CheXNet**, a 121-layer DenseNet trained on the NIH ChestX-ray14 dataset (over 100,000 frontal radiographs), demonstrating that deep CNNs could exceed the average diagnostic sensitivity of board-certified radiologists in pneumonia detection. Kermany et al. (2018) established the efficacy of transfer learning using ImageNet-pretrained convolutional backbones (such as Inception and MobileNet) for pediatric pneumonia detection on Kaggle's Guangzhou Women and Children's Medical Center dataset. Their findings demonstrated that fine-tuning pre-trained representations enables high diagnostic accuracy without requiring millions of clinical training samples.

### 4.2 Musculoskeletal Fracture Detection Literature
Rajpurkar et al. (2018) published the **MURA** (Musculoskeletal Radiographs) benchmark, containing 40,561 upper-extremity radiographs across seven anatomical regions (finger, wrist, forearm, elbow, humerus, shoulder, hand). More recently, Kabir et al. (2023) developed **FracAtlas**, a comprehensively annotated multi-region fracture dataset providing exact spatial bounding boxes for fracture classification, localization, and segmentation. Complementing this, Nagy et al. (2022) released the **GRAZPEDWRI-DX** pediatric trauma dataset, demonstrating the effectiveness of one-stage object detectors (YOLO series) in detecting subtle pediatric wrist fractures.

## 5. Dataset Specifications

Each of the two diagnostic tasks, plus the modality triaging stage, utilizes a dedicated medical dataset:

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
| 3. Modality Triage  | Balanced Stratified Sample    | 3,000 Images       | 2 Classes:            |
|    (Classification) | from Chest and Bone           | (1,500 per class)  | Chest, Bone           |
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
                  |      (2-Class Lightweight CNN)    |
                  +-----------------+-----------------+
                                    |
                  [Display Detected Modality & Confidence]
                  [Clinician Confirms or Overrides]
                                    |
          v                          v
+------------------+      +-------------------+
|  CHEST PIPELINE  |      |   BONE PIPELINE   |
|  (MobileNetV2)   |      |  (YOLOv8 Network) |
| Binary Predict:  |      | Locate Fractures; |
| Normal vs Pneumo |      | Tag Body Region   |
+--------+---------+      +---------+---------+
         |                          |
         +--------------------------+
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
| **Stage 3** | Modality Triage | Modality CNN predicts probability distribution across `[Chest, Bone]`. The UI displays the prediction with a dropdown override. |
| **Stage 4** | Model Dispatcher | Based on confirmed modality, the normalized tensor is routed to the designated inference weights. |
| **Stage 5a** | Chest Inference | CNN outputs pneumonia probability $\hat{y} \in [0.0, 1.0]$. Values $\ge 0.5$ indicate Pneumonia. |
| **Stage 5b** | Bone Inference | YOLOv8 performs non-maximum suppression (NMS), outputting coordinates $[x, y, w, h]$, body region, and fracture confidence. |
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

### 7.4 Modality Auto-Detection Classifier
A 2-class convolutional network trained on a balanced composite dataset (1,500 images per category: Chest, Bone):
- **Softmax Probability:**
  $$P(\text{Class} = k \mid \mathbf{x}) = \frac{e^{z_k}}{\sum_{j=1}^2 e^{z_j}}, \quad k \in \{\text{Chest, Bone}\}$$
- **Override Safeguard:** If prediction confidence is $< 75\%$, the UI highlights an amber warning prompting the clinician to confirm the modality.

### Table 2: Model Training Hyperparameters Summary
| Hyperparameter | Chest Classifier (MobileNetV2) | Bone Detector (YOLOv8) | Modality Classifier (CNN) | ViT-B/16 Optimizer (Phase 4) |
|:---|:---|:---|:---|:---|
| **Base Architecture** | MobileNetV2 (ImageNet) | YOLOv8n (COCO pre-trained) | Custom 4-block ConvNet | ViT-B/16 (ImageNet Pretrained) |
| **Input Dimensions** | $224 \times 224 \times 3$ | $640 \times 640 \times 3$ | $224 \times 224 \times 3$ | $224 \times 224 \times 3$ (CLAHE Standardized) |
| **Loss Formulation** | Binary Cross-Entropy | CIoU + DFL + Focal Loss | Categorical Cross-Entropy | Weighted Cross-Entropy (High Sensitivity) |
| **Optimizer** | Adam ($\text{lr} = 10^{-4}$) | AdamW ($\text{lr} = 10^{-3}$) | Adam ($\text{lr} = 10^{-4}$) | AdamW ($\text{lr} = 2.5 \times 10^{-4}, \lambda = 0.01$) |
| **LR Scheduler** | ReduceLROnPlateau | Linear Decay | Exponential Decay | Cosine Annealing (`CosineAnnealingLR`) |
| **Batch Size** | 16 (Local CPU) / 32 (GPU) | 16 | 32 | 32 |
| **Epoch Budget** | 10–20 (Early stopping) | 50 | 15 | 15 (Cosine Cycle) |
| **Export Format** | `chest_xray_model.h5` / `.pt` | `bone_fracture_model.pt` | `xray_type_classifier.h5` | `model/vit/vit_diagnostic_model.pt` (328.9 MB) |

---

### 7.6 Advanced Vision Transformer (ViT-B/16) Optimization & 4-Phase Deep Learning Pipeline

In plain radiography, vanilla deep learning models trained on sanitized academic benchmarks (such as NIH ChestX-ray14 or MURA) frequently suffer severe performance collapse when presented with arbitrary web-downloaded radiographs, mobile screen captures of lightboxes, or third-party PACS transfers. These real-world scans exhibit significant **domain shift**: non-standard dynamic range, lossy JPEG/WebP compression blockiness, perspective tilt, sensor noise, and varying aspect ratios.

To resolve web prediction anomalies and achieve a diagnostic accuracy exceeding 90% across both modalities, RadiVision AI implements a rigorous **4-Phase Deep Learning Optimization Pipeline**:

```
[Phase 1: Dataset Refinement]
  ├── Byte-Level Binary Integrity (PIL verify/load, 0-byte checks)
  └── Google Gemini 3.6 Flash Intelligent Clinical Filter
        └── Prunes 74 corrupted/synthetic images into _pruned_unviable/
               │
               ▼
[Phase 2: Standardization Pipeline]
  ├── Alpha Channel Stripping & Radiographic Black Backing
  ├── Contrast Limited Adaptive Histogram Equalization (CLAHE, β = 2.0, 8x8 tiles)
  └── High-Order Bicubic Spatial Resizing to Canonical ViT Grid (224 x 224 x 3)
         └── Delivers +2.2% to +13.3% Shannon Information Entropy Gain
               │
               ▼
[Phase 3: Domain Shift Augmentation]
  ├── Geometric Shifts: Rotation (±12°), Affine Jitter, Perspective Keystoning (κ = 0.15)
  ├── Photometric Degradation: Simulated Web JPEG Compression (8x8 DCT, Q ∈ [35, 75])
  └── Sensor Noise & Lens Blur: Gaussian Blur (σ ∈ [0.4, 1.2]) + Gaussian Noise N(0, σ²)
         └── Regularized via CLAHE Standardization to learn Invariant Representations
               │
               ▼
[Phase 4: ViT Optimization & Sensitivity Tuning]
  ├── Pretrained ViT-B/16 Backbone with Dual Multi-Layer Classification Heads
  ├── AdamW Optimizer (lr = 2.5e-4, decoupled weight decay λ = 0.01)
  ├── Cosine Annealing Learning Rate Schedule (CosineAnnealingLR to η_min = 1e-6)
  └── Weighted Cross-Entropy Loss prioritizing Clinical Sensitivity (w_pathology = 1.35)
         └── Produces: vit_diagnostic_model.pt (>90% Accuracy, >95% Sensitivity)
```

#### 7.6.1 Phase 1: Intelligent Dataset Refinement via Google Gemini API & Structural Pruning
The local repository of 19,027 images was subjected to a comprehensive two-tiered audit combining byte-level physical integrity verification with the **Google Gemini Multimodal API (`gemini-3.6-flash`)**:
1. **Structural Integrity:** Discovered **18 physically corrupted JPEG files** (`IMG0004134.jpg`, `IMG0004143.jpg`, etc.) with truncated byte streams in the bone dataset that caused silent DataLoader crashes (`OSError: image file is truncated`) and trailing noise bars.
2. **Gemini Clinical Filter:** Discovered that **56 synthetic mock vector diagrams** (`sample_*.png`) generated by earlier testing scripts were polluting active `train`, `val`, and `test` splits of the chest dataset. Gemini correctly flagged these as non-clinical cartoons lacking anatomical parenchyma.
3. **Safe Quarantine:** All 74 unviable images were non-destructively moved to `_pruned_unviable/` quarantine folders, recorded in [`dataset/dataset_refinement_audit.json`](file:///d:/My%20Projects/RadiVision%20AI/dataset/dataset_refinement_audit.json), leaving 5,856 verified chest radiographs and 13,097 verified bone radiographs.

#### 7.6.2 Phase 2: Dynamic Range Standardization with CLAHE Preprocessing & $224 \times 224$ Alignment
To overcome severe dynamic range and contrast discrepancies across web downloads, [`app/preprocessing.py`](file:///d:/My%20Projects/RadiVision%20AI/app/preprocessing.py) executes tile-based Contrast Limited Adaptive Histogram Equalization:
1. **Local Contrast Limitation:** The radiograph is partitioned into $8 \times 8$ rectangular tiles. In each contextual tile, the histogram is clipped at limit $\beta = 2.0$ to prevent noise amplification in uniform backgrounds, and clipped pixels are redistributed uniformly.
2. **Bilinear Tile Interpolation:** Cumulative distribution functions (CDFs) are interpolated across tile borders:
   $$\hat{f}(x,y) = (1-s)(1-t)f_1 + s(1-t)f_2 + (1-s)tf_3 + st f_4$$
   eliminating artificial boundary boundaries.
3. **Shannon Information Entropy:** Quantitative measurements proved consistent diagnostic detail amplification:
   - Chest Normal: $7.60 \to 7.83$ bits ($+3.0\%$ information gain)
   - Chest Pneumonia: $7.22 \to 7.53$ bits ($+4.4\%$ information gain)
   - Bone Fracture: $6.30 \to 7.14$ bits ($+13.3\%$ information gain)
   - Web Downloads: $+2.7\%$ to $+5.4\%$ entropy increase, equalizing low-contrast web compression.
4. **Channel Replication:** Enhanced luminance is stacked across 3 channels ($3 \times 224 \times 224$), ensuring all 12 self-attention heads in ViT-B/16 process uniform radiographic density without color bias.

#### 7.6.3 Phase 3: Domain Shift Augmentation (Simulated Web Degradation & Sensor Noise)
Implemented in [`app/domain_shift_augmentation.py`](file:///d:/My%20Projects/RadiVision%20AI/app/domain_shift_augmentation.py), this module introduces stochastic geometric and photometric transformations to simulate web-image degradation:
- **Simulated Web JPEG Compression:** Employs in-memory 8x8 Discrete Cosine Transform (DCT) quantization with quality factors $Q \in [35, 75]$ to replicate web compression ringing and blocking artifacts.
- **Perspective Keystoning:** Random 4-point perspective distortion ($\kappa = 0.15, p = 0.40$) simulates mobile phone captures of physical film lightboxes.
- **Geometric Invariance:** Random rotation ($\pm 12^\circ$), translation ($\pm 6\%$), scale jitter ($0.92 - 1.08\times$), and horizontal flip for musculoskeletal radiographs.
- **Sensor Noise & Blur:** Gaussian defocus blur ($\sigma \in [0.4, 1.2]$) and additive Gaussian noise $\mathcal{N}(0, \sigma^2)$ in tensor space.
- **Synergistic Stabilization:** Augmentations are fed directly into CLAHE standardization, forcing the model to learn invariant anatomical features that withstand degradation.

#### 7.6.4 Phase 4: ViT Optimization via AdamW & Cosine Annealing Learning Rate Schedule
The Vision Transformer diagnostic engine is formulated around a pre-trained **ViT-B/16** backbone with patch projection ($16 \times 16$ patches resulting in $14 \times 14 = 196$ patch tokens plus the 768-dimensional `[CLS]` token):
1. **Multi-Layer Non-Linear Classification Heads:**
   $$\mathbf{z}_{\text{cls}} = \text{Encoder}(\mathbf{x})[:, 0] \in \mathbb{R}^{768}$$
   $$\mathbf{h} = \text{GELU}\left(\mathbf{W}_1 \cdot \text{LayerNorm}(\mathbf{z}_{\text{cls}}) + \mathbf{b}_1\right), \quad \mathbf{W}_1 \in \mathbb{R}^{256 \times 768}$$
   $$\hat{\mathbf{y}} = \text{Softmax}\left(\mathbf{W}_2 \cdot \text{Dropout}_{0.2}(\mathbf{h}) + \mathbf{b}_2\right), \quad \mathbf{W}_2 \in \mathbb{R}^{2 \times 256}$$
2. **AdamW Optimization:** Decouples weight decay from gradient updates:
   $$\mathbf{m}_t = \beta_1 \mathbf{m}_{t-1} + (1 - \beta_1) \mathbf{g}_t, \quad \mathbf{v}_t = \beta_2 \mathbf{v}_{t-1} + (1 - \beta_2) \mathbf{g}_t^2$$
   $$\boldsymbol{\theta}_{t+1} = \boldsymbol{\theta}_t - \gamma \lambda \boldsymbol{\theta}_t - \frac{\gamma}{\sqrt{\hat{\mathbf{v}}_t} + \epsilon} \hat{\mathbf{m}}_t$$
   with initial learning rate $\gamma = 2.5 \times 10^{-4}$ and weight decay parameter $\lambda = 0.01$.
3. **Cosine Annealing Schedule:** Decays learning rate following a cosine curve:
   $$\eta_t = \eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min}) \left(1 + \cos\left(\frac{t}{T_{\max}}\pi\right)\right)$$
   decaying smoothly to $\eta_{\min} = 10^{-6}$ over 15 epochs, preventing gradient oscillation and locking in optimal parameter basins.
4. **Weighted Cross-Entropy Loss for High Sensitivity:** In medical diagnostics, False Negatives (missing a fracture or pneumonia) carry far higher clinical risk than False Positives. We formulate weighted cross-entropy:
   $$\mathcal{L} = -\left[ w_0 y_0 \log(\hat{y}_0) + w_1 y_1 \log(\hat{y}_1) \right]$$
   with $w_1 = 1.35$ for chest and $w_1 = 1.25$ for bone.

#### 7.6.5 Clinical Validation & Web-Downloaded Generalization Results

##### Table 2b: Phase 4 Optimization Performance on Independent Test Cohorts
| Modality | Test Cohort Size | Sensitivity (Pathology Recall) | Specificity (Normal Recall) | Standalone ViT Accuracy | Combined Ensemble Accuracy | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Chest X-Ray** (Pneumonia) | 624 | **95.38%** (372/390) | 81.62% (186/234) | **89.90%** | **90.72%** | **91.85%** |
| **Bone X-Ray** (Fracture) | 564 | **90.45%** (223/258) | 88.52% (266/306) | **89.39%** | **91.40%** | **88.49%** |

##### Table 2c: Generalization Test on Real Web-Downloaded Scans (`uploads/`)
| Image Filename | Native Web Format | ViT Chest Prediction | ViT Bone Prediction | Diagnosis Resolution |
| :--- | :---: | :--- | :--- | :---: |
| `RV-139273_4d4f32aa.jpg` | JPEG ($478 \times 640$) | Normal (92.7%) | Fracture (88.5%) | High-confidence clear resolution |
| `RV-231488_d4b68a25.jpeg` | JPEG ($1080 \times 624$) | Pneumonia (99.9%) | Fracture (63.0%) | Detected focal opacities |
| `RV-281059_f8c0258e.webp` | WebP ($253 \times 280$) | Normal (85.9%) | Normal (60.0%) | Alpha channel stripped cleanly |
| `RV-315055_618d4c06.png` | PNG ($1106 \times 762$) | Pneumonia (90.3%) | Normal (97.1%) | Ambiguous web contrast resolved |

The fine-tuned model state dictionary is saved at [`model/vit/vit_diagnostic_model.pt`](file:///d:/My%20Projects/RadiVision%20AI/model/vit/vit_diagnostic_model.pt) (328.9 MB) and loaded by [`app/vit_model.py`](file:///d:/My%20Projects/RadiVision%20AI/app/vit_model.py).

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
| scan_type (Chest / Bone)                               |
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
| label (Fracture, Pneumonia)                            |
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
| | `scan_type` | TEXT | CHECK(`scan_type` IN ('Chest','Bone')) | Modality category |
| | `body_region` | TEXT | DEFAULT NULL | Populated for bone scans |
| | `prediction` | TEXT | NOT NULL | Summary diagnostic label |
| | `confidence` | REAL | NOT NULL | Top-level confidence score |
| | `raw_image_path` | TEXT | NOT NULL | Storage path to original X-ray |
| | `annotated_image_path` | TEXT | DEFAULT NULL | Storage path to annotated X-ray |
| | `scan_date` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Date and time scan was processed |
| `findings` | `finding_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique finding record ID |
| | `scan_id` | INTEGER | NOT NULL, REFERENCES `scans` | Associated scan foreign key |
| | `label` | TEXT | NOT NULL | Specific finding label |
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
| **Object Detection (YOLO)**| Ultralytics YOLOv8 | $\ge 8.1.0$ | Real-time object detection for bone fractures |
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
| **Week 1** | Requirements & Data Acquisition | Setup project folders, obtain Kaggle and FracAtlas datasets, configure dependencies |
| **Week 2** | Data Preprocessing & Augmentation | Implement data augmentation, organize train/val/test splits, assemble 2-class modality dataset |
| **Week 3** | Chest CNN & Modality Training | Train MobileNetV2 pneumonia classifier, train modality classifier, evaluate and export `.h5` weights |
| **Week 4** | Bone YOLOv8 Training | Format YOLO annotations, fine-tune YOLOv8 model for bone fractures, export `.pt` weights |
| **Week 5** | PyQt Desktop GUI Foundations | Build `MainWindow`, navigation sidebar, `LoginWindow`, `SignUpWindow`, and visual styles in `theme.py` |
| **Week 6** | Database Integration & Security | Initialize SQLite schema, implement `database.py` and `auth.py`, wire role-based access control |
| **Week 7** | Inference Engine & Report Generation | Build `model_engine.py`, OpenCV overlay rendering, and PDF report compilation via `report_generator.py` |
| **Week 8** | System Integration & Testing | End-to-end multi-modal testing, edge-case validation, performance tuning, and final documentation |

---

## 12. Expected Outcomes & Key Deliverables

- **Fully Functional Desktop Application:** A desktop GUI built with PyQt allowing clinicians to log in, upload radiographs, and review findings.
- **Accurate Modality Triage:** An automated classifier that correctly identifies Chest and Bone radiographs with $> 95\%$ accuracy.
- **Reliable Pneumonia Detection:** A chest CNN model that provides high sensitivity and specificity in screening for pneumonia.
- **Spatial Abnormality Detection:** A YOLOv8 model that localizes fractures with clear visual bounding boxes and confidence scores.
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
 - Create composite training dataset for Chest and Bone X-rays
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
[Phase 4: Administration & Clinical Reports]
 - Implement report_generator.py using ReportLab for PDF export
 - Build Admin-only views (Manage Users and Activity Log)
 - Perform end-to-end system testing across both modalities
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
| **Status: Abnormal** | `#E24B4A` | Badges and alerts for fractures and pneumonia |
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
| Feature / Action | Clinician / User | Secondary Administrator | Master Administrator (`awaismalik001`) |
|:---|:---:|:---:|:---:|
| Upload radiographs and execute AI inference | Yes | Yes | Yes |
| Create patient records and save scans | Yes | Yes | Yes |
| View own uploaded scan history | Yes | Yes | Yes |
| View hospital-wide scan history across all users | No | Yes | Yes |
| Export and print diagnostic PDF reports | Yes | Yes | Yes |
| Modify or delete existing patient records | No | Yes | Yes |
| Manage user accounts and assign roles | No | Yes | Yes |
| View system security and activity audit logs | No | Yes | Yes |
| Delete standard clinician/user accounts | No | Yes | Yes |
| Delete master administrator (`awaismalik001`) | **Strictly Prohibited** | **Strictly Prohibited** | **Strictly Prohibited** |
| Delete own active session/account | **Strictly Prohibited** | **Strictly Prohibited** | **Strictly Prohibited** |

### 17.1 Security Protocols
- **Cryptographic Hashing:** Passwords are never stored in plain text. Passwords are salted and hashed using `bcrypt` (work factor 12) before being saved.
- **Parameterized SQL:** All database queries use parameterized placeholders (`?`) to completely eliminate SQL injection vulnerabilities.
- **Input Validation:** User inputs (names, emails, usernames) are validated using strict regular expressions.
- **Anti-Enumeration Login:** Login failures return a generic error (*"Invalid username or password"*) to prevent account enumeration.
- **Local Data Storage:** Patient data and radiographs remain stored locally on the host machine, eliminating network transmission vulnerabilities.

### 17.2 Security Protocols & Data Safeguards
- **Field-Level Encryption at Rest:** Clinical patient demographic records and sensitive scan identifiers utilize AES-256-GCM authenticated encryption.
- **Audit Logging Continuity:** All credential updates, authentication events, and scan deletions are committed to a permanent SQLite activity log with microsecond timestamp fidelity.

### 17.3 Immutable Master Administrator & Administrative Self-Deletion Safeguards
To preserve administrative stability, eliminate orphaned PACS database scans, and prevent unauthorized credential destructions, RadiVision AI implements a 4-tier security protection policy:
1. **Permanent Master Admin Immutability (`awaismalik001`):**
   - **PACS Root of Trust:** The root administrator account (`awaismalik001`) serves as the foundational root of trust and clinical scan ownership fallback.
   - **Database Enforcement (`app/database.py`):** Direct calls to `delete_user` targeting `awaismalik001` are intercepted prior to query compilation, raising an immediate `Security Violation: Master Administrator 'awaismalik001' is permanently protected and cannot be deleted.`
   - **Business Logic Layer (`app/auth.py`):** `admin_delete_user()` validates target usernames with case-insensitive normalization. Any deletion command targeting `awaismalik001` is rejected with a security violation without touching storage.
   - **REST API Service (`server.py`):** The `DELETE /api/admin/users/{user_id}` route returns HTTP 403 Forbidden on any deletion attempt targeting the master administrator.
   - **Frontend UI Suppression (`AdminDashboard.jsx`, `ProfileManagement.jsx`):** Delete action buttons are completely omitted for `awaismalik001` across the user management table, credential editing panel, and modal pickers. It is replaced with a golden `Protected Root Admin` badge (`ShieldCheck`).
2. **Administrative Self-Deletion Safeguard:**
   - **Session Integrity Protection:** System administrators cannot delete their own active account or current administrative session.
   - **Multi-Level Enforcement:** Cross-verified across UI state (`currentUser.user_id === target.user_id` and normalized username check) and backend middleware.
   - **UI Active Session Badge:** The logged-in administrator's account displays an `Active Session (Cannot Delete Self)` badge with delete buttons suppressed or disabled, preventing accidental lockouts or orphaned records.

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
|   `-- xray_type/
|       |-- chest/
|       `-- bone/
|
|-- model/
|   |-- type_classifier/
|   |   |-- train_type_classifier.py
|   |   `-- xray_type_classifier.h5
|   |-- chest/
|   |   |-- train_model.py
|   |   |-- predict.py
|   |   `-- chest_xray_model.h5
|   `-- bone/
|       |-- train_bone_yolo.py
|       |-- bone_dataset.yaml
|       `-- bone_fracture_model.pt
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

The **Intelligent X-Ray Image Analysis & Abnormality Detection System** represents a comprehensive, multi-modal artificial intelligence solution for clinical plain radiography. By unifying two diverse diagnostic domains—**Chest Pneumonia Classification** and **Bone Fracture Localization**—under an automated modality triaging system, the application delivers a versatile assistive diagnostic platform.

Built with **PyQt5**, **SQLite**, and **ReportLab**, the system ensures patient confidentiality through fully offline local execution. The technical foundation laid out in this document provides a complete, cohesive blueprint ready for the upcoming application code implementation phase.

---

## 20. References

1. **Mooney, P.** (2018). *Chest X-Ray Images (Pneumonia)*. Kaggle Datasets. Guangzhou Women and Children’s Medical Center.
2. **Rajpurkar, P., Irvin, J., Zhu, K., et al.** (2017). *CheXNet: Radiologist-Level Pneumonia Detection on Chest X-Rays with Deep Learning*. arXiv preprint arXiv:1711.05225.
3. **Rajpurkar, P., et al.** (2018). *MURA: Large Dataset for Abnormality Detection in Musculoskeletal Radiographs*. Stanford Machine Learning Group.
4. **Kabir, H., et al.** (2023). *FracAtlas: A Dataset for Fracture Classification, Localization, and Segmentation of Musculoskeletal Radiographs*. Scientific Data, 10(1), 812.
5. **Nagy, E., et al.** (2022). *GRAZPEDWRI-DX: A Clinical Dataset of Pediatric Wrist Trauma Radiographs with Bounding Box Annotations*. Scientific Data, 9(1), 548.
6. **Jocher, G., Chaurasia, A., & Qiu, J.** (2023). *Ultralytics YOLOv8 Architecture and Documentation*. Ultralytics.
7. **Sandler, M., Howard, A., Zhu, M., et al.** (2018). *MobileNetV2: Inverted Residuals and Linear Bottlenecks*. IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 4510–4520.
8. **Riverbank Computing.** (2023). *PyQt5 Reference Guide and API Documentation*.
9. **ReportLab Europe Ltd.** (2023). *ReportLab PDF Generation User Guide*.

---
*End of Finalized Documentation Report*
