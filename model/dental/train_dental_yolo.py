"""
train_dental_yolo.py
--------------------
Fine-tunes a pre-trained YOLOv8 model for panoramic dental radiograph analysis
and pathology detection (caries, lesions, impactions) with FDI tooth correlation.
"""

import os
import sys

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
YAML_PATH = os.path.join(CURRENT_DIR, "dental_dataset.yaml")
EXPORT_MODEL_PATH = os.path.join(CURRENT_DIR, "dental_xray_model.pt")

def train():
    if not HAS_YOLO:
        print("[Error] Ultralytics is not installed. Run: pip install ultralytics")
        return

    print("=" * 60)
    print("   TRAINING YOLOV8 DENTAL PANORAMIC DETECTOR")
    print("=" * 60)

    # Initialize YOLOv8 small model for multi-tooth feature extraction
    model = YOLO("yolov8s.pt")

    results = model.train(
        data=YAML_PATH,
        epochs=30,
        imgsz=640,
        batch=16,
        patience=0,  # 0 disables EarlyStopping
        save=True,
        project=CURRENT_DIR,
        name="dental_train_run"
    )

    # Save final best weights from the actual training run
    save_dir = str(results.save_dir) if hasattr(results, 'save_dir') else os.path.join(CURRENT_DIR, "dental_train_run")
    best_weights = os.path.join(save_dir, "weights", "best.pt")
    if not os.path.exists(best_weights):
        import glob
        all_bests = glob.glob(os.path.join(CURRENT_DIR, "dental_train_run*", "weights", "best.pt"))
        if all_bests:
            best_weights = max(all_bests, key=os.path.getmtime)

    if os.path.exists(best_weights):
        import shutil
        shutil.copy(best_weights, EXPORT_MODEL_PATH)
        print(f"\n[Success] Model exported to: {EXPORT_MODEL_PATH}")
    else:
        model.save(EXPORT_MODEL_PATH)
        print(f"\n[Success] Model saved to: {EXPORT_MODEL_PATH}")

if __name__ == "__main__":
    train()
