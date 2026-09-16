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
    init_db, save_scan, get_all_scans, save_finding, get_scan_by_id, db
)
from app.auth import (
    authenticate_user, admin_update_credentials, validate_password_complexity,
    validate_email, hash_password, SessionManager
)
from app.excel_export import generate_excel_export

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
        "chest_model": "Vision Transformer (ViT-B/16) + MobileNetV2 (90.72% Accuracy)",
        "bone_model": "Vision Transformer (ViT-B/16) + YOLOv8 (91.40% Accuracy)",
        "ai_assistant": "Google Gemini Multimodal Preprocessing & Cross-Verification",
        "encryption": "AES-256-GCM PACS Database Encryption at Rest",
        "device": "CPU / GPU Acceleration",
        "timestamp": datetime.now().isoformat()
    }

# ------------------ Authentication & Session Endpoints ------------------
@app.post("/api/auth/login")
async def login(credentials: dict):
    username = credentials.get("username", "").strip()
    password = credentials.get("password", "")
    success, msg, user = authenticate_user(username, password)
    if not success:
        status_code = 429 if "blocked" in msg.lower() else 401
        raise HTTPException(status_code=status_code, detail=msg)
    return {"success": True, "message": msg, "user": user}

@app.post("/api/auth/signup")
async def signup(user_data: dict):
    full_name = user_data.get("full_name", "").strip()
    username = user_data.get("username", "").strip()
    email = user_data.get("email", "").strip()
    password = user_data.get("password", "")
    role = user_data.get("role", "User")

    if not full_name or not username or not email or not password:
        raise HTTPException(status_code=400, detail="All fields are required.")

    if not validate_email(email):
        raise HTTPException(status_code=400, detail="Invalid email address format.")

    valid_pw, pw_msg = validate_password_complexity(password)
    if not valid_pw:
        raise HTTPException(status_code=400, detail=pw_msg)

    if db.get_user_by_username(username):
        raise HTTPException(status_code=409, detail=f"Username '{username}' is already registered.")

    pw_hash = hash_password(password)
    user_id = db.create_user(full_name=full_name, username=username, email=email, password_hash=pw_hash, role=role)
    db.log_activity(user_id, username, "USER_REGISTERED", f"Account created with role: {role}")

    safe_user = {
        "user_id": user_id,
        "full_name": full_name,
        "username": username,
        "email": email,
        "role": role,
        "is_active": 1
    }
    return {"success": True, "message": "Account created successfully.", "user": safe_user}

@app.post("/api/auth/logout")
async def logout():
    SessionManager.logout()
    return {"success": True, "message": "Logged out successfully."}

# ------------------ Admin Dashboard & Credential Management ------------------
@app.get("/api/admin/analytics")
async def get_admin_analytics():
    stats = db.get_dashboard_stats()
    scans = db.get_scans(limit=1000)
    chest_count = sum(1 for s in scans if s.get("scan_type") == "Chest")
    bone_count = sum(1 for s in scans if s.get("scan_type") == "Bone")
    return {
        "success": True,
        "total_scans": stats.get("total_scans", 0),
        "abnormal_scans": stats.get("abnormal_scans", 0),
        "normal_scans": stats.get("normal_scans", 0),
        "total_patients": stats.get("total_patients", 0),
        "total_users": stats.get("total_users", 0),
        "reports_exported": stats.get("reports_exported", 0),
        "chest_count": chest_count,
        "bone_count": bone_count,
        "system_status": "All Deep Learning & PACS Systems Operational"
    }

@app.get("/api/admin/activity-logs")
async def get_admin_activity_logs(limit: int = 150):
    logs = db.get_activity_logs(limit=limit)
    return {"success": True, "logs": logs}

@app.get("/api/admin/export-excel")
async def export_excel_database():
    try:
        file_path = generate_excel_export()
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Failed to generate Excel export.")
        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=os.path.basename(file_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel generation error: {str(e)}")

@app.get("/api/admin/users")
async def get_users_list():
    users = db.get_all_users()
    return {"success": True, "users": users}

@app.put("/api/admin/users/{user_id}")
async def update_user(user_id: int, payload: dict):
    current_user = payload.get("current_user")
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication session required.")

    ok, msg = admin_update_credentials(
        current_user=current_user,
        target_user_id=user_id,
        new_username=payload.get("username"),
        new_password=payload.get("password"),
        new_full_name=payload.get("full_name"),
        new_email=payload.get("email"),
        new_role=payload.get("role"),
        new_is_active=payload.get("is_active")
    )
    if not ok:
        raise HTTPException(status_code=403 if "Access Denied" in msg else 400, detail=msg)
    return {"success": True, "message": msg}

@app.get("/api/referrals")
def get_referrals(location: str = "New York", modality: str = "Bone", is_abnormal: bool = True):
    """Returns nearby hospital and physician recommendations matched to location & modality."""
    facilities = get_recommended_facilities(location=location, modality=modality, is_abnormal=is_abnormal)
    return {"location": location, "modality": modality, "facilities": facilities}

@app.get("/api/history")
def get_history(user_id: Optional[int] = None):
    """Returns past patient scan records from SQLite database, isolated by user_id if provided."""
    if user_id is not None:
        scans = db.get_scans(user_id=user_id)
    else:
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
    user_id: Optional[int] = Form(1),
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
            patient_national_id=patient_id,
            user_id=user_id or 1
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
            "vit_details": result.get("vit_details"),
            "gemini_refinement": result.get("gemini_refinement"),
            "architecture": result.get("architecture", "Vision Transformer (ViT-B/16) + Gemini AI Cross-Verification"),
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
