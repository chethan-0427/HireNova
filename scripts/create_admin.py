"""
HireNova - Administrator Creation Script
Interactive CLI utility to register a new administrator account.

Usage:
    python scripts/create_admin.py
"""

import os
import sys
import sqlite3
from getpass import getpass
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import get_db_connection, create_tables


def create_admin():
    print("=" * 50)
    print("  HireNova - Create Administrator Account")
    print("=" * 50)

    create_tables()

    name = input("Enter admin name: ").strip()
    email = input("Enter admin email: ").strip().lower()
    password = getpass("Enter admin password: ")

    if not name or not email or not password:
        print("[Error] Name, email, and password are required.")
        return

    if "@" not in email or "." not in email:
        print("[Error] Please enter a valid email address.")
        return

    if len(password) < 8:
        print("[Error] Password must contain at least 8 characters.")
        return

    conn = get_db_connection()

    try:
        conn.execute(
            """
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, 'admin')
            """,
            (name, email, generate_password_hash(password))
        )
        conn.commit()
        print(f"[Success] Administrator account created for '{email}'!")

    except sqlite3.IntegrityError:
        print(f"[Error] An account with email '{email}' already exists.")

    finally:
        conn.close()


if __name__ == "__main__":
    create_admin()

