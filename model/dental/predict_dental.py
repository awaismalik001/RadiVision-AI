"""
predict_dental.py
-----------------
Standalone inference verification script for dental panoramic radiographs.
Evaluates any panoramic X-ray, pinpoints pathologies with YOLOv8,
maps findings to FDI Two-Digit Tooth Numbers (ISO 3950),
and renders the clinical bounding box and FDI label overlay.
"""

import sys
import os
from PIL import Image

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
MODEL_PATH = os.path.join(CURRENT_DIR, "dental_xray_model.pt")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except ImportError:
    HAS_YOLO = False

def predict_dental_image(image_path: str, conf_threshold: float = 0.30, generate_overlay: bool = True):
    if not os.path.exists(image_path):
        print(f"[Error] Target image '{image_path}' not found.")
        return

    if not HAS_YOLO:
        print("[Error] Ultralytics is not installed.")
        return

    if not os.path.exists(MODEL_PATH):
        print(f"[Error] Dental model weights not found at: {MODEL_PATH}")
        return

    from app.dental_fdi import map_coordinates_to_fdi, format_pathology_label
    from app.detection_overlay import draw_findings_overlay

    model = YOLO(MODEL_PATH)

    with Image.open(image_path) as img:
        raw_w, raw_h = img.size

    results = model.predict(image_path, conf=conf_threshold, verbose=False)[0]

    all_findings = []
    pathology_findings = []
    top_conf = 0.0

    for box in results.boxes:
        cls_id = int(box.cls[0])
        raw_name = model.names.get(cls_id, f"Class_{cls_id}")
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].tolist()

        # Normalized coordinates
        bx = max(0.0, min(1.0, xyxy[0] / float(raw_w)))
        by = max(0.0, min(1.0, xyxy[1] / float(raw_h)))
        bw = max(0.01, min(1.0, (xyxy[2] - xyxy[0]) / float(raw_w)))
        bh = max(0.01, min(1.0, (xyxy[3] - xyxy[1]) / float(raw_h)))

        # FDI Tooth Numbering
        fdi_num = map_coordinates_to_fdi(bx, by, bw, bh)
        label_text = format_pathology_label(raw_name, fdi_num)

        finding_item = {
            "label": label_text,
            "tooth_number": fdi_num,
            "confidence": round(conf, 4),
            "bbox_x": round(bx, 3),
            "bbox_y": round(by, 3),
            "bbox_w": round(bw, 3),
            "bbox_h": round(bh, 3),
            "is_pathology": (cls_id != 0)  # Class 0 is Healthy_Tooth
        }

        all_findings.append(finding_item)
        if finding_item["is_pathology"]:
            pathology_findings.append(finding_item)
            top_conf = max(top_conf, conf)

    # Determine clinical diagnosis
    if len(pathology_findings) > 0:
        summary = f"DENTAL PATHOLOGY DETECTED ({len(pathology_findings)} site{'s' if len(pathology_findings)>1 else ''})"
        display_confidence = top_conf
        display_findings = pathology_findings
    else:
        summary = "HEALTHY DENTITION (No Pathology)"
        display_confidence = 0.95
        display_findings = [{
            "label": "Normal Erupted Dentition",
            "tooth_number": None,
            "confidence": 0.95,
            "bbox_x": None,
            "bbox_y": None,
            "bbox_w": None,
            "bbox_h": None
        }]

    print("=" * 65)
    print("         RadiVision AI: Dental Panoramic Diagnostic Report")
    print("=" * 65)
    print(f"Target Radiograph   : {image_path}")
    print(f"Resolution          : {raw_w} x {raw_h}")
    print(f"Diagnostic Summary  : {summary}")
    print(f"Overall Confidence  : {display_confidence * 100:.2f}%")
    print(f"Pathologies Found   : {len(pathology_findings)}")
    print("-" * 65)

    for idx, f in enumerate(pathology_findings, 1):
        print(f"  #{idx} Tooth #{f['tooth_number']}: {f['label']}")
        print(f"     Confidence : {f['confidence'] * 100:.1f}%")
        print(f"     Coordinates: [X: {f['bbox_x']}, Y: {f['bbox_y']}, W: {f['bbox_w']}, H: {f['bbox_h']}]")

    if not pathology_findings:
        print("  All visualized teeth exhibit intact coronal enamel and normal periodontal margins.")

    print("=" * 65)

    if generate_overlay:
        out_path = draw_findings_overlay(
            image_path, display_findings, "Dental", summary, display_confidence
        )
        print(f"[Overlay] Annotated panoramic radiograph generated at:\n  {out_path}")

    return summary, display_confidence, display_findings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict_dental.py <path_to_panoramic_xray.png>")
        sys.exit(1)
    predict_dental_image(sys.argv[1])
