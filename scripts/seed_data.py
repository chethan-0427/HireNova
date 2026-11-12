"""
HireNova - Seed Demo Data Script
Populates the database with realistic sample jobs, test users, and applications.
Useful for grading, demonstrations, testing, and UI evaluation.

Usage:
    python scripts/seed_data.py
"""

import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import get_db_connection, create_tables


SAMPLE_USERS = [
    {
        "name": "HireNova Administrator",
        "email": "admin@hirenova.com",
        "password": "adminpassword123",
        "role": "admin"
    },
    {
        "name": "Jane Jobseeker",
        "email": "jane@example.com",
        "password": "jobseekerpass123",
        "role": "jobseeker"
    },
    {
        "name": "Alex Applicant",
        "email": "alex@example.com",
        "password": "jobseekerpass123",
        "role": "jobseeker"
    }
]

SAMPLE_JOBS = [
    {
        "title": "Full Stack Python Developer",
        "company": "TechNova Solutions",
        "location": "Bangalore, India (Hybrid)",
        "salary": "INR 8,50,000 - 12,00,000 / year",
        "description": "Looking for a Full Stack Python Developer with hands-on experience in Flask/Django, SQLite/PostgreSQL, REST APIs, and modern frontend technologies (HTML5, Bootstrap, JavaScript). You will design scalable web applications and collaborate with cross-functional teams."
    },
    {
        "title": "Frontend UI/UX Engineer",
        "company": "CreativePulse Studios",
        "location": "Remote / Bengaluru",
        "salary": "INR 6,00,000 - 9,50,000 / year",
        "description": "We are seeking a Frontend UI/UX Engineer proficient in responsive web design, CSS3, modern JavaScript, and UI frameworks. You will turn wireframes into intuitive, accessible user interfaces."
    },
    {
        "title": "Junior Backend Engineer",
        "company": "CloudScale Systems",
        "location": "Hyderabad, India",
        "salary": "INR 5,00,000 - 7,50,000 / year",
        "description": "Join our backend infrastructure team to build robust APIs, maintain relational database schemas, and integrate microservices. Knowledge of Python, SQLite/MySQL, and Git is preferred."
    },
    {
        "title": "Data Analyst & Reporting Specialist",
        "company": "InsightForge Analytics",
        "location": "Mumbai, India (Remote)",
        "salary": "INR 7,00,000 - 10,00,000 / year",
        "description": "Seeking an analytical thinker to extract actionable insights from business metrics. Proficiency in SQL queries, Python data analysis, and dashboard visualization is required."
    },
    {
        "title": "DevOps & Cloud Associate",
        "company": "InfraStack Networks",
        "location": "Pune, India",
        "salary": "INR 6,50,000 - 9,00,000 / year",
        "description": "Responsible for CI/CD pipelines, automated testing workflows, cloud server monitoring, and environment configuration management."
    }
]


def seed():
    print("=" * 60)
    print("  HireNova - Seeding Realistic Demo Data")
    print("=" * 60)

    create_tables()
    conn = get_db_connection()

    try:
        # Seed users
        user_ids = {}
        for u in SAMPLE_USERS:
            existing = conn.execute(
                "SELECT id FROM users WHERE email = ?",
                (u["email"],)
            ).fetchone()

            if not existing:
                cursor = conn.execute(
                    """
                    INSERT INTO users (name, email, password, role)
                    VALUES (?, ?, ?, ?)
                    """,
                    (u["name"], u["email"], generate_password_hash(u["password"]), u["role"])
                )
                user_ids[u["email"]] = cursor.lastrowid
                print(f"[+] Created user: {u['name']} ({u['email']}) [{u['role']}]")
            else:
                user_ids[u["email"]] = existing["id"]
                print(f"[-] User already exists: {u['email']}")

        # Seed jobs
        job_ids = []
        for j in SAMPLE_JOBS:
            existing = conn.execute(
                "SELECT id FROM jobs WHERE title = ? AND company = ?",
                (j["title"], j["company"])
            ).fetchone()

            if not existing:
                cursor = conn.execute(
                    """
                    INSERT INTO jobs (title, company, location, salary, description)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (j["title"], j["company"], j["location"], j["salary"], j["description"])
                )
                job_ids.append(cursor.lastrowid)
                print(f"[+] Added job posting: {j['title']} @ {j['company']}")
            else:
                job_ids.append(existing["id"])
                print(f"[-] Job posting already exists: {j['title']}")

        # Seed sample applications
        if user_ids.get("jane@example.com") and len(job_ids) >= 3:
            jane_id = user_ids["jane@example.com"]
            sample_apps = [
                (jane_id, job_ids[0], "Shortlisted"),
                (jane_id, job_ids[1], "Pending"),
                (jane_id, job_ids[2], "Rejected")
            ]
            for uid, jid, status in sample_apps:
                try:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO applications (user_id, job_id, status)
                        VALUES (?, ?, ?)
                        """,
                        (uid, jid, status)
                    )
                except sqlite3.Error:
                    pass

        conn.commit()
        print("\n[Done] Database seeded successfully!")
        print("\nDemo Credentials:")
        print("  Administrator: admin@hirenova.com  /  adminpassword123")
        print("  Jobseeker:     jane@example.com    /  jobseekerpass123")
        print("=" * 60)

    finally:
        conn.close()


if __name__ == "__main__":
    seed()
