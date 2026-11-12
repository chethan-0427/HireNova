# HireNova – Output Screenshots & UI Gallery

This directory contains the visual output artifacts for the HireNova Job Portal. These screenshots serve as evidence of implementation for the internship minor project submission.

---

## Screenshot Inventory & Mapping

| File Name | Screen / Feature | Description |
|---|---|---|
| `01_landing_hero.png` | Landing Page & Hero Section | Homepage with branding, call-to-actions, and navigation bar. |
| `02_job_search_filters.png` | Job Discovery & Search | Dynamic live search filtering job cards by title, company, or keyword. |
| `03_job_details_modal.png` | Job Details Modal | Detailed view showing salary, location, description, and "Apply Now" button. |
| `04_user_registration.png` | Registration Form | Client-side validated form with email format and password strength checks. |
| `05_user_login.png` | Authentication Modal/View | Secure login interface with session management. |
| `06_job_application_submission.png` | Application Success | Feedback toast/alert confirming job application submission. |
| `07_duplicate_application_prevention.png` | Duplicate Constraint Alert | Warning showing rejection when applying for the same position twice. |
| `08_my_applications_status_tracking.png` | Jobseeker Application Dashboard | Table/cards showing applied jobs with badges: Pending, Shortlisted, Rejected. |
| `09_admin_dashboard_overview.png` | Admin Dashboard | Administrative panel showing all candidate submissions and system stats. |
| `10_admin_post_new_job.png` | Post/Edit Job Form | Modal/form allowing administrators to create and modify job postings. |
| `11_admin_update_application_status.png` | Status Transition | Interactive status updater (Pending -> Shortlisted / Rejected). |
| `12_password_reset_flow.png` | Password Recovery | Token-based password recovery and verification screen. |

---

## How to Capture and Replace Screenshots

1. **Launch the Application**:
   ```bash
   python run.py
   ```
2. **Seed Demo Data (Optional but recommended)**:
   ```bash
   python scripts/seed_data.py
   ```
3. **Open Browser**:
   Navigate to `http://127.0.0.1:5000` in Google Chrome or Microsoft Edge.
4. **Capture**:
   - Use `Windows + Shift + S` or Chrome DevTools Device Mode (`Ctrl + Shift + M`).
   - Save screenshots with 1920x1080 resolution (or responsive mobile view where applicable).
   - Save files directly into this directory (`assets/screenshots/`) using the filenames listed in the table above.
