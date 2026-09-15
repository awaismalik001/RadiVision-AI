"""
evaluate_dental.py
------------------
Comprehensive clinical evaluation suite for the RadiVision AI Dental Pathology YOLO Model.
Evaluates the model across the test radiographs using Ultralytics YOLO metrics:
- Overall mAP50 and mAP50-95
- Clinical Precision & Recall
- Per-class pathology performance (Caries, Deep Caries, Periapical Lesion, Impacted Tooth)
- Generates publication-ready confusion matrix and metric plots
"""

import os
import sys
import shutil

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "dental_xray_model.pt")
YAML_PATH = os.path.join(CURRENT_DIR, "dental_dataset.yaml")

def evaluate_dental_model():
    print("=" * 65)
    print("       RadiVision AI: Dental Panoramic Pathology Evaluation")
    print("=" * 65)

    if not HAS_YOLO:
        print("[Error] Ultralytics YOLO is not installed.")
        return

    if not os.path.exists(MODEL_PATH):
        print(f"[Error] Model weights not found at: {MODEL_PATH}")
        return

    if not os.path.exists(YAML_PATH):
        print(f"[Error] Dataset configuration not found at: {YAML_PATH}")
        return

    model = YOLO(MODEL_PATH)
    print(f"Model Path    : {MODEL_PATH}")
    print(f"Dataset Config: {YAML_PATH}\n")

    # Run validation on test split
    metrics = model.val(data=YAML_PATH, split="test", verbose=True, plots=True)

    mp50_95 = metrics.box.map
    mp50 = metrics.box.map50
    mp75 = metrics.box.map75
    precision = metrics.box.mp
    recall = metrics.box.mr
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    print("\n" + "=" * 65)
    print("                 CLINICAL DENTAL PERFORMANCE REPORT")
    print("=" * 65)
    print(f"  Mean Average Precision (mAP50)   : {mp50 * 100:.2f}%")
    print(f"  Overall mAP (mAP50-95)           : {mp50_95 * 100:.2f}%")
    print(f"  Clinical Detection Recall (Sensitivity): {recall * 100:.2f}%")
    print(f"  Diagnostic Precision (PPV)       : {precision * 100:.2f}%")
    print(f"  Clinical F1-Score                : {f1 * 100:.2f}%")
    print("-" * 65)

    # Copy generated plots to model directory
    val_dir = str(metrics.save_dir) if hasattr(metrics, "save_dir") else ""
    if val_dir and os.path.exists(val_dir):
        for plot_name in ["confusion_matrix.png", "confusion_matrix_normalized.png", "PR_curve.png", "F1_curve.png"]:
            src = os.path.join(val_dir, plot_name)
            if os.path.exists(src):
                dst = os.path.join(CURRENT_DIR, plot_name.lower())
                shutil.copy2(src, dst)
                print(f"  [Saved Plot] {plot_name} -> {dst}")
    print("=" * 65)

    return {
        "mAP50": mp50,
        "mAP50_95": mp50_95,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

if __name__ == "__main__":
    evaluate_dental_model()
