"""
HireNova - Automated Screenshot Capture Utility
Uses Playwright to navigate the live application at 1440x900 resolution
and capture authentic .png screenshots for submission.
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "assets", "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

BASE_URL = "http://127.0.0.1:5000"


def capture_all():
    print("=" * 60)
    print("  HireNova - Capturing Application Screenshots (1440x900)")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # -------------------------------------------------------------
        # 01. Landing Hero Section
        # -------------------------------------------------------------
        print("[1/12] Capturing 01_landing_hero.png...")
        page.goto(f"{BASE_URL}/", wait_until="networkidle")
        page.wait_for_selector("#home")
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "01_landing_hero.png"))

        # -------------------------------------------------------------
        # 02. Job Search & Filtering
        # -------------------------------------------------------------
        print("[2/12] Capturing 02_job_search_filters.png...")
        page.evaluate("showSection('jobs')")
        page.wait_for_selector("#job-list .job-card")
        page.fill("#jobSearch", "Python")
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "02_job_search_filters.png"))

        # -------------------------------------------------------------
        # 03. Job Details Modal
        # -------------------------------------------------------------
        print("[3/12] Capturing 03_job_details_modal.png...")
        page.fill("#jobSearch", "")
        time.sleep(0.5)
        # Click view details on first card
        page.locator("#job-list .job-card button").first.click()
        page.wait_for_selector("#jobDetailsModal.show", state="visible")
        time.sleep(0.8)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "03_job_details_modal.png"))
        # Close modal
        page.locator('#jobDetailsModal button[data-bs-dismiss="modal"]').first.click()
        time.sleep(0.5)

        # -------------------------------------------------------------
        # 04. User Registration Form
        # -------------------------------------------------------------
        print("[4/12] Capturing 04_user_registration.png...")
        page.evaluate("showSection('register')")
        page.wait_for_selector("#registerForm")
        page.fill("#registerName", "Rahul Sharma")
        page.fill("#registerEmail", "rahul.sharma@example.com")
        page.fill("#registerPassword", "HireNova@2026Pass")
        time.sleep(0.5)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "04_user_registration.png"))

        # -------------------------------------------------------------
        # 05. User Login Form
        # -------------------------------------------------------------
        print("[5/12] Capturing 05_user_login.png...")
        page.evaluate("showSection('login')")
        page.wait_for_selector("#loginForm")
        page.fill("#loginEmail", "jane@example.com")
        page.fill("#loginPassword", "jobseekerpass123")
        time.sleep(0.5)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "05_user_login.png"))

        # -------------------------------------------------------------
        # 06. Job Application Submission (Logged in as Jane)
        # -------------------------------------------------------------
        print("[6/12] Capturing 06_job_application_submission.png...")
        # Submit login form
        page.locator('#loginForm button[type="submit"]').click()
        page.wait_for_selector("#navLogout", state="visible")
        time.sleep(1)

        # Open jobs and view a job Jane hasn't applied to yet (e.g. Data Analyst)
        page.evaluate("showSection('jobs')")
        page.wait_for_selector("#job-list .job-card")
        time.sleep(0.5)
        # Click View Details on job 4 (Data Analyst) or 5 (DevOps)
        page.locator("#job-list .job-card button").nth(3).click()
        page.wait_for_selector("#jobDetailsModal.show", state="visible")
        time.sleep(0.5)
        page.locator("#applyJobButton").click()
        page.wait_for_selector("#applyMessage", state="visible")
        time.sleep(0.8)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "06_job_application_submission.png"))

        # -------------------------------------------------------------
        # 07. Duplicate Application Prevention Alert
        # -------------------------------------------------------------
        print("[7/12] Capturing 07_duplicate_application_prevention.png...")
        # Click Apply again on the same job
        page.locator("#applyJobButton").click()
        time.sleep(0.8)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "07_duplicate_application_prevention.png"))
        # Close modal
        page.locator('#jobDetailsModal button[data-bs-dismiss="modal"]').first.click()
        time.sleep(0.5)

        # -------------------------------------------------------------
        # 08. My Applications Status Tracking
        # -------------------------------------------------------------
        print("[8/12] Capturing 08_my_applications_status_tracking.png...")
        page.evaluate("showSection('myApplications'); loadApplications();")
        page.wait_for_selector("#application-list .job-card")
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "08_my_applications_status_tracking.png"))

        # -------------------------------------------------------------
        # 09. Admin Dashboard Overview (Logged in as admin)
        # -------------------------------------------------------------
        print("[9/12] Capturing 09_admin_dashboard_overview.png...")
        # Logout Jane
        page.locator("#logoutButton").click()
        time.sleep(0.8)
        # Login as Admin
        page.evaluate("showSection('login')")
        page.fill("#loginEmail", "admin@hirenova.com")
        page.fill("#loginPassword", "adminpassword123")
        page.locator('#loginForm button[type="submit"]').click()
        page.wait_for_selector("#navAdminDashboard", state="visible")
        time.sleep(1)
        page.evaluate("showSection('adminDashboard')")
        page.wait_for_selector("#admin-applications .job-card")
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "09_admin_dashboard_overview.png"))

        # -------------------------------------------------------------
        # 10. Admin Post New Job Form
        # -------------------------------------------------------------
        print("[10/12] Capturing 10_admin_post_new_job.png...")
        page.fill("#jobTitle", "Senior AI/ML Platform Engineer")
        page.fill("#jobCompany", "NovaIntelligence Labs")
        page.fill("#jobLocation", "Bengaluru (Hybrid)")
        page.fill("#jobSalary", "INR 22,00,000 - 30,00,000 / year")
        page.fill("#jobDescription", "Architect scalable deep learning deployment pipelines, optimize inference serving with TensorRT, and integrate LLM microservices.")
        time.sleep(0.5)
        # Scroll up to form in admin dashboard
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.5)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "10_admin_post_new_job.png"))

        # -------------------------------------------------------------
        # 11. Admin Update Application Status
        # -------------------------------------------------------------
        print("[11/12] Capturing 11_admin_update_application_status.png...")
        page.evaluate("document.getElementById('admin-applications').scrollIntoView()")
        time.sleep(0.5)
        # Change status on the first application
        first_select = page.locator("#admin-applications select").first
        first_select.select_option("Shortlisted")
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "11_admin_update_application_status.png"))

        # -------------------------------------------------------------
        # 12. Password Reset Flow
        # -------------------------------------------------------------
        print("[12/12] Capturing 12_password_reset_flow.png...")
        page.evaluate("showSection('forgotPassword')")
        page.wait_for_selector("#forgotPasswordForm")
        page.fill("#forgotEmail", "jane@example.com")
        page.locator('#forgotPasswordForm button[type="submit"]').click()
        page.wait_for_selector("#forgotMessage")
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "12_password_reset_flow.png"))

        browser.close()

    print("\n[Done] All 12 real screenshots captured successfully at 1440x900 resolution!")
    print(f"Output directory: {SCREENSHOTS_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    capture_all()
