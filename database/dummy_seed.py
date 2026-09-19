"""
dummy_seed.py
------------
Seeds a clean, isolated SQLite PACS database with synthetic, de-identified demo data
for developers, evaluators, and automated test pipelines.
Guarantees NO Personally Identifiable Information (PII) or protected health records.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.database import db
from app.auth import hash_password

def seed_demo_environment():
    print('[RadiVision AI] Initializing clean database schema...')
    db.init_database()

    with db.get_connection() as conn:
        c = conn.cursor()

        # 1. Seed Master Admin (awaismalik001) with dummy official contact
        c.execute("SELECT user_id FROM users WHERE LOWER(username) = 'awaismalik001';")
        admin_row = c.fetchone()
        if not admin_row:
            admin_pw_hash = hash_password('Admin123!')
            c.execute("""
                INSERT INTO users (full_name, username, email, password_hash, role, phone, country, city)
                VALUES (?, ?, ?, ?, 'Admin', ?, 'Pakistan', 'Rawalpindi');
            """, ('Awais Malik', 'awaismalik001', 'admin@radivision.ai', admin_pw_hash, '+92-300-0000000'))
            print('[Seed] Created Master Administrator: awaismalik001 / Admin123!')

        # 2. Seed Demo Clinician User
        c.execute("SELECT user_id FROM users WHERE LOWER(username) = 'demo_clinician' OR email = 'sarah.jenkins@radivision.ai';")
        if not c.fetchone():
            user_pw_hash = hash_password('Password123!')
            c.execute("""
                INSERT INTO users (full_name, username, email, password_hash, role, phone, country, city)
                VALUES (?, ?, ?, ?, 'User', ?, 'Pakistan', 'Rawalpindi');
            """, ('Dr. Sarah Jenkins', 'demo_clinician', 'sarah.jenkins@radivision.ai', user_pw_hash, '+92-300-1111111'))
            print('[Seed] Created Demo Clinician: demo_clinician / Password123!')

        conn.commit()

    print('[RadiVision AI] Synthetic demo environment ready with 100% de-identified dummy records.')

if __name__ == '__main__':
    seed_demo_environment()
