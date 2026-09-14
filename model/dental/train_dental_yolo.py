# train_dental_yolo.py
# -----------------------------------
# Fine‑tunes a pre‑trained YOLOv8 model for panoramic dental radiograph analysis
# (caries, lesions, impactions) with FDI tooth correlation.
# -----------------------------------

import os
import random
import numpy as np
import torch

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False

# -------------------------------------------------
# Deterministic setup – fixed seed for reproducibility
# -------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
# Ensure deterministic CuDNN behaviour (CPU only but kept for completeness)
if torch.cuda.is_available():
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

# Paths
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

    # Initialize YOLOv8 small model for multi‑tooth feature extraction
    model = YOLO("yolov8s.pt")

    # Train with deterministic seed and EarlyStopping disabled (patience=0)
    results = model.train(
        data=YAML_PATH,
        epochs=30,
        imgsz=640,
        batch=16,
        patience=0,          # disables EarlyStopping
        seed=SEED,
        save=True,
        project=CURRENT_DIR,
        name="dental_train_run",
    )

    # -----------------------------------------------------------------
    # Export the best checkpoint from the run folder (robust fallback)
    # -----------------------------------------------------------------
    save_dir = str(results.save_dir) if hasattr(results, "save_dir") else os.path.join(CURRENT_DIR, "dental_train_run")
    best_weights = os.path.join(save_dir, "weights", "best.pt")
    if not os.path.exists(best_weights):
        # Fallback: search any run folder under CURRENT_DIR for best.pt
        import glob
        candidates = glob.glob(os.path.join(CURRENT_DIR, "dental_train_run*", "weights", "best.pt"))
        if candidates:
            best_weights = max(candidates, key=os.path.getmtime)

    if os.path.exists(best_weights):
        import shutil
        shutil.copy(best_weights, EXPORT_MODEL_PATH)
        print(f"\n[Success] Model exported to: {EXPORT_MODEL_PATH}")
    else:
        # As a last resort, save the model directly (may not be the best checkpoint)
        model.save(EXPORT_MODEL_PATH)
        print(f"\n[Success] Model saved to: {EXPORT_MODEL_PATH}")

if __name__ == "__main__":
    train()
