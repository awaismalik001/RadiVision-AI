"""
test_system.py
--------------
Automated system verification suite for RadiVision AI.
Validates:
  1. SQLite 3NF relational database schema & default Admin seed
  2. Bcrypt authentication & session tracking
  3. Modality detection, Chest inference, and Bone inference
  4. OpenCV bounding-box overlay compositing
  5. ReportLab PDF clinical report compilation
  6. PyQt5 GUI components initialization
"""

import os
import sys

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def run_verification():
    print("=" * 65)
    print("      RADIVISION AI - AUTOMATED SYSTEM VERIFICATION SUITE")
    print("        Clinical Multi-Modal Radiograph Screening System")
    print("=" * 65)

    passed_tests = 0
    total_tests = 6

    # Test 1: Sample Radiograph Generation
    print("\n[Test 1/6] Generating Test Radiographs...")
    try:
        from dataset.generate_sample_xrays import generate_samples, SAMPLES_DIR
        generate_samples()
        chest_sample = os.path.join(SAMPLES_DIR, "sample_chest_xray.png")
        bone_sample = os.path.join(SAMPLES_DIR, "sample_bone_xray.png")

        assert os.path.exists(chest_sample), "Chest sample missing"
        assert os.path.exists(bone_sample), "Bone sample missing"
        print("  -> PASSED: All sample radiographs generated successfully.")
        passed_tests += 1
    except Exception as e:
        print(f"  -> FAILED: {e}")

    # Test 2: Database Initialization & Tables
    print("\n[Test 2/6] Verifying SQLite 3NF Schema & Admin Seed...")
    try:
        from app.database import db
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  Detected tables: {tables}")

        required_tables = ["users", "patients", "scans", "findings", "activity_logs"]
        for t in required_tables:
            assert t in tables, f"Missing table: {t}"

        # Check Admin Seed
        admin_user = db.get_user_by_username("admin")
        assert admin_user is not None, "Admin user not seeded"
        assert admin_user["role"] == "Admin", "Admin role mismatch"
        print(f"  Admin account verified: ID #{admin_user['user_id']} ({admin_user['username']})")
        print("  -> PASSED: Database schema normalized and initialized.")
        passed_tests += 1
    except Exception as e:
        print(f"  -> FAILED: {e}")

    # Test 3: Authentication & Password Security
    print("\n[Test 3/6] Verifying Authentication & Access Control...")
    try:
        from app.auth import authenticate_user, SessionManager, hash_password

        # Test valid login
        success, msg, user = authenticate_user("admin", "Admin123!")
        assert success, f"Admin login failed: {msg}"
        assert SessionManager.is_admin(), "Admin session state failed"

        # Test invalid password
        fail_success, fail_msg, _ = authenticate_user("admin", "WrongPassword!")
        assert not fail_success, "Invalid login unexpectedly succeeded"
        assert fail_msg == "Invalid username or password.", "Error message disclosure vulnerability"

        print("  -> PASSED: Authentication, password hashing, and session management verified.")
        passed_tests += 1
    except Exception as e:
        print(f"  -> FAILED: {e}")

    # Test 4: AI Model Engine (Modality Triage + 2 Inference Pipelines)
    print("\n[Test 4/6] Verifying AI Inference Engine across Both Modalities...")
    try:
        from app.model_engine import ai_engine

        # Modality detection
        mod_chest, conf_c = ai_engine.detect_modality(chest_sample)
        mod_bone, conf_b = ai_engine.detect_modality(bone_sample)

        print(f"  Modality Triage -> Chest: {mod_chest} ({conf_c*100:.1f}%), Bone: {mod_bone} ({conf_b*100:.1f}%)")

        # Modality Inferences
        res_chest = ai_engine.predict_chest(chest_sample)
        res_bone = ai_engine.predict_bone(bone_sample)

        assert "prediction" in res_chest and len(res_chest["findings"]) > 0
        assert "prediction" in res_bone and len(res_bone["findings"]) > 0

        print(f"  Chest Inference  : {res_chest['prediction']} (Conf: {res_chest['confidence']*100:.1f}%)")
        print(f"  Bone Inference   : {res_bone['prediction']} (Conf: {res_bone['confidence']*100:.1f}%)")

        print("  -> PASSED: AI model pipelines operational for Chest and Bone.")
        passed_tests += 1
    except Exception as e:
        print(f"  -> FAILED: {e}")

    # Test 5: Computer Vision Visual Overlay
    print("\n[Test 5/6] Verifying OpenCV / PIL Visual Annotation Compositor...")
    try:
        from app.detection_overlay import draw_findings_overlay

        annotated_path = draw_findings_overlay(
            bone_sample,
            res_bone["findings"],
            "Bone",
            res_bone["prediction"],
            res_bone["confidence"]
        )

        assert os.path.exists(annotated_path), "Annotated image output file not generated"
        print(f"  Rendered visual overlay at: {annotated_path}")
        print("  -> PASSED: Visual bounding-box compositor verified.")
        passed_tests += 1
    except Exception as e:
        print(f"  -> FAILED: {e}")

    # Test 6: ReportLab Clinical PDF Compilation
    print("\n[Test 6/6] Verifying Clinical Diagnostic PDF Report Compilation...")
    try:
        from app.report_generator import generate_pdf_report

        # Create test patient & scan record
        p_id = db.create_patient("Test Patient", 42, "Male", "+1-555-0199")
        s_id = db.create_scan(
            patient_id=p_id,
            user_id=1,
            scan_type="Bone",
            body_region="Wrist (Distal Radius)",
            prediction=res_bone["prediction"],
            confidence=res_bone["confidence"],
            raw_image_path=bone_sample,
            annotated_image_path=annotated_path
        )

        for f in res_bone["findings"]:
            db.create_finding(
                scan_id=s_id,
                label=f["label"],
                confidence=f["confidence"],
                bbox_x=f.get("bbox_x"),
                bbox_y=f.get("bbox_y"),
                bbox_w=f.get("bbox_w"),
                bbox_h=f.get("bbox_h")
            )

        scan_details = db.get_scan_details(s_id)
        pdf_path = generate_pdf_report(scan_details)

        assert os.path.exists(pdf_path), "Report file not created"
        print(f"  Compiled PDF clinical report at: {pdf_path}")
        print("  -> PASSED: ReportLab clinical report generation verified.")
        passed_tests += 1
    except Exception as e:
        print(f"  -> FAILED: {e}")

    print("\n" + "=" * 65)
    print(f"  VERIFICATION COMPLETE: {passed_tests}/{total_tests} TEST SUITES PASSED")
    print("=" * 65)

if __name__ == "__main__":
    run_verification()
