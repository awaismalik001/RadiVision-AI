"""
train_bone_yolo.py
------------------
Fine-tunes a pre-trained YOLOv8 model for bone fracture localization
and body-region identification using FracAtlas / GRAZPEDWRI-DX datasets.
"""

import os
import sys

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
YAML_PATH = os.path.join(CURRENT_DIR, "bone_dataset.yaml")
EXPORT_MODEL_PATH = os.path.join(CURRENT_DIR, "bone_fracture_model.pt")

def train():
    if not HAS_YOLO:
        print("[Error] Ultralytics is not installed. Run: pip install ultralytics")
        return

    print("=" * 60)
    print("   TRAINING YOLOV8 BONE FRACTURE & REGION DETECTOR")
    print("=" * 60)

    # Initialize YOLOv8 nano pre-trained model for fast transfer learning
    model = YOLO("yolov8n.pt")

    # Train model
    results = model.train(
        data=YAML_PATH,
        epochs=30,
        imgsz=640,
        batch=16,
        patience=5,
        save=True,
        project=CURRENT_DIR,
        name="bone_train_run"
    )

    # Save final best weights
    best_weights = os.path.join(CURRENT_DIR, "bone_train_run", "weights", "best.pt")
    if os.path.exists(best_weights):
        import shutil
        shutil.copy(best_weights, EXPORT_MODEL_PATH)
        print(f"\n[Success] Model exported to: {EXPORT_MODEL_PATH}")
    else:
        model.save(EXPORT_MODEL_PATH)
        print(f"\n[Success] Model saved to: {EXPORT_MODEL_PATH}")

if __name__ == "__main__":
    train()
