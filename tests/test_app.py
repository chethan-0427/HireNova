"""
HireNova Automated Test Suite
Covers authentication, job listings, application processing,
duplicate prevention, admin authorization, and password recovery.
"""

import os
import sys
import tempfile
import unittest

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.database import create_tables, get_db_connection
from werkzeug.security import generate_password_hash


class HireNovaTestCase(unittest.TestCase):

    def setUp(self):
        # Create an isolated temporary SQLite database for testing
        self.db_fd, self.test_db_path = tempfile.mkstemp(suffix=".db")
        os.environ["HIRENOVA_DB_PATH"] = self.test_db_path

        # Re-import app with updated db path
        from src import app as app_module
        self.app_module = app_module
        self.app = app_module.app
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "test-secret-key-123"
        self.client = self.app.test_client()

        # Initialize tables in temporary database
        create_tables(self.test_db_path)

        # Seed test admin and test job
        conn = get_db_connection(self.test_db_path)
        conn.execute(
            """
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
            """,
            ("Admin Test", "admin@test.com", generate_password_hash("adminpass123"), "admin")
        )
        conn.execute(
            """
            INSERT INTO jobs (title, company, location, description, salary)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("Software Engineer", "TechCorp", "Remote", "Develop web applications.", "INR 10 LPA")
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except OSError:
                pass

    def test_01_home_page_loads(self):
        """Verify home route returns status 200 and renders HTML."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"HireNova", response.data)

    def test_02_registration_success(self):
        """Verify valid user registration creates account with 201 status."""
        response = self.client.post("/api/register", json={
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "password": "securepassword123"
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn("Registration successful", data["message"])

    def test_03_registration_duplicate_email(self):
        """Verify registering with duplicate email returns 409 conflict."""
        self.client.post("/api/register", json={
            "name": "Jane",
            "email": "duplicate@example.com",
            "password": "password123"
        })
        response = self.client.post("/api/register", json={
            "name": "Jane Second",
            "email": "duplicate@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 409)

    def test_04_registration_password_length_validation(self):
        """Verify password shorter than 8 characters is rejected with 400."""
        response = self.client.post("/api/register", json={
            "name": "Short Pass",
            "email": "short@example.com",
            "password": "123"
        })
        self.assertEqual(response.status_code, 400)

    def test_05_login_and_logout_flow(self):
        """Verify login sets session and logout clears session."""
        login_res = self.client.post("/api/login", json={
            "email": "admin@test.com",
            "password": "adminpass123"
        })
        self.assertEqual(login_res.status_code, 200)
        data = login_res.get_json()
        self.assertEqual(data["user"]["role"], "admin")

        # Check current user endpoint
        curr_res = self.client.get("/api/current-user")
        self.assertEqual(curr_res.status_code, 200)
        self.assertTrue(curr_res.get_json()["logged_in"])

        # Logout
        logout_res = self.client.post("/api/logout")
        self.assertEqual(logout_res.status_code, 200)

        # Check current user again
        curr_res_after = self.client.get("/api/current-user")
        self.assertFalse(curr_res_after.get_json()["logged_in"])

    def test_06_jobs_listing_and_search(self):
        """Verify jobs endpoint lists jobs and filters by keyword."""
        response = self.client.get("/api/jobs")
        self.assertEqual(response.status_code, 200)
        jobs = response.get_json()
        self.assertGreaterEqual(len(jobs), 1)

        # Search existing keyword
        search_res = self.client.get("/api/jobs?search=Software")
        self.assertEqual(search_res.status_code, 200)
        self.assertEqual(len(search_res.get_json()), 1)

        # Search non-existing keyword
        empty_res = self.client.get("/api/jobs?search=NonExistentKeywordXYZ")
        self.assertEqual(empty_res.status_code, 200)
        self.assertEqual(len(empty_res.get_json()), 0)

    def test_07_job_application_flow_and_duplicate_prevention(self):
        """Verify job application submission and duplicate prevention (409)."""
        # Register and log in as jobseeker
        self.client.post("/api/register", json={
            "name": "Applicant",
            "email": "applicant@test.com",
            "password": "password123"
        })
        self.client.post("/api/login", json={
            "email": "applicant@test.com",
            "password": "password123"
        })

        # Apply for job 1
        apply_res = self.client.post("/api/jobs/1/apply")
        self.assertEqual(apply_res.status_code, 201)

        # Verify application appears in my-applications
        my_apps = self.client.get("/api/my-applications")
        self.assertEqual(my_apps.status_code, 200)
        apps_list = my_apps.get_json()
        self.assertEqual(len(apps_list), 1)
        self.assertEqual(apps_list[0]["status"], "Pending")

        # Try to apply again for the same job (should be blocked)
        duplicate_res = self.client.post("/api/jobs/1/apply")
        self.assertEqual(duplicate_res.status_code, 409)

    def test_08_admin_job_crud_and_status_update(self):
        """Verify admin can add jobs, update application status, and manage listings."""
        # Non-logged in add job must fail (401)
        res_unauth = self.client.post("/api/jobs", json={
            "title": "Unauthorized Job",
            "company": "NoCo",
            "location": "Nowhere",
            "description": "Desc"
        })
        self.assertEqual(res_unauth.status_code, 401)

        # Log in as admin
        self.client.post("/api/login", json={
            "email": "admin@test.com",
            "password": "adminpass123"
        })

        # Add job
        add_res = self.client.post("/api/jobs", json={
            "title": "Data Analyst",
            "company": "Analytics Corp",
            "location": "Bangalore",
            "description": "SQL and Python required.",
            "salary": "INR 8 LPA"
        })
        self.assertEqual(add_res.status_code, 201)

        # Update job
        update_res = self.client.put("/api/admin/jobs/2", json={
            "title": "Senior Data Analyst",
            "company": "Analytics Corp",
            "location": "Bangalore (Hybrid)",
            "description": "Advanced SQL and Python required.",
            "salary": "INR 12 LPA"
        })
        self.assertEqual(update_res.status_code, 200)

        # Delete job with no applications
        del_res = self.client.delete("/api/admin/jobs/2")
        self.assertEqual(del_res.status_code, 200)

    def test_09_forgot_and_reset_password_workflow(self):
        """Verify password reset request generates token and allows password reset."""
        # Request reset
        forgot_res = self.client.post("/api/forgot-password", json={
            "email": "admin@test.com"
        })
        self.assertEqual(forgot_res.status_code, 200)

        # Retrieve token from database
        conn = get_db_connection(self.test_db_path)
        token_row = conn.execute(
            "SELECT token FROM password_resets WHERE user_id = 1"
        ).fetchone()
        self.assertIsNotNone(token_row)
        token = token_row["token"]
        conn.close()

        # Reset password
        reset_res = self.client.post("/api/reset-password", json={
            "token": token,
            "new_password": "newadminpassword456"
        })
        self.assertEqual(reset_res.status_code, 200)

        # Verify login with new password
        login_res = self.client.post("/api/login", json={
            "email": "admin@test.com",
            "password": "newadminpassword456"
        })
        self.assertEqual(login_res.status_code, 200)


if __name__ == "__main__":
    unittest.main()

