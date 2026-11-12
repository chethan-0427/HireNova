"""
HireNova Database Module
Handles SQLite database connection, table creation, and schema integrity.
"""

import os
import sqlite3

# Resolve project root directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_default_db_path():
    """Retrieve database path dynamically from environment or default to project root."""
    return os.environ.get("HIRENOVA_DB_PATH", os.path.join(BASE_DIR, "hirenova.db"))


def get_db_connection(db_path=None):
    """
    Establish and return a connection to the SQLite database.
    Enforces foreign key constraints and row factory for dict-like access.
    """
    target_path = db_path or get_default_db_path()
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(db_path=None):
    """
    Initialize all database tables if they do not already exist.
    Tables: users, jobs, applications, password_resets.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'jobseeker'
        )
    """)

    # Jobs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL,
            salary TEXT
        )
    """)

    # Applications Table (enforcing unique user_id + job_id)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE RESTRICT,
            UNIQUE(user_id, job_id)
        )
    """)

    # Password Resets Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expires_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    db_file = get_default_db_path()
    print(f"Initializing database at: {db_file}")
    create_tables(db_file)
    print("Database tables initialized successfully.")
