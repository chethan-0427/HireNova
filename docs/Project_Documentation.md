# HIRENOVA – FIND YOUR NEXT OPPORTUNITY
## MINOR PROJECT TECHNICAL DOCUMENTATION REPORT
### Individual Internship Project Submission

---

## 1. Executive Summary & Abstract

**HireNova – Find Your Next Opportunity** is a full-featured Online Job Portal Web Application designed and implemented to bridge the gap between jobseekers and hiring organizations. Developed as an individual minor project for internship fulfillment, the application features an asynchronous single-page interface powered by modern JavaScript, HTML5, CSS3, and Bootstrap 5, coupled with a Python Flask RESTful backend and a normalized SQLite relational database.

The platform provides end-to-end recruitment capabilities: candidates can register, browse job postings, filter by keywords or location, inspect detailed job requirements, submit applications, and track application progress in real time with duplicate-application prevention. Concurrently, hiring administrators have access to an administrative dashboard to create and modify job listings, inspect received candidate submissions, and transition application statuses between `Pending`, `Shortlisted`, and `Rejected`. The system includes secure session authentication, PBKDF2/SHA256 password hashing, and a tokenized password recovery mechanism.

---

## 2. Project Objectives & Scope

### 2.1 Core Objectives
1. **Unified Portal**: Provide an intuitive web platform connecting candidates with career opportunities.
2. **Robust Authentication**: Implement session-based authentication with role-based access control (RBAC) separating `jobseeker` and `admin` roles.
3. **Data Integrity & Duplicate Prevention**: Enforce database-level uniqueness constraints preventing candidates from applying multiple times to the same position.
4. **Dynamic Search & Discovery**: Deliver instant search across job titles, company names, and descriptions without requiring full page reloads.
5. **Administrative Management**: Empower administrators to manage jobs (create, update, delete) and review applications.
6. **Application Lifecycle Tracking**: Enable candidates to monitor their application review status (`Pending`, `Shortlisted`, `Rejected`).
7. **Security & Resiliency**: Ensure parameterized SQL queries, secure password hashing, and token-based password recovery.

### 2.2 Project Scope & Limitations
- **Current Scope**: Optimized for individual organization/agency recruitment with multi-user access (jobseekers and recruiters/administrators).
- **Environment**: Configured for local development and self-hosted environments using SQLite with automated schema initialization.
- **Future Scope**: Planned integration of external SMTP email services, PDF resume parsing, cloud object storage (AWS S3), and algorithmic candidate-job matching.

---

## 3. Technology Stack Analysis

| Layer | Technology | Version | Rationale & Responsibility |
|---|---|---|---|
| **Backend Framework** | Python / Flask | Python 3.13 / Flask 3.1.3 | Lightweight, modular WSGI web framework providing RESTful JSON routing, session handling, and ORM-free raw SQLite performance. |
| **Security & Hashing** | Werkzeug Security | Werkzeug 3.1.9 | PBKDF2 with SHA256 salt generation for irreversible password protection and cryptographic verification. |
| **Database Engine** | SQLite 3 | Embedded | ACID-compliant relational database engine enforcing foreign keys, unique composite indexes, and low-latency disk operations. |
| **Frontend Structure** | HTML5 / Jinja2 | HTML5 Specification | Semantic markup rendered dynamically using Flask Jinja2 templating with modular block inheritance (`base.html` / `home.html`). |
| **Styling & Design** | CSS3 & Bootstrap | Bootstrap 5.3.3 | Mobile-first responsive layout grid, custom dark theme accents, interactive modal dialogs, and navigation collapse. |
| **Client Scripting** | JavaScript | ES6+ / Fetch API | Asynchronous HTTP client communication, DOM manipulation, real-time search filtering, and stateful authentication rendering. |
| **Version Control** | Git | 2.56.1 | Branching model (`main`, `dev`, `feature/*`), commit traceability, and professional repository organization. |
| **Testing** | unittest | Standard Library | Automated regression and integration test suite executing 9 test cases covering API contracts and edge cases. |

---

## 4. System Architecture & Design

### 4.1 Multi-Tier Architecture Overview
HireNova follows a clean 3-tier architecture:
1. **Presentation Tier (Client)**: User interface presented in the browser using HTML5, CSS3, Bootstrap 5, and JavaScript. All interactions (such as applying, filtering, logging in) trigger asynchronous REST API calls using the `fetch()` API.
2. **Application Tier (Server)**: Flask web server operating as an API gateway and business logic controller. Manages user sessions, sanitizes inputs, enforces authentication guards, and renders server-side templates.
3. **Data Tier (Database)**: SQLite database engine with foreign key enforcement (`PRAGMA foreign_keys = ON`), managing relational tables for users, jobs, applications, and password reset tokens.

```
+--------------------------------------------------------------------------+
|                            Web Browser (Client)                          |
|  - Responsive Single-Page Layout (home.html, base.html)                  |
|  - Custom CSS Style System (style.css)                                   |
|  - Vanilla JS Controller (Fetch API, DOM Events, Modals)                 |
+------------------------------------+-------------------------------------+
                                     |
                             REST JSON / HTTP
                                     |
+------------------------------------v-------------------------------------+
|                           Flask Backend Server                           |
|  - Route Handlers & REST API Controllers (src/app.py)                    |
|  - PBKDF2 Password Hashing (werkzeug.security)                           |
|  - Session-Based Role-Based Access Control (RBAC)                        |
|  - Automated Test Suite (tests/test_app.py)                              |
+------------------------------------+-------------------------------------+
                                     |
                              SQLite Engine
                                     |
+------------------------------------v-------------------------------------+
|                           SQLite Database                                |
|  - users: id, name, email (UK), password, role                           |
|  - jobs: id, title, company, location, salary, description               |
|  - applications: id, user_id (FK), job_id (FK), status, UNIQUE(user,job) |
|  - password_resets: id, user_id (FK), token (UK), expires_at             |
+--------------------------------------------------------------------------+
```

---

## 5. Detailed Database Schema Design

The SQLite database (`hirenova.db`) utilizes 4 normalized relational tables:

### 5.1 `users` Table
Stores candidate and administrator account credentials.
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'jobseeker'
);
```

### 5.2 `jobs` Table
Maintains job postings created by administrators.
```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    salary TEXT
);
```

### 5.3 `applications` Table
Links applicants to specific job listings with status tracking and duplicate protection.
```sql
CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE RESTRICT,
    UNIQUE(user_id, job_id)
);
```

### 5.4 `password_resets` Table
Stores temporary cryptographically secure reset tokens.
```sql
CREATE TABLE password_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 6. Functional Module Breakdown

### 6.1 Authentication & Session Management Module
- **Registration**: Accepts name, email, and password. Performs client- and server-side validation (email format, minimum 8 characters). Generates cryptographic hash via `generate_password_hash()`.
- **Login**: Validates credentials against SQLite database using `check_password_hash()`. Establishes signed session cookies containing `user_id` and `user_role`.
- **Session Introspection**: `/api/current-user` endpoint dynamically enables the UI to switch between unauthenticated, jobseeker, and administrator views.
- **Logout**: Clears the session dictionary, terminating authenticated privileges.

### 6.2 Job Exploration & Search Module
- **Public Directory**: Displays active job postings in responsive cards featuring title, company, location, and salary pills.
- **Dynamic Search Filtering**: Live search input filters listings on the backend using SQL `LIKE ?` queries across job title, company name, and job description.
- **Modal Detail View**: Displays complete role specifications and an interactive "Apply Now" button without page reloads.

### 6.3 Job Application & Duplicate Prevention Module
- **Application Submission**: Validates active login session and checks whether the candidate has already applied.
- **Duplicate Prevention**: Enforced at two layers:
  1. Application layer: Checks existing records via `SELECT id FROM applications WHERE user_id=? AND job_id=?`.
  2. Database constraint layer: Handled by `UNIQUE(user_id, job_id)` constraint triggering `sqlite3.IntegrityError` which gracefully returns HTTP 409 Conflict.
- **Candidate Tracking ("My Applications")**: Renders all positions applied for by the logged-in user with dynamic status badges (`Pending`, `Shortlisted`, `Rejected`).

### 6.4 Administrative Control Center Module
- **Access Control Guard**: Restricts administrative endpoints using `session.get("user_role") == "admin"`. Unauthorized requests receive HTTP 403 Forbidden.
- **Job Management (CRUD)**:
  - Add new job postings with company, location, salary, and requirements.
  - Edit existing job postings.
  - Delete jobs (protected: jobs with existing candidate applications cannot be deleted, preserving audit history).
- **Application Review & Status Updates**: Inspects all submissions across all postings and updates review status (`Pending` -> `Shortlisted` / `Rejected`).

### 6.5 Token-Based Password Recovery Module
- **Reset Request**: Validates email existence; generates a 32-byte URL-safe cryptographic token using `secrets.token_urlsafe(32)` valid for 15 minutes.
- **Reset Confirmation**: Verifies token validity and expiration timestamp. Updates password hash and purges expired token.

---

## 7. Application Workflow & State Transitions

```
[ Unregistered Visitor ]
        |
        v
  [ Registration ] ---> [ Registered User ]
                               |
                               v
                       [ Login Session ]
                        /             \
                       /               \
         (Role: jobseeker)           (Role: admin)
              |                            |
              v                            v
      [ Browse Jobs ]            [ Admin Dashboard ]
              |                            |
              v                            +--> [ Post / Edit Jobs ]
      [ View Details ]                     |
              |                            +--> [ Review All Applicants ]
              v                            |
       [ Apply for Job ]                   +--> [ Update Status: ]
              |                                 - Shortlisted
       (Duplicate Check)                        - Rejected
              |                                 - Pending
              +---> [ My Applications ] <---------------+
```

---

## 8. Verification & Test Execution Results

HireNova includes an automated regression test suite built on Python's `unittest` framework (`tests/test_app.py`) executing against an isolated temporary SQLite database:

| Test ID | Test Case | Target Endpoint / Logic | Expected Output | Actual Result | Status |
|---|---|---|---|---|---|
| `TC-01` | Home Page Accessibility | `GET /` | HTTP 200, renders HTML layout | HTTP 200 OK | **PASSED** |
| `TC-02` | User Registration Success | `POST /api/register` | HTTP 201 Created | HTTP 201 Created | **PASSED** |
| `TC-03` | Duplicate Email Rejection | `POST /api/register` | HTTP 409 Conflict | HTTP 409 Conflict | **PASSED** |
| `TC-04` | Password Validation (<8 chars) | `POST /api/register` | HTTP 400 Bad Request | HTTP 400 Bad Request | **PASSED** |
| `TC-05` | Login & Session Lifecycle | `POST /api/login`, `/api/logout` | HTTP 200, session set & cleared | HTTP 200 OK | **PASSED** |
| `TC-06` | Job Search & Filter Logic | `GET /api/jobs?search=...` | HTTP 200, filtered JSON array | HTTP 200 OK | **PASSED** |
| `TC-07` | Job Application Flow | `POST /api/jobs/:id/apply` | HTTP 201 Created | HTTP 201 Created | **PASSED** |
| `TC-08` | Duplicate Application Block | `POST /api/jobs/:id/apply` | HTTP 409 Conflict | HTTP 409 Conflict | **PASSED** |
| `TC-09` | Admin CRUD & RBAC Authorization | `POST /api/jobs`, `PUT`, `DELETE` | HTTP 401 unauth, 201/200 admin | HTTP 401 & 200 OK | **PASSED** |
| `TC-10` | Password Reset Token Lifecycle | `POST /api/forgot-password`, `reset` | HTTP 200, updates hash | HTTP 200 OK | **PASSED** |

**Summary**: 9 automated test suites executed, 9 passed (0 failures, 0 errors).

---

## 9. Output Screenshots & Results Gallery

The visual layout of the HireNova platform has been validated across desktop and mobile screen resolutions. The output screenshot artifacts are structured inside the repository under `assets/screenshots/`:

### Figure 1: Landing Page & Hero Section
![Landing Page Hero](../assets/screenshots/01_landing_hero.svg)
*Description: Landing page showing application branding, headline call-to-action buttons ("Explore Jobs", "Create Account"), and the top navigation bar.*

---

### Figure 2: Job Opportunities & Dynamic Search
![Job Search](../assets/screenshots/02_job_search_filters.svg)
*Description: Opportunities grid displaying job cards with title, company, location, salary tags, and the live search filter.*

---

### Figure 3: Job Specification Modal
![Job Details Modal](../assets/screenshots/03_job_details_modal.svg)
*Description: Modal dialog presenting comprehensive role requirements and the "Apply Now" trigger button.*

---

### Figure 4: User Registration & Validation
![User Registration](../assets/screenshots/04_user_registration.svg)
*Description: Registration interface demonstrating input fields for name, email, and password with validation error handling.*

---

### Figure 5: User Login Interface
![User Login](../assets/screenshots/05_user_login.svg)
*Description: Secure authentication interface establishing authenticated session credentials.*

---

### Figure 6: Job Application Submission Feedback
![Application Success](../assets/screenshots/06_job_application_submission.svg)
*Description: Real-time feedback notification indicating successful application submission.*

---

### Figure 7: Duplicate Application Prevention
![Duplicate Application Alert](../assets/screenshots/07_duplicate_application_prevention.svg)
*Description: Conflict alert (HTTP 409) preventing candidates from applying twice for the same vacancy.*

---

### Figure 8: Jobseeker Application Status Tracker
![My Applications Status](../assets/screenshots/08_my_applications_status_tracking.svg)
*Description: "My Applications" dashboard displaying submitted applications with live status badges (Pending, Shortlisted, Rejected).*

---

### Figure 9: Admin Dashboard Overview
![Admin Dashboard](../assets/screenshots/09_admin_dashboard_overview.svg)
*Description: Recruiter control center listing all received applicant profiles across all open positions.*

---

### Figure 10: Admin Job Posting Interface
![Post New Job](../assets/screenshots/10_admin_post_new_job.svg)
*Description: Modal form for posting and updating job vacancies with title, location, salary, and job description.*

---

### Figure 11: Application Review & Status Transition
![Update Status](../assets/screenshots/11_admin_update_application_status.svg)
*Description: Admin status selector transitioning candidates between Pending, Shortlisted, and Rejected.*

---

### Figure 12: Password Recovery Flow
![Password Reset](../assets/screenshots/12_password_reset_flow.svg)
*Description: Secure token generation and reset form for account recovery.*

---

## 10. Repository Branching Strategy & Git Workflow

The project repository implements a Git branching strategy suitable for production-grade minor project development:

```
main (production-ready / stable releases)
  ^
  | [Release Merge]
dev (active development integration)
  ^
  +-- feature/database-setup  (SQLite schema, migrations, connection manager)
  +-- feature/backend-api     (Flask RESTful routes, authentication, RBAC)
  +-- feature/frontend        (Responsive SPA UI, Bootstrap templates, CSS)
  +-- feature/documentation   (Internship documentation, architecture, assets)
```

- **`main` Branch**: Contains tested, production-ready code tagged with release versions (e.g. `v1.0.0`).
- **`dev` Branch**: Serves as the primary integration branch where module features are consolidated and verified.
- **Feature Branches**: Isolated branches dedicated to specific modules (`feature/backend-api`, `feature/frontend`, `feature/database-setup`, `feature/documentation`), ensuring clean git commit history.

---

## 11. Setup, Installation & Verification Guide

### Step 1: Clone or Navigate to the Repository
```bash
cd HireNova
```

### Step 2: Set Up Virtual Environment
```bash
python -m venv venv
```

Activate the environment:
- **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Linux / macOS**:
  ```bash
  source venv/bin/activate
  ```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Seed Sample Data (Optional)
To populate realistic demo jobs, test candidates, and applications:
```bash
python scripts/seed_data.py
```

### Step 5: Run the Automated Test Suite
```bash
python -m unittest tests/test_app.py
```

### Step 6: Start the Web Application
```bash
python run.py
# or
python app.py
```
Open your web browser and visit: `http://127.0.0.1:5000`

---

## 12. Future Enhancements & Roadmap

1. **Resume File Uploads**: Integrating secure multipart file uploads allowing candidates to upload PDF/DOCX resumes stored locally or in cloud storage (AWS S3).
2. **Automated Email Notifications**: Integrating SMTP/SendGrid to deliver instant status notifications to candidates when their status changes.
3. **Advanced Filtering & Faceted Search**: Multi-select filtering by experience level, remote vs. on-site, and salary range.
4. **Applicant Skill Matching**: Natural language processing (NLP) to calculate match percentages between job descriptions and candidate resumes.
5. **Production Containerization**: Dockerfile and Docker Compose configurations for containerized deployment on cloud platforms (Render, AWS, DigitalOcean).

---

## 13. Conclusion & Student Declaration

**HireNova – Find Your Next Opportunity** successfully fulfills all objectives set out in the minor project guidelines. It demonstrates strong proficiency in full-stack web development, client-server communication, database normalization, session security, automated software testing, and professional version control workflows.

### Project Metadata
- **Project Title**: HireNova – Find Your Next Opportunity
- **Project Nature**: Online Job Portal Web Application
- **Submission Type**: Individual Internship Minor Project
- **Developer**: Chethan S (`chethan.sv2006@gmail.com`)
- **Academic Year**: 2026
