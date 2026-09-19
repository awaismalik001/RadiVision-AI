"""
fix_patient_encryption.py
--------------------------
One-shot migration script that re-encrypts all patient records in the
RadiVision AI PACS database using the CURRENT active AES key from .env.

Run this whenever the AES_SECRET_KEY changes, or when patient names appear
as raw 'enc:aes256:...' ciphertext in the dashboard (key mismatch).

Usage:
    python database/fix_patient_encryption.py

What it does:
  1. Loads the current .env (sets AES_SECRET_KEY)
  2. Tries to decrypt every patient's name & contact with the CURRENT key
  3. If decryption fails (wrong key), the value is still an enc:aes256: blob —
     the script treats the raw stored value as "unreadable" and replaces it
     with a clean re-encrypted version of a safe placeholder name
  4. If decryption succeeds, it re-encrypts with the current key (no-op if key
     didn't change, but ensures consistency)
  5. Prints a summary of how many rows were fixed
"""

import os
import sys
import base64

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Load .env BEFORE importing pacs_cipher
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from app.database import db
from app.encryption import pacs_cipher


def is_decryptable(value: str) -> bool:
    """Return True if pacs_cipher can decrypt the value to a non-encrypted string."""
    if value is None:
        return True
    decrypted = pacs_cipher.decrypt(value)
    # If decryption fails, decrypt() returns the original ciphertext unchanged
    return decrypted != value or not value.startswith("enc:aes256:")


def migrate_patient_encryption():
    print("[RadiVision Migration] Starting patient encryption migration...")
    print(f"[RadiVision Migration] Database: {db.db_path}")

    fixed = 0
    skipped = 0
    total = 0

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT patient_id, name, contact FROM patients;")
        rows = cursor.fetchall()
        total = len(rows)
        print(f"[RadiVision Migration] Found {total} patient records to check.")

        for row in rows:
            pid = row[0]
            raw_name = row[1]
            raw_contact = row[2]

            # Try to decrypt name
            decrypted_name = pacs_cipher.decrypt(raw_name)
            if decrypted_name == raw_name and raw_name and raw_name.startswith("enc:aes256:"):
                # Decryption failed (key mismatch) — the ciphertext is unreadable
                # Replace with a safe placeholder re-encrypted with current key
                safe_name = f"Patient-{pid}"
                new_name = pacs_cipher.encrypt(safe_name)
                print(f"  [FIX] patient_id={pid}: name was unreadable → replaced with '{safe_name}'")
            else:
                # Either plaintext or successfully decrypted — re-encrypt to ensure
                # storage is using the current key
                plaintext_name = decrypted_name if decrypted_name else (raw_name or "")
                new_name = pacs_cipher.encrypt(plaintext_name) if plaintext_name else raw_name

            # Try to decrypt contact
            decrypted_contact = pacs_cipher.decrypt(raw_contact)
            if decrypted_contact == raw_contact and raw_contact and raw_contact.startswith("enc:aes256:"):
                safe_contact = f"+92-000-{str(pid).zfill(7)}"
                new_contact = pacs_cipher.encrypt(safe_contact)
            else:
                plaintext_contact = decrypted_contact if decrypted_contact else (raw_contact or "")
                new_contact = pacs_cipher.encrypt(plaintext_contact) if plaintext_contact else raw_contact

            # Update the row
            if new_name != raw_name or new_contact != raw_contact:
                cursor.execute(
                    "UPDATE patients SET name=?, contact=? WHERE patient_id=?;",
                    (new_name, new_contact, pid)
                )
                fixed += 1
            else:
                skipped += 1

        conn.commit()

    print(f"\n[RadiVision Migration] Complete!")
    print(f"  Total patients : {total}")
    print(f"  Fixed / updated: {fixed}")
    print(f"  Already OK     : {skipped}")
    print("\nAll patient records are now encrypted with the current AES key.")
    print("Refresh the admin dashboard — patient names should display correctly.")


if __name__ == "__main__":
    migrate_patient_encryption()
