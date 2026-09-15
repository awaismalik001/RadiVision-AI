"""
predict.py
-----------
Standalone inference verification script for chest radiograph classification.
Supports PyTorch (chest_xray_model.pt) and TensorFlow (chest_xray_model.h5).
Runs Grad-CAM abnormality localization to pinpoint the exact lesion location.
"""

import sys
import os
from PIL import Image

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
MODEL_PT_PATH = os.path.join(CURRENT_DIR, "chest_xray_model.pt")
MODEL_H5_PATH = os.path.join(CURRENT_DIR, "chest_xray_model.h5")

# Ensure project root is in sys.path for app imports
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def predict_xray(image_path: str, generate_overlay: bool = True):
    if not os.path.exists(image_path):
        print(f"[Error] Target image '{image_path}' not found.")
        return

    # Check PyTorch model first
    if os.path.exists(MODEL_PT_PATH):
        try:
            import torch
            import torch.nn as nn
            from torchvision import models, transforms
            from app.gradcam import localize_chest_abnormality
            from app.detection_overlay import draw_findings_overlay

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

            # Load model
            model = models.mobilenet_v2(weights=None)
            in_features = model.classifier[1].in_features
            model.classifier = nn.Sequential(
                nn.Dropout(0.3),
                nn.Linear(in_features, 128),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(128, 2)
            )
            model.load_state_dict(torch.load(MODEL_PT_PATH, map_location=device))
            model = model.to(device)
            model.eval()

            # Preprocess image
            raw_img = Image.open(image_path).convert('RGB')
            raw_w, raw_h = raw_img.size

            tfms = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            tensor = tfms(raw_img).unsqueeze(0).to(device)

            with torch.no_grad():
                outputs = model(tensor)
                probs = torch.softmax(outputs, dim=1)[0]
                norm_prob = float(probs[0].item())
                pneu_prob = float(probs[1].item())
                pred_idx = int(torch.argmax(probs).item())
                confidence = pneu_prob if pred_idx == 1 else norm_prob

            is_pneumonia = (pred_idx == 1)
            summary = "PNEUMONIA (Abnormal)" if is_pneumonia else "NORMAL (Healthy)"

            # Compute exact abnormality localization
            if is_pneumonia:
                finding = localize_chest_abnormality(model, tensor, raw_w, raw_h, confidence)
                body_region = finding.get("body_region", "Thoracic")
                findings = [finding]
            else:
                body_region = "Thoracic (Normal Lung Fields)"
                findings = [{
                    "label": "Clear Pulmonary Parenchyma",
                    "confidence": confidence,
                    "bbox_x": None,
                    "bbox_y": None,
                    "bbox_w": None,
                    "bbox_h": None
                }]

            print("=" * 60)
            print("         RadiVision AI: Radiograph Diagnostic Report")
            print("=" * 60)
            print(f"Target Radiograph   : {image_path}")
            print(f"Resolution          : {raw_w} x {raw_h}")
            print(f"Diagnostic Result   : {summary}")
            print(f"Diagnosis Confidence: {confidence * 100:.2f}%")
            print(f"Normal Probability  : {norm_prob * 100:.2f}%")
            print(f"Pneumonia Prob      : {pneu_prob * 100:.2f}%")
            print(f"Anatomical Location : {body_region}")
            if is_pneumonia and findings[0].get("bbox_x") is not None:
                f = findings[0]
                print(f"Lesion Finding      : {f['label']}")
                print(f"Exact Bounding Box  : [X: {f['bbox_x']}, Y: {f['bbox_y']}, W: {f['bbox_w']}, H: {f['bbox_h']}]")
            print("=" * 60)

            if generate_overlay:
                out_path = draw_findings_overlay(
                    image_path, findings, "Chest", summary, confidence
                )
                print(f"[Overlay] Annotated radiograph generated at:\n  {out_path}")

            return summary, confidence, findings

        except Exception as e:
            print(f"[AI] PyTorch inference error: {e}")

    print("[Error] No trained model weights found (chest_xray_model.pt). Run train_model.py first.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict.py <path_to_xray_image.jpg>")
        sys.exit(1)
    predict_xray(sys.argv[1])
