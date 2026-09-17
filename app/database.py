"""
database.py
-----------
Relational SQLite database manager for RadiVision AI.
Implements a 3NF normalized schema with foreign keys, role-based scan isolation,
and activity audit logging.
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.encryption import pacs_cipher

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
DB_PATH = os.path.join(DB_DIR, "xray_system.db")

class DatabaseManager:
    """Manages SQLite database connections and CRUD operations."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a connection with foreign key enforcement and row dict mapping."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_database(self):
        """Creates all 3NF relational tables and auto-seeds the default Admin account."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT CHECK(role IN ('Admin', 'User')) NOT NULL DEFAULT 'User',
                    phone TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Ensure phone, country, and city columns exist for existing installations
            cursor.execute("PRAGMA table_info(users);")
            u_cols = [r[1] for r in cursor.fetchall()]
            if "phone" not in u_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT;")
            if "country" not in u_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN country TEXT DEFAULT 'Pakistan';")
            if "city" not in u_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN city TEXT DEFAULT 'Rawalpindi';")

            # 2. Patients Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')) NOT NULL,
                    contact TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 3. Scans Table (incorporates user_id for multi-user isolation)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scans (
                    scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    scan_type TEXT CHECK(scan_type IN ('Chest', 'Bone')) NOT NULL,
                    body_region TEXT,
                    prediction TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    raw_image_path TEXT NOT NULL,
                    annotated_image_path TEXT,
                    scan_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
                );
            """)

            # 4. Findings Table (supports 1-to-many detections for Bone)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS findings (
                    finding_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER NOT NULL,
                    label TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    bbox_x REAL,
                    bbox_y REAL,
                    bbox_w REAL,
                    bbox_h REAL,
                    FOREIGN KEY (scan_id) REFERENCES scans(scan_id) ON DELETE CASCADE
                );
            """)

            # 5. Activity Logs Table (for administrative audit trail)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
                );
            """)

            conn.commit()

            # Seed default Admin account if no users exist
            cursor.execute("SELECT COUNT(*) FROM users;")
            if cursor.fetchone()[0] == 0:
                # Default password is 'Admin123!' hashed with bcrypt
                from app.auth import hash_password
                default_pw_hash = hash_password("Admin123!")
                cursor.execute("""
                    INSERT INTO users (full_name, username, email, password_hash, role)
                    VALUES (?, ?, ?, ?, 'Admin');
                """, ("System Administrator", "admin", "admin@radivision.ai", default_pw_hash))
                
                # Log the initialization event
                cursor.execute("""
                    INSERT INTO activity_logs (username, action, details)
                    VALUES ('SYSTEM', 'SYSTEM_INITIALIZATION', 'Database initialized and default Admin account seeded.');
                """)
                conn.commit()

    # ----------------- User Management -----------------
    def create_user(self, full_name: str, username: str, email: str, password_hash: str, role: str = 'User', phone: str = "", country: str = "Pakistan", city: str = "Rawalpindi") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (full_name, username, email, password_hash, role, phone, country, city)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (full_name.strip(), username.strip(), email.strip(), password_hash, role, phone.strip() if phone else "", country.strip() if country else "Pakistan", city.strip() if city else "Rawalpindi"))
            conn.commit()
            return cursor.lastrowid

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?;", (username.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?;", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_users(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, full_name, username, email, role, phone, country, city, is_active, created_at FROM users ORDER BY created_at DESC;")
            return [dict(row) for row in cursor.fetchall()]

    def update_user_status(self, user_id: int, is_active: bool):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_active = ? WHERE user_id = ?;", (1 if is_active else 0, user_id))
            conn.commit()

    def update_user_role(self, user_id: int, role: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET role = ? WHERE user_id = ?;", (role, user_id))
            conn.commit()

    def update_user_credentials(self, user_id: int, username: Optional[str] = None, full_name: Optional[str] = None,
                                email: Optional[str] = None, password_hash: Optional[str] = None,
                                role: Optional[str] = None, is_active: Optional[bool] = None,
                                country: Optional[str] = None, city: Optional[str] = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            updates = []
            params = []
            if username:
                updates.append("username = ?")
                params.append(username.strip())
            if full_name:
                updates.append("full_name = ?")
                params.append(full_name.strip())
            if email:
                updates.append("email = ?")
                params.append(email.strip())
            if password_hash:
                updates.append("password_hash = ?")
                params.append(password_hash)
            if role:
                updates.append("role = ?")
                params.append(role)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)
            if country:
                updates.append("country = ?")
                params.append(country.strip())
            if city:
                updates.append("city = ?")
                params.append(city.strip())
            if updates:
                params.append(user_id)
                cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?;", tuple(params))
                conn.commit()

    # ----------------- Patient Management -----------------
    def create_patient(self, name: str, age: int, gender: str, contact: str = "") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            enc_name = pacs_cipher.encrypt(name.strip())
            enc_contact = pacs_cipher.encrypt(contact.strip()) if contact else ""
            cursor.execute("""
                INSERT INTO patients (name, age, gender, contact)
                VALUES (?, ?, ?, ?);
            """, (enc_name, age, gender, enc_contact))
            conn.commit()
            return cursor.lastrowid

    def get_patient(self, patient_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients WHERE patient_id = ?;", (patient_id,))
            row = cursor.fetchone()
            if not row:
                return None
            p = dict(row)
            p["name"] = pacs_cipher.decrypt(p.get("name"))
            p["contact"] = pacs_cipher.decrypt(p.get("contact"))
            return p

    def get_all_patients(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients ORDER BY created_at DESC;")
            patients = []
            for row in cursor.fetchall():
                p = dict(row)
                p["name"] = pacs_cipher.decrypt(p.get("name"))
                p["contact"] = pacs_cipher.decrypt(p.get("contact"))
                patients.append(p)
            return patients

    # ----------------- Scan & Findings Management -----------------
    def create_scan(self, patient_id: int, user_id: int, scan_type: str, body_region: Optional[str],
                    prediction: str, confidence: float, raw_image_path: str, annotated_image_path: Optional[str] = None) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scans (patient_id, user_id, scan_type, body_region, prediction, confidence, raw_image_path, annotated_image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (patient_id, user_id, scan_type, body_region, prediction, float(confidence), raw_image_path, annotated_image_path))
            conn.commit()
            return cursor.lastrowid

    def update_scan_annotated_path(self, scan_id: int, annotated_path: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE scans SET annotated_image_path = ? WHERE scan_id = ?;", (annotated_path, scan_id))
            conn.commit()

    def create_finding(self, scan_id: int, label: str,
                       confidence: float, bbox_x: Optional[float] = None, bbox_y: Optional[float] = None,
                       bbox_w: Optional[float] = None, bbox_h: Optional[float] = None) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO findings (scan_id, label, confidence, bbox_x, bbox_y, bbox_w, bbox_h)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (scan_id, label, float(confidence), bbox_x, bbox_y, bbox_w, bbox_h))
            conn.commit()
            return cursor.lastrowid

    def get_scans(self, user_id: Optional[int] = None, limit: int = 200) -> List[Dict[str, Any]]:
        """
        Retrieves scan records joined with patient and clinician info.
        If user_id is provided, filters for that clinician's uploads.
        If user_id is None (Admin mode), returns all scans across the institution.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute("""
                    SELECT s.*, p.name AS patient_name, p.age AS patient_age, p.gender AS patient_gender,
                           u.full_name AS clinician_name, u.username AS clinician_username
                    FROM scans s
                    JOIN patients p ON s.patient_id = p.patient_id
                    JOIN users u ON s.user_id = u.user_id
                    WHERE s.user_id = ?
                    ORDER BY s.scan_date DESC
                    LIMIT ?;
                """, (user_id, limit))
            else:
                cursor.execute("""
                    SELECT s.*, p.name AS patient_name, p.age AS patient_age, p.gender AS patient_gender,
                           u.full_name AS clinician_name, u.username AS clinician_username
                    FROM scans s
                    JOIN patients p ON s.patient_id = p.patient_id
                    LEFT JOIN users u ON s.user_id = u.user_id
                    ORDER BY s.scan_date DESC
                    LIMIT ?;
                """, (limit,))
            rows = [dict(row) for row in cursor.fetchall()]
            for r in rows:
                if "patient_name" in r:
                    r["patient_name"] = pacs_cipher.decrypt(r["patient_name"])
            return rows

    def get_scan_details(self, scan_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, p.name AS patient_name, p.age AS patient_age, p.gender AS patient_gender, p.contact AS patient_contact,
                       u.full_name AS clinician_name, u.email AS clinician_email
                FROM scans s
                JOIN patients p ON s.patient_id = p.patient_id
                LEFT JOIN users u ON s.user_id = u.user_id
                WHERE s.scan_id = ?;
            """, (scan_id,))
            row = cursor.fetchone()
            if not row:
                return None
            scan_dict = dict(row)
            scan_dict["patient_name"] = pacs_cipher.decrypt(scan_dict.get("patient_name"))
            scan_dict["patient_contact"] = pacs_cipher.decrypt(scan_dict.get("patient_contact"))
            cursor.execute("SELECT * FROM findings WHERE scan_id = ?;", (scan_id,))
            scan_dict["findings"] = [dict(f) for f in cursor.fetchall()]
            return scan_dict

    # ----------------- Activity Audit Logs -----------------
    def log_activity(self, user_id: Optional[int], username: str, action: str, details: str = ""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO activity_logs (user_id, username, action, details)
                VALUES (?, ?, ?, ?);
            """, (user_id, username, action, details))
            conn.commit()

    def get_activity_logs(self, limit: int = 200) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM activity_logs
                ORDER BY timestamp DESC
                LIMIT ?;
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # ----------------- Dashboard Statistics -----------------
    def get_dashboard_stats(self, user_id: Optional[int] = None) -> Dict[str, int]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            user_clause = "WHERE user_id = ?" if user_id is not None else ""
            params = (user_id,) if user_id is not None else ()

            cursor.execute(f"SELECT COUNT(*) FROM scans {user_clause};", params)
            total_scans = cursor.fetchone()[0]

            abn_where = "WHERE " + ("user_id = ? AND " if user_id is not None else "") + "(prediction LIKE '%Abnormal%' OR prediction LIKE '%Pneumonia%' OR (prediction LIKE '%Fracture%' AND prediction NOT LIKE '%No Fracture%'))"
            cursor.execute(f"SELECT COUNT(*) FROM scans {abn_where};", params)
            abnormal_scans = cursor.fetchone()[0]

            normal_scans = total_scans - abnormal_scans

            cursor.execute("SELECT COUNT(*) FROM patients;")
            total_patients = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users;")
            total_users = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM activity_logs WHERE action IN ('PDF_EXPORTED', 'REPORT_GENERATED');")
            reports_exported = cursor.fetchone()[0]
            if reports_exported == 0 and total_scans > 0:
                reports_exported = total_scans

            return {
                "total_scans": total_scans,
                "abnormal_scans": abnormal_scans,
                "normal_scans": normal_scans,
                "total_patients": total_patients,
                "total_users": total_users,
                "reports_exported": reports_exported,
            }

    def get_recent_scans_summary(self, user_id: Optional[int] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves formatted recent activity records for the dashboard."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT s.scan_id, s.scan_type, s.prediction, s.confidence, s.scan_date,
                       p.name AS patient_name, u.full_name AS clinician_name
                FROM scans s
                JOIN patients p ON s.patient_id = p.patient_id
                LEFT JOIN users u ON s.user_id = u.user_id
            """
            params = []
            if user_id is not None:
                query += " WHERE s.user_id = ?"
                params.append(user_id)
            query += " ORDER BY s.scan_date DESC LIMIT ?;"
            rows = [dict(row) for row in cursor.fetchall()]
            for r in rows:
                if "patient_name" in r:
                    r["patient_name"] = pacs_cipher.decrypt(r["patient_name"])
            return rows

# Global singleton instance
db = DatabaseManager()

def init_db():
    """Initializes the database schema and seeds default data."""
    db.init_database()

def save_scan(patient_name: str, patient_age: int, patient_gender: str, scan_type: str,
              image_path: str, prediction: str, confidence: float, body_region: Optional[str] = None,
              annotated_image_path: Optional[str] = None, patient_national_id: Optional[str] = None,
              user_id: int = 1) -> int:
    """Convenience helper to register a patient and scan record."""
    patient_id = db.create_patient(patient_name, patient_age, patient_gender, contact=patient_national_id or "")
    scan_id = db.create_scan(patient_id=patient_id, user_id=user_id, scan_type=scan_type,
                             body_region=body_region, prediction=prediction, confidence=confidence,
                             raw_image_path=image_path, annotated_image_path=annotated_image_path)
    return scan_id

def save_finding(scan_id: int, label: str, confidence: float,
                 bbox_x: Optional[float] = None, bbox_y: Optional[float] = None,
                 bbox_w: Optional[float] = None, bbox_h: Optional[float] = None,
                 tooth_number: Optional[str] = None) -> int:
    """Convenience helper to record a detected bounding box finding."""
    return db.create_finding(scan_id, label, confidence, bbox_x, bbox_y, bbox_w, bbox_h)

def get_all_scans(limit: int = 200) -> List[Dict[str, Any]]:
    """Retrieves all past scans across all patients."""
    return db.get_scans(user_id=None, limit=limit)

def get_scan_by_id(scan_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves full scan details including findings."""
    return db.get_scan_details(scan_id)

