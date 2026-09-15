"""
server.py
---------
FastAPI REST API Bridge for RadiVision AI.
Connects the React + Tailwind + Framer Motion frontend to:
- PyTorch Chest Model (90.72% Accuracy)
- PyTorch Bone Fracture Model (91.40% Accuracy)
- Dynamic Grad-CAM Lesion & Fracture Localization
- GPS Hospital & Doctor Recommendation Engine
- Professional Clinical PDF Report Generator
- SQLite PACS Database
"""

import os
import sys
import uuid
import shutil
from typing import Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.model_engine import ai_engine
from app.hospital_referral import get_recommended_facilities
from app.report_generator import generate_pdf_report
from app.database import (
    init_db, save_scan, get_all_scans, save_finding, get_scan_by_id
)

app = FastAPI(title="RadiVision AI API", version="2.0.0")

# Enable CORS for React frontend (Vite default: http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure required directories exist
UPLOADS_DIR = os.path.join(PROJECT_ROOT, "uploads")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
ANNOTATED_DIR = os.path.join(PROJECT_ROOT, "runs", "annotated")
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(ANNOTATED_DIR, exist_ok=True)

# Mount static file endpoints
app.mount("/static/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.mount("/static/reports", StaticFiles(directory=REPORTS_DIR), name="reports")
app.mount("/static/annotated", StaticFiles(directory=ANNOTATED_DIR), name="annotated")

# Initialize database
init_db()

@app.get("/api/health")
def get_health():
    """Returns AI Engine and telemetry status."""
    return {
        "status": "online",
        "chest_model": "MobileNetV2 (90.72% Accuracy, 0.9534 AUC)",
        "bone_model": "MobileNetV2 (91.40% Accuracy, 0.9691 AUC)",
        "device": "CPU (8 Threads)",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/referrals")
def get_referrals(location: str = "New York", modality: str = "Bone", is_abnormal: bool = True):
    """Returns nearby hospital and physician recommendations matched to location & modality."""
    facilities = get_recommended_facilities(location=location, modality=modality, is_abnormal=is_abnormal)
    return {"location": location, "modality": modality, "facilities": facilities}

@app.get("/api/history")
def get_history():
    """Returns past patient scan records from SQLite database."""
    scans = get_all_scans()
    return {"scans": scans}

@app.post("/api/predict")
async def predict_scan(
    file: UploadFile = File(...),
    modality: str = Form("Bone"),
    patient_name: str = Form("Sarah Chen"),
    patient_age: int = Form(34),
    patient_gender: str = Form("Female"),
    patient_id: Optional[str] = Form(None),
    location: str = Form("New York"),
):
    """
    Executes deep learning inference on an uploaded radiograph.
    Returns diagnostic classification, Grad-CAM spatial coordinates, and nearby hospital referrals.
    """
    if not patient_id:
        patient_id = f"RV-{uuid.uuid4().hex[:6].upper()}"

    # Save uploaded file
    file_ext = os.path.splitext(file.filename)[1] or ".jpg"
    unique_name = f"{patient_id}_{uuid.uuid4().hex[:8]}{file_ext}"
    saved_path = os.path.join(UPLOADS_DIR, unique_name)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run AI inference
    try:
        mod_clean = modality.strip().capitalize()
        if "bone" in mod_clean.lower():
            result = ai_engine.predict_bone(saved_path)
            scan_type_str = "Bone"
        else:
            result = ai_engine.predict_chest(saved_path)
            scan_type_str = "Chest"

        prediction = result.get("prediction", "Normal")
        confidence = float(result.get("confidence", 0.95))
        body_region = result.get("body_region", "Skeletal")
        findings = result.get("findings", [])

        # Check if abnormality detected
        is_abnormal = "abnormal" in prediction.lower() or "fracture" in prediction.lower() or "pneumonia" in prediction.lower()

        # Generate annotated image
        annotated_filename = f"annotated_{unique_name}"
        annotated_path = os.path.join(ANNOTATED_DIR, annotated_filename)
        try:
            # Draw bounding box and Grad-CAM highlight on image
            from PIL import Image, ImageDraw, ImageFont
            img = Image.open(saved_path).convert("RGB")
            w, h = img.size
            draw = ImageDraw.Draw(img)

            for f in findings:
                bx = f.get("bbox_x")
                by = f.get("bbox_y")
                bw = f.get("bbox_w")
                bh = f.get("bbox_h")
                if bx is not None and by is not None and bw is not None and bh is not None:
                    x0 = bx * w
                    y0 = by * h
                    x1 = (bx + bw) * w
                    y1 = (by + bh) * h
                    # Draw bold red bounding box
                    for offset in range(3):
                        draw.rectangle([x0 - offset, y0 - offset, x1 + offset, y1 + offset], outline="red")
            img.save(annotated_path)
        except Exception as draw_err:
            print(f"[Server] Annotation error: {draw_err}")
            shutil.copy2(saved_path, annotated_path)

        # Get GPS-matched hospital & doctor referrals
        facilities = get_recommended_facilities(location, scan_type_str, is_abnormal=is_abnormal)

        # Record scan to SQLite database
        scan_db_id = save_scan(
            patient_name=patient_name,
            patient_age=patient_age,
            patient_gender=patient_gender,
            scan_type=scan_type_str,
            image_path=saved_path,
            prediction=prediction,
            confidence=confidence,
            body_region=body_region,
            annotated_image_path=annotated_path,
            patient_national_id=patient_id
        )

        for finding in findings:
            save_finding(
                scan_id=scan_db_id,
                label=finding.get("label", "Finding"),
                tooth_number=None,
                confidence=finding.get("confidence", confidence),
                bbox_x=finding.get("bbox_x"),
                bbox_y=finding.get("bbox_y"),
                bbox_w=finding.get("bbox_w"),
                bbox_h=finding.get("bbox_h")
            )

        return {
            "success": True,
            "scan_id": scan_db_id,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "patient_age": patient_age,
            "patient_gender": patient_gender,
            "location": location,
            "scan_type": scan_type_str,
            "prediction": prediction,
            "confidence": confidence,
            "body_region": body_region,
            "findings": findings,
            "image_url": f"/static/uploads/{unique_name}",
            "annotated_url": f"/static/annotated/{annotated_filename}",
            "local_annotated_path": annotated_path,
            "facilities": facilities,
            "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p")
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export-pdf")
async def export_pdf(data: dict):
    """
    Generates an official RSNA-style clinical PDF report matching the exact
    capsule-header template and returns it for download.
    """
    try:
        pdf_path = generate_pdf_report(data)
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="Failed to compile PDF report.")

        filename = os.path.basename(pdf_path)
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
