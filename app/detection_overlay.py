"""
detection_overlay.py
--------------------
Computer Vision rendering engine for RadiVision AI.
Composites anti-aliased bounding boxes, FDI dental labels, fracture markers,
and clinical diagnostic status badges onto radiographs using OpenCV (with PIL fallback).
"""

import os
import time
from typing import List, Dict, Any, Optional

try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except (ImportError, OSError, Exception):
    HAS_OPENCV = False

from PIL import Image, ImageDraw, ImageFont

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")

def draw_findings_overlay(
    image_path: str,
    findings: List[Dict[str, Any]],
    scan_type: str,
    summary_prediction: str,
    summary_confidence: float,
    output_prefix: str = "annotated"
) -> str:
    """
    Renders visual bounding boxes, labels, and status badges onto the radiograph.
    Saves the result to reports/ and returns the absolute path to the annotated image.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    timestamp = int(time.time() * 1000)
    output_path = os.path.join(REPORTS_DIR, f"{output_prefix}_{timestamp}.png")

    if not os.path.exists(image_path):
        # Fallback if image doesn't exist
        img = Image.new('RGB', (800, 600), color=(20, 30, 40))
        draw = ImageDraw.Draw(img)
        draw.text((40, 280), f"Image file not found: {image_path}", fill=(255, 255, 255))
        img.save(output_path)
        return output_path

    if HAS_OPENCV:
        return _render_with_opencv(image_path, findings, scan_type, summary_prediction, summary_confidence, output_path)
    else:
        return _render_with_pil(image_path, findings, scan_type, summary_prediction, summary_confidence, output_path)

def _render_with_opencv(
    image_path: str,
    findings: List[Dict[str, Any]],
    scan_type: str,
    summary_prediction: str,
    summary_confidence: float,
    output_path: str
) -> str:
    """OpenCV implementation for high-speed, anti-aliased annotation rendering."""
    img = cv2.imread(image_path)
    if img is None:
        # If OpenCV fails to read (e.g. unicode path or unsupported encoding), fallback to PIL
        return _render_with_pil(image_path, findings, scan_type, summary_prediction, summary_confidence, output_path)

    h, w = img.shape[:2]

    # Color definitions in BGR
    RED_ALERT = (74, 75, 226)       # #E24B4A in BGR
    GREEN_SUCCESS = (34, 153, 99)   # #639922 in BGR
    AMBER_WARN = (23, 117, 186)     # #BA7517 in BGR
    NAVY_BRAND = (102, 61, 11)      # #0B3D66 in BGR
    WHITE = (255, 255, 255)

    is_abnormal = any(term in summary_prediction.lower() for term in ["abnormal", "pneumonia", "fracture", "caries", "lesion"])
    badge_color = RED_ALERT if is_abnormal else GREEN_SUCCESS

    # 1. Draw Bounding Boxes for Object Detection findings (Bone & Dental)
    for f in findings:
        bx = f.get("bbox_x")
        by = f.get("bbox_y")
        bw = f.get("bbox_w")
        bh = f.get("bbox_h")

        if bx is not None and by is not None and bw is not None and bh is not None:
            # Denormalize coordinates
            x1 = int(bx * w)
            y1 = int(by * h)
            x2 = int((bx + bw) * w)
            y2 = int((by + bh) * h)

            # Ensure inside boundaries
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w - 1, x2), min(h - 1, y2)

            box_color = RED_ALERT if "fracture" in f['label'].lower() or "caries" in f['label'].lower() or "lesion" in f['label'].lower() else GREEN_SUCCESS

            # Draw rectangular bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), box_color, 3, cv2.LINE_AA)

            # Construct label tag
            if f.get("tooth_number"):
                tag_text = f"Tooth #{f['tooth_number']}: {f['label']} ({int(f['confidence'] * 100)}%)"
            else:
                tag_text = f"{f['label']} ({int(f['confidence'] * 100)}%)"

            # Tag background banner
            (tw, th), baseline = cv2.getTextSize(tag_text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
            tag_y1 = max(0, y1 - th - 10)
            tag_y2 = y1
            cv2.rectangle(img, (x1, tag_y1), (x1 + tw + 12, tag_y2), box_color, -1)
            cv2.putText(img, tag_text, (x1 + 6, tag_y2 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, WHITE, 2, cv2.LINE_AA)

    # 2. Draw Top Diagnostic Banner
    banner_text = f"[{scan_type.upper()}] {summary_prediction.upper()} (Confidence: {summary_confidence * 100:.1f}%)"
    cv2.rectangle(img, (0, 0), (w, 48), NAVY_BRAND, -1)
    cv2.rectangle(img, (0, 44), (w, 48), badge_color, -1)
    cv2.putText(img, banner_text, (18, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.75, WHITE, 2, cv2.LINE_AA)

    # Save annotated result
    cv2.imwrite(output_path, img)
    return output_path

def _render_with_pil(
    image_path: str,
    findings: List[Dict[str, Any]],
    scan_type: str,
    summary_prediction: str,
    summary_confidence: float,
    output_path: str
) -> str:
    """Pillow fallback implementation ensuring universal cross-platform rendering."""
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size

    RED_ALERT = (226, 75, 74)
    GREEN_SUCCESS = (99, 153, 34)
    NAVY_BRAND = (11, 61, 102)
    WHITE = (255, 255, 255)

    is_abnormal = any(term in summary_prediction.lower() for term in ["abnormal", "pneumonia", "fracture", "caries", "lesion"])
    badge_color = RED_ALERT if is_abnormal else GREEN_SUCCESS

    # 1. Bounding Boxes
    for f in findings:
        bx, by, bw, bh = f.get("bbox_x"), f.get("bbox_y"), f.get("bbox_w"), f.get("bbox_h")
        if bx is not None and by is not None and bw is not None and bh is not None:
            x1 = int(bx * w)
            y1 = int(by * h)
            x2 = int((bx + bw) * w)
            y2 = int((by + bh) * h)

            draw.rectangle([x1, y1, x2, y2], outline=RED_ALERT, width=3)
            tag = f"{f['label']} ({int(f['confidence'] * 100)}%)"
            if f.get("tooth_number"):
                tag = f"Tooth #{f['tooth_number']}: {tag}"

            draw.rectangle([x1, max(0, y1 - 22), x1 + len(tag) * 9, y1], fill=RED_ALERT)
            draw.text((x1 + 4, max(0, y1 - 18)), tag, fill=WHITE)

    # 2. Top Banner
    draw.rectangle([0, 0, w, 44], fill=NAVY_BRAND)
    draw.rectangle([0, 42, w, 46], fill=badge_color)
    banner_text = f"[{scan_type.upper()}] {summary_prediction.upper()} ({summary_confidence * 100:.1f}%)"
    draw.text((16, 12), banner_text, fill=WHITE)

    img.save(output_path)
    return output_path
