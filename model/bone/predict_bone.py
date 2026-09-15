"""
predict_bone.py
----------------
Standalone inference verification script for musculoskeletal bone fracture detection.
Evaluates any bone X-ray, pinpoints fracture coordinates using Grad-CAM,
and composites the visual bounding box and label overlay.
"""

import sys
import os
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
MODEL_PATH = os.path.join(CURRENT_DIR, "bone_fracture_model.pt")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def predict_bone_image(image_path: str, generate_overlay: bool = True):
    if not os.path.exists(image_path):
        print(f"[Error] Target image '{image_path}' not found.")
        return

    if not os.path.exists(MODEL_PATH):
        print(f"[Error] Model weights not found at: {MODEL_PATH}")
        return

    try:
        import torch
        import torch.nn as nn
        from torchvision import models, transforms
        from app.bone_gradcam import localize_bone_fracture
        from app.detection_overlay import draw_findings_overlay

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load architecture
        model = models.mobilenet_v2(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 2)
        )
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model = model.to(device)
        model.eval()

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
            frac_prob = float(probs[0].item())
            norm_prob = float(probs[1].item())
            pred_idx = int(torch.argmax(probs).item())

        is_fractured = (pred_idx == 0)
        confidence = frac_prob if is_fractured else norm_prob
        summary = "FRACTURE DETECTED (Abnormal)" if is_fractured else "NO FRACTURE OBSERVED (Normal)"

        if is_fractured:
            finding = localize_bone_fracture(model, tensor, raw_w, raw_h, confidence, fracture_class_idx=0)
            body_region = finding.get("body_region", "Extremity / Skeletal")
            findings = [finding]
        else:
            body_region = "Extremity / Intact Cortices"
            findings = [{
                "label": "Intact Bony Cortices",
                "tooth_number": None,
                "confidence": confidence,
                "bbox_x": None,
                "bbox_y": None,
                "bbox_w": None,
                "bbox_h": None
            }]

        print("=" * 60)
        print("         RadiVision AI: Bone Fracture Diagnostic Report")
        print("=" * 60)
        print(f"Target Radiograph   : {image_path}")
        print(f"Resolution          : {raw_w} x {raw_h}")
        print(f"Diagnostic Result   : {summary}")
        print(f"Diagnosis Confidence: {confidence * 100:.2f}%")
        print(f"Fracture Probability: {frac_prob * 100:.2f}%")
        print(f"Normal Probability  : {norm_prob * 100:.2f}%")
        print(f"Anatomical Location : {body_region}")
        if is_fractured and findings[0].get("bbox_x") is not None:
            f = findings[0]
            print(f"Fracture Finding    : {f['label']}")
            print(f"Exact Bounding Box  : [X: {f['bbox_x']}, Y: {f['bbox_y']}, W: {f['bbox_w']}, H: {f['bbox_h']}]")
        print("=" * 60)

        if generate_overlay:
            out_path = draw_findings_overlay(
                image_path, findings, "Bone", summary, confidence
            )
            print(f"[Overlay] Annotated radiograph generated at:\n  {out_path}")

        return summary, confidence, findings

    except Exception as e:
        print(f"[AI Engine] Bone prediction error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict_bone.py <path_to_bone_xray.jpg>")
        sys.exit(1)
    predict_bone_image(sys.argv[1])
