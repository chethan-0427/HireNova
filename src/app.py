"""
HireNova - Online Job Portal
Main Flask Application and REST API Controllers
"""

import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from flask import Flask, request, jsonify, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash

try:
    from src.database import create_tables, get_db_connection
except ImportError:
    from database import create_tables, get_db_connection

# Initialize Flask application with explicit template and static paths
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

app.secret_key = os.environ.get("SECRET_KEY", "hirenova-secret-key-development-2026")

# Initialize database schema on startup
create_tables()


# ============================================================================
# Page Routes
# ============================================================================

@app.route("/")
def home():
    """Render the main single-page application dashboard."""
    return render_template("home.html")


# ============================================================================
# Authentication APIs
# ============================================================================

@app.route("/api/register", methods=["POST"])
def register():
    """Register a new jobseeker user."""
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    if "@" not in email or "." not in email:
        return jsonify({"message": "Invalid email address"}), 400

    if len(password) < 8:
        return jsonify({"message": "Password must contain at least 8 characters"}), 400

    hashed_password = generate_password_hash(password)
    conn = get_db_connection()

    try:
        conn.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
            """,
            (name, email, hashed_password)
        )
        conn.commit()
        return jsonify({"message": "Registration successful!"}), 201

    except Exception as error:
        if "UNIQUE constraint failed" in str(error):
            return jsonify({"message": "Email already registered"}), 409
        return jsonify({"message": "Registration failed"}), 500

    finally:
        conn.close()


@app.route("/api/login", methods=["POST"])
def login():
    """Authenticate user credentials and establish session."""
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    conn = get_db_connection()

    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_role"] = user["role"]

            return jsonify({
                "message": "Login successful!",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "role": user["role"]
                }
            }), 200

        return jsonify({"message": "Invalid email or password"}), 401

    finally:
        conn.close()


@app.route("/api/current-user", methods=["GET"])
def current_user():
    """Retrieve session details for the currently authenticated user."""
    if "user_id" not in session:
        return jsonify({"logged_in": False}), 200

    conn = get_db_connection()

    try:
        user = conn.execute(
            "SELECT id, name, email, role FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()

        if not user:
            session.clear()
            return jsonify({"logged_in": False}), 200

        return jsonify({
            "logged_in": True,
            "user": dict(user)
        }), 200

    finally:
        conn.close()


@app.route("/api/logout", methods=["POST"])
def logout():
    """Clear active user session."""
    session.clear()
    return jsonify({"message": "Logout successful!"}), 200


# ============================================================================
# Job Listings APIs
# ============================================================================

@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    """Retrieve available job postings with optional search & location filters."""
    search = request.args.get("search", "").strip()
    location = request.args.get("location", "").strip()

    conn = get_db_connection()

    try:
        query = "SELECT * FROM jobs WHERE 1=1"
        params = []

        if search:
            query += """
                AND (
                    title LIKE ?
                    OR company LIKE ?
                    OR description LIKE ?
                )
            """
            keyword = f"%{search}%"
            params.extend([keyword, keyword, keyword])

        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")

        query += " ORDER BY id DESC"

        jobs = conn.execute(query, params).fetchall()
        return jsonify([dict(job) for job in jobs]), 200

    finally:
        conn.close()


@app.route("/api/jobs", methods=["POST"])
def add_job():
    """Create a new job posting (Admin role required)."""
    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session.get("user_role") != "admin":
        return jsonify({"message": "Admin access required"}), 403

    data = request.get_json(silent=True) or {}

    title = data.get("title", "").strip()
    company = data.get("company", "").strip()
    location = data.get("location", "").strip()
    description = data.get("description", "").strip()
    salary = data.get("salary", "").strip()

    if not title or not company or not location or not description:
        return jsonify({"message": "All required fields must be filled"}), 400

    conn = get_db_connection()

    try:
        conn.execute(
            """
            INSERT INTO jobs (title, company, location, description, salary)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, company, location, description, salary)
        )
        conn.commit()
        return jsonify({"message": "Job added successfully!"}), 201

    finally:
        conn.close()


@app.route("/api/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):
    """Retrieve details for a specific job posting."""
    conn = get_db_connection()

    try:
        job = conn.execute(
            "SELECT * FROM jobs WHERE id = ?",
            (job_id,)
        ).fetchone()

        if job is None:
            return jsonify({"message": "Job not found"}), 404

        return jsonify(dict(job)), 200

    finally:
        conn.close()


# ============================================================================
# Job Application APIs
# ============================================================================

@app.route("/api/jobs/<int:job_id>/apply", methods=["POST"])
def apply_job(job_id):
    """Submit an application for a specific job opportunity."""
    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    conn = get_db_connection()

    try:
        # Check whether job exists
        job = conn.execute(
            "SELECT id FROM jobs WHERE id = ?",
            (job_id,)
        ).fetchone()

        if job is None:
            return jsonify({"message": "Job not found"}), 404

        # Check duplicate application
        existing = conn.execute(
            """
            SELECT id FROM applications
            WHERE user_id = ? AND job_id = ?
            """,
            (session["user_id"], job_id)
        ).fetchone()

        if existing:
            return jsonify({"message": "You have already applied for this job"}), 409

        # Save application
        try:
            conn.execute(
                """
                INSERT INTO applications (user_id, job_id)
                VALUES (?, ?)
                """,
                (session["user_id"], job_id)
            )
            conn.commit()

        except sqlite3.IntegrityError:
            return jsonify({"message": "You have already applied for this job"}), 409

        return jsonify({"message": "Application submitted successfully!"}), 201

    finally:
        conn.close()


@app.route("/api/my-applications", methods=["GET"])
def my_applications():
    """Retrieve all job applications submitted by the logged-in jobseeker."""
    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    conn = get_db_connection()

    try:
        applications = conn.execute(
            """
            SELECT
                applications.id AS application_id,
                jobs.title,
                jobs.company,
                jobs.location,
                applications.status
            FROM applications
            JOIN jobs ON applications.job_id = jobs.id
            WHERE applications.user_id = ?
            ORDER BY applications.id DESC
            """,
            (session["user_id"],)
        ).fetchall()

        return jsonify([dict(application) for application in applications]), 200

    finally:
        conn.close()


# ============================================================================
# Admin Management APIs
# ============================================================================

@app.route("/api/admin/applications", methods=["GET"])
def admin_applications():
    """Retrieve all received applications across all jobs (Admin role required)."""
    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session.get("user_role") != "admin":
        return jsonify({"message": "Admin access required"}), 403

    conn = get_db_connection()

    try:
        applications = conn.execute(
            """
            SELECT
                applications.id AS application_id,
                users.name AS applicant_name,
                users.email AS applicant_email,
                jobs.title AS job_title,
                jobs.company,
                applications.status
            FROM applications
            JOIN users ON applications.user_id = users.id
            JOIN jobs ON applications.job_id = jobs.id
            ORDER BY applications.id DESC
            """
        ).fetchall()

        return jsonify([dict(application) for application in applications]), 200

    finally:
        conn.close()


@app.route("/api/admin/applications/<int:application_id>", methods=["PUT"])
def update_application_status(application_id):
    """Update review status of an application: Pending, Shortlisted, Rejected."""
    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session.get("user_role") != "admin":
        return jsonify({"message": "Admin access required"}), 403

    data = request.get_json(silent=True) or {}
    status = data.get("status", "").strip()

    if status not in ["Pending", "Shortlisted", "Rejected"]:
        return jsonify({"message": "Invalid application status"}), 400

    conn = get_db_connection()

    try:
        application = conn.execute(
            "SELECT id FROM applications WHERE id = ?",
            (application_id,)
        ).fetchone()

        if application is None:
            return jsonify({"message": "Application not found"}), 404

        conn.execute(
            "UPDATE applications SET status = ? WHERE id = ?",
            (status, application_id)
        )
        conn.commit()

        return jsonify({
            "message": "Application status updated successfully!",
            "status": status
        }), 200

    finally:
        conn.close()


@app.route("/api/admin/jobs/<int:job_id>", methods=["PUT"])
def update_job(job_id):
    """Update details of an existing job posting (Admin role required)."""
    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session.get("user_role") != "admin":
        return jsonify({"message": "Admin access required"}), 403

    data = request.get_json(silent=True) or {}

    title = data.get("title", "").strip()
    company = data.get("company", "").strip()
    location = data.get("location", "").strip()
    description = data.get("description", "").strip()
    salary = data.get("salary", "").strip()

    if not title or not company or not location or not description:
        return jsonify({"message": "Please provide all required job details"}), 400

    conn = get_db_connection()

    try:
        job = conn.execute(
            "SELECT id FROM jobs WHERE id = ?",
            (job_id,)
        ).fetchone()

        if job is None:
            return jsonify({"message": "Job not found"}), 404

        conn.execute(
            """
            UPDATE jobs
            SET title = ?, company = ?, location = ?,
                description = ?, salary = ?
            WHERE id = ?
            """,
            (title, company, location, description, salary, job_id)
        )
        conn.commit()

        return jsonify({"message": "Job updated successfully!"}), 200

    finally:
        conn.close()


@app.route("/api/admin/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):
    """Delete a job posting if no applications are attached (Admin role required)."""
    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session.get("user_role") != "admin":
        return jsonify({"message": "Admin access required"}), 403

    conn = get_db_connection()

    try:
        job = conn.execute(
            "SELECT id FROM jobs WHERE id = ?",
            (job_id,)
        ).fetchone()

        if job is None:
            return jsonify({"message": "Job not found"}), 404

        applications = conn.execute(
            "SELECT id FROM applications WHERE job_id = ?",
            (job_id,)
        ).fetchone()

        if applications:
            return jsonify({"message": "Cannot delete job because applications exist"}), 409

        conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        conn.commit()

        return jsonify({"message": "Job deleted successfully!"}), 200

    finally:
        conn.close()


# ============================================================================
# Password Recovery APIs
# ============================================================================

@app.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    """Generate a temporary 15-minute password reset token for a user account."""
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"message": "Email is required"}), 400

    conn = get_db_connection()

    try:
        user = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if user:
            token = secrets.token_urlsafe(32)
            expires_at = (
                datetime.now(timezone.utc) + timedelta(minutes=15)
            ).isoformat()

            conn.execute(
                "DELETE FROM password_resets WHERE user_id = ?",
                (user["id"],)
            )

            conn.execute(
                """
                INSERT INTO password_resets (user_id, token, expires_at)
                VALUES (?, ?, ?)
                """,
                (user["id"], token, expires_at)
            )
            conn.commit()

            # Development/Testing environment log:
            print(f"[Password Reset] Token for {email}: {token}")

        return jsonify({
            "message": "If the account exists, a reset link will be generated."
        }), 200

    finally:
        conn.close()


@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    """Verify reset token and update user password."""
    data = request.get_json(silent=True) or {}

    token = data.get("token", "").strip()
    new_password = data.get("new_password", "")

    if not token or not new_password:
        return jsonify({"message": "Token and new password are required"}), 400

    if len(new_password) < 8:
        return jsonify({"message": "Password must contain at least 8 characters"}), 400

    conn = get_db_connection()

    try:
        reset = conn.execute(
            "SELECT * FROM password_resets WHERE token = ?",
            (token,)
        ).fetchone()

        if reset is None:
            return jsonify({"message": "Invalid or expired token"}), 400

        expires_at = datetime.fromisoformat(reset["expires_at"])

        if datetime.now(timezone.utc) >= expires_at:
            conn.execute(
                "DELETE FROM password_resets WHERE id = ?",
                (reset["id"],)
            )
            conn.commit()
            return jsonify({"message": "Reset token has expired"}), 400

        hashed_password = generate_password_hash(new_password)

        conn.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (hashed_password, reset["user_id"])
        )

        conn.execute(
            "DELETE FROM password_resets WHERE id = ?",
            (reset["id"],)
        )
        conn.commit()

        return jsonify({"message": "Password reset successfully!"}), 200

    finally:
        conn.close()


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

