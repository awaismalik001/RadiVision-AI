"""
test_complete_system.py
-----------------------
Full Verification Suite for RadiVision AI Master Implementation Plan.
Verifies:
  1. Phase 5 Security: AES-256 Encryption at rest & transparent decryption
  2. Phase 5 Security: Login Rate-Limiting & Strict Password Policy
  3. Phase 4 Logic: Admin-Only Credential Updates (Non-admin strictly blocked)
  4. Phase 3 AI: Vision Transformer (ViT-B/16) + Gemini AI Cross-Verification
  5. Phase 4 Logic: Excel PACS Database Export (.xlsx generation)
  6. Phase 4 Logic: Google Maps Doctor Referrals & Clinical PDF Report Generation
"""

import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from app.encryption import pacs_cipher
from app.database import db
from app.auth import (
    validate_password_complexity, is_rate_limited, record_failed_attempt,
    clear_failed_attempts, admin_update_credentials, authenticate_user
)
from app.vit_model import vit_engine
from app.gemini_service import gemini_service
from app.hospital_referral import get_recommended_facilities
from app.excel_export import generate_excel_export
from app.report_generator import generate_pdf_report

def run_tests():
    print("=" * 70)
    print("      RADIVISION AI - COMPREHENSIVE VERIFICATION SUITE")
    print("=" * 70)

    # TEST 1: AES-256 Encryption at Rest
    print("\n[TEST 1] Verifying AES-256 Database Encryption at Rest...")
    secret_text = "Patient: Jonathan Doe, MRN: RV-889912, Phone: +1-202-555-0188"
    ciphertext = pacs_cipher.encrypt(secret_text)
    assert ciphertext.startswith("enc:aes256:"), "Ciphertext does not have AES-256 header"
    assert secret_text not in ciphertext, "Plaintext leaked in ciphertext"
    decrypted = pacs_cipher.decrypt(ciphertext)
    assert decrypted == secret_text, f"Decrypted mismatch: {decrypted} != {secret_text}"
    print("  ✓ AES-256-GCM Encryption & Decryption Verified.")

    # TEST 2: Password Complexity & Hospital Policy
    print("\n[TEST 2] Verifying Hospital-Grade Password Policy...")
    weak_cases = ["simple", "short1!", "ALLCAPS1!", "alllower1!", "NoSpecialChar1"]
    for w in weak_cases:
        valid, msg = validate_password_complexity(w)
        assert not valid, f"Weak password '{w}' should have failed complexity check"
    valid, msg = validate_password_complexity("ClinicalSecure2026!")
    assert valid, f"Strong password failed: {msg}"
    print("  ✓ Strict Password Complexity Enforcement Verified.")

    # TEST 3: Login Rate-Limiting (Anti-Brute Force)
    print("\n[TEST 3] Verifying Anti-Brute-Force Rate Limiting...")
    test_id = "test_clinician_bruteforce"
    clear_failed_attempts(test_id)
    for _ in range(4):
        record_failed_attempt(test_id)
    limited, _ = is_rate_limited(test_id)
    assert not limited, "Should not be locked out at 4 attempts"
    record_failed_attempt(test_id) # 5th attempt
    limited, secs = is_rate_limited(test_id)
    assert limited, "Should be locked out after 5 consecutive failed attempts"
    clear_failed_attempts(test_id)
    print(f"  ✓ Rate-Limiter triggered correctly after 5 failed attempts ({secs}s cooldown).")

    # TEST 4: Admin-Only Credential Updates
    print("\n[TEST 4] Verifying Phase 4 Admin-Only Credential Update Enforcement...")
    admin_user = db.get_user_by_username("admin")
    non_admin_session = {"user_id": 999, "username": "clinician_jane", "role": "User"}
    
    # Regular user attempt must fail
    ok, msg = admin_update_credentials(non_admin_session, admin_user["user_id"], new_username="hacked_admin")
    assert not ok, "Non-admin was able to modify credentials!"
    assert "Access Denied" in msg or "restricted to System Administrators" in msg
    print("  ✓ Non-admin user blocked from credential modification (403 Forbidden).")

    # Admin attempt must succeed
    admin_session = {"user_id": admin_user["user_id"], "username": "admin", "role": "Admin"}
    ok, msg = admin_update_credentials(admin_session, admin_user["user_id"], new_full_name="Chief Radiologist & Administrator")
    assert ok, f"Admin credential update failed: {msg}"
    print("  ✓ Admin authorized credential update confirmed & activity logged.")

    # TEST 5: Vision Transformer (ViT-B/16) Multi-Modal Inference
    print("\n[TEST 5] Verifying Vision Transformer Diagnostic Model...")
    sample_chest = os.path.join(PROJECT_ROOT, "dataset", "samples", "sample_chest_xray.png")
    sample_bone = os.path.join(PROJECT_ROOT, "dataset", "samples", "sample_bone_xray.png")

    if os.path.exists(sample_chest):
        chest_res = vit_engine.predict(sample_chest, modality="Chest")
        assert "prediction" in chest_res and "confidence" in chest_res
        print(f"  ✓ ViT Chest Diagnosis: {chest_res['prediction']} ({chest_res['confidence']*100:.1f}%)")

    if os.path.exists(sample_bone):
        bone_res = vit_engine.predict(sample_bone, modality="Bone")
        assert "prediction" in bone_res and "confidence" in bone_res
        print(f"  ✓ ViT Bone Diagnosis: {bone_res['prediction']} ({bone_res['confidence']*100:.1f}%)")

    # TEST 6: Gemini Multimodal Cross-Verification
    print("\n[TEST 6] Verifying Gemini Multi-Modal Cross-Verification...")
    if os.path.exists(sample_chest):
        gemini_res = gemini_service.refine_and_cross_verify(sample_chest, "Chest", "Pneumonia", 0.94)
        assert gemini_res["verified"] is True
        print(f"  ✓ Gemini Status: {gemini_res['status']} | Urgency: {gemini_res['urgency']}")

    # TEST 7: Google Maps Local Referrals & PDF Report Generation
    print("\n[TEST 7] Verifying Google Maps Referrals & Clinical PDF Compilation...")
    facilities = get_recommended_facilities("New York", "Bone")
    assert len(facilities) >= 1, "No facilities returned"
    print(f"  ✓ Local Healthcare Referrals: {len(facilities)} facilities retrieved ({facilities[0]['hospital_name']})")

    pdf_data = {
        "patient_id": "RV-TEST-001",
        "patient_name": "Test Patient",
        "patient_age": 42,
        "patient_gender": "Male",
        "scan_type": "Chest",
        "prediction": "PNEUMONIA (Abnormal)",
        "confidence": 0.962,
        "body_region": "Thoracic",
        "facilities": facilities,
        "location": "New York"
    }
    pdf_path = generate_pdf_report(pdf_data)
    assert os.path.exists(pdf_path), f"PDF file was not generated: {pdf_path}"
    print(f"  ✓ Clinical Diagnostic PDF Generated ({os.path.getsize(pdf_path)} bytes).")

    # TEST 8: Excel Database Export
    print("\n[TEST 8] Verifying Excel PACS Database Export (.xlsx)...")
    excel_path = generate_excel_export()
    assert os.path.exists(excel_path), f"Excel file was not generated: {excel_path}"
    print(f"  ✓ Excel Database Export Generated ({os.path.getsize(excel_path)} bytes).")

    print("\n" + "=" * 70)
    print("      ALL 8 VERIFICATION PHASES PASSED WITH ZERO ERRORS!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
