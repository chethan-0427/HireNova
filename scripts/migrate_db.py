"""
HireNova - Database Migration Script
Safely applies schema adjustments (such as application uniqueness constraint).

Usage:
    python scripts/migrate_db.py
"""

import os
import sys
import sqlite3

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import get_db_connection


def run_migration():
    print("[Migration] Checking and migrating applications schema...")
    conn = get_db_connection()

    try:
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("BEGIN")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE RESTRICT,
                UNIQUE(user_id, job_id)
            )
        """)

        # Copy existing data if applications table exists
        existing_table = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='applications'"
        ).fetchone()

        if existing_table:
            conn.execute("""
                INSERT OR IGNORE INTO applications_new (id, user_id, job_id, status)
                SELECT id, user_id, job_id, status
                FROM applications
            """)
            conn.execute("DROP TABLE applications")

        conn.execute("ALTER TABLE applications_new RENAME TO applications")
        conn.commit()
        print("[Migration] Applications table updated successfully!")

    except Exception as e:
        conn.rollback()
        print(f"[Migration Error] Migration failed: {e}")

    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()


if __name__ == "__main__":
    run_migration()
