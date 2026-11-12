# HireNova – System Architecture & Design Specification

This document details the architectural blueprints, component interactions, database schema relationships, and runtime workflows for the **HireNova** web application.

---

## 1. High-Level System Architecture

HireNova is engineered following a clean **3-Tier Client-Server Architecture**:

```
+------------------------------------------------------------------------+
|                         Presentation Tier                              |
|   HTML5  *  CSS3  *  Bootstrap 5.3  *  Vanilla JavaScript (ES6+)       |
|                                                                        |
|  [ Single Page Application (SPA) UI ]  <--->  [ Asynchronous Fetch ]   |
+-----------------------------------+------------------------------------+
                                    |
                            HTTP / REST JSON
                                    |
+-----------------------------------v------------------------------------+
|                         Application Tier                               |
|                     Python 3.13  *  Flask 3.1                          |
|                                                                        |
|   +-------------------+  +-------------------+  +-------------------+  |
|   |   Auth Service    |  |    Jobs Service   |  | Applications Svc  |  |
|   +-------------------+  +-------------------+  +-------------------+  |
|   +-------------------+  +-------------------+  +-------------------+  |
|   |  Admin Controller |  |  Password Reset   |  | Session Manager   |  |
|   +-------------------+  +-------------------+  +-------------------+  |
+-----------------------------------+------------------------------------+
                                    |
                           SQLite Connection / SQL
                                    |
+-----------------------------------v------------------------------------+
|                            Data Tier                                   |
|               SQLite 3  *  Foreign Key Constraints                     |
|                                                                        |
|   [ users ] <----+ (1:N)                                               |
|                  |                                                     |
|                  +------ [ applications ] ------+ (N:1) ---> [ jobs ]  |
|                  |                                                     |
|   [ password_resets ] <---+ (1:1)                                      |
+------------------------------------------------------------------------+
```

---

## 2. Component Structure

```mermaid
flowchart TD
    subgraph Client["Frontend Client (Browser)"]
        UI["DOM / Bootstrap View (home.html, base.html)"]
        JS["Interactive JS Controller (Fetch API, Modal Triggers)"]
        CSS["Custom Styling (style.css)"]
    end

    subgraph Server["Flask Application Server (src/app.py)"]
        Router["Flask URL Routing Engine"]
        AuthCtrl["Authentication Controller (/api/register, /api/login, /api/logout)"]
        JobCtrl["Job Listings Controller (/api/jobs, /api/jobs/:id)"]
        AppCtrl["Applications Controller (/api/jobs/:id/apply, /api/my-applications)"]
        AdminCtrl["Admin Controller (/api/admin/applications, /api/admin/jobs)"]
        ResetCtrl["Password Reset Controller (/api/forgot-password, /api/reset-password)"]
        SessionStore["Server-Side Signed Cookie Session"]
    end

    subgraph Database["Relational Database (SQLite)"]
        UsersTbl[("users Table")]
        JobsTbl[("jobs Table")]
        AppsTbl[("applications Table")]
        ResetsTbl[("password_resets Table")]
    end

    UI --> JS
    JS -- "HTTP JSON / Async Fetch" --> Router
    Router --> AuthCtrl
    Router --> JobCtrl
    Router --> AppCtrl
    Router --> AdminCtrl
    Router --> ResetCtrl

    AuthCtrl --> UsersTbl
    AuthCtrl --> SessionStore
    JobCtrl --> JobsTbl
    AppCtrl --> AppsTbl
    AppCtrl --> JobsTbl
    AdminCtrl --> AppsTbl
    AdminCtrl --> JobsTbl
    ResetCtrl --> ResetsTbl
    ResetCtrl --> UsersTbl
```

---

## 3. Database Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o{ APPLICATIONS : "submits"
    USERS ||--o{ PASSWORD_RESETS : "requests"
    JOBS ||--o{ APPLICATIONS : "receives"

    USERS {
        INTEGER id PK "AUTOINCREMENT"
        TEXT name "NOT NULL"
        TEXT email UK "NOT NULL, UNIQUE"
        TEXT password "NOT NULL, HASHED"
        TEXT role "DEFAULT 'jobseeker'"
    }

    JOBS {
        INTEGER id PK "AUTOINCREMENT"
        TEXT title "NOT NULL"
        TEXT company "NOT NULL"
        TEXT location "NOT NULL"
        TEXT description "NOT NULL"
        TEXT salary "OPTIONAL"
    }

    APPLICATIONS {
        INTEGER id PK "AUTOINCREMENT"
        INTEGER user_id FK "REFERENCES users(id) ON DELETE CASCADE"
        INTEGER job_id FK "REFERENCES jobs(id) ON DELETE RESTRICT"
        TEXT status "DEFAULT 'Pending'"
    }

    PASSWORD_RESETS {
        INTEGER id PK "AUTOINCREMENT"
        INTEGER user_id FK "REFERENCES users(id) ON DELETE CASCADE"
        TEXT token UK "NOT NULL, UNIQUE"
        TEXT expires_at "ISO-8601 TIMESTAMP"
    }
```

### Integrity Constraints & Rules
1. **Unique Email**: `users.email` is declared `UNIQUE` to prevent duplicate account registration.
2. **Composite Uniqueness on Applications**: `UNIQUE(user_id, job_id)` guarantees that a candidate cannot submit multiple applications for the exact same job listing.
3. **Foreign Key Cascading**: When a user is removed, associated password reset tokens and applications cascade safely.
4. **Deletion Restriction on Jobs**: Deleting a job is prohibited if applications are linked to it (`ON DELETE RESTRICT`), preventing orphan records.

---

## 4. Sequence Diagrams

### 4.1 Job Application & Duplicate Prevention Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Candidate as Jobseeker
    participant Client as Frontend SPA
    participant Server as Flask Backend
    participant DB as SQLite DB

    Candidate->>Client: Clicks "Apply Now" on Job Card
    Client->>Server: POST /api/jobs/{id}/apply (Session Cookie)
    alt User is Not Authenticated
        Server-->>Client: 401 Unauthorized {"message": "Please login first"}
        Client->>Candidate: Prompts user to log in
    else User is Authenticated
        Server->>DB: SELECT id FROM applications WHERE user_id=? AND job_id=?
        alt Application Already Exists
            DB-->>Server: Record found
            Server-->>Client: 409 Conflict {"message": "You have already applied for this job"}
            Client->>Candidate: Displays warning banner
        else Application Does Not Exist
            Server->>DB: INSERT INTO applications (user_id, job_id, status) VALUES (?, ?, 'Pending')
            DB-->>Server: Commit successful
            Server-->>Client: 201 Created {"message": "Application submitted successfully!"}
            Client->>Candidate: Displays success confirmation modal
        end
    end
```

### 4.2 Admin Review & Application Status Update Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrator
    participant Client as Admin Dashboard SPA
    participant Server as Flask Backend
    participant DB as SQLite DB

    Admin->>Client: Navigates to Admin Dashboard
    Client->>Server: GET /api/admin/applications (Session Cookie)
    Server->>DB: Verify role == 'admin' & fetch all applications with user & job metadata
    DB-->>Server: Returns joined application rows
    Server-->>Client: 200 OK [applications list]
    Client->>Admin: Renders application cards with status dropdown

    Admin->>Client: Selects status ('Shortlisted' / 'Rejected')
    Client->>Server: PUT /api/admin/applications/{id} {"status": "Shortlisted"}
    Server->>DB: UPDATE applications SET status=? WHERE id=?
    DB-->>Server: Update confirmed
    Server-->>Client: 200 OK {"message": "Application status updated successfully!"}
    Client->>Admin: Updates status badge in real-time
```

---

## 5. Security & Verification Architecture

1. **Password Security**: Passwords are never stored in plaintext. Werkzeug's `generate_password_hash` uses PBKDF2/SHA256 with cryptographically strong salt.
2. **Session Security**: Session tokens are encrypted and tamper-resistant using Flask's signed cookie mechanism configured with `app.secret_key`.
3. **Role-Based Access Control (RBAC)**: All administrative endpoints (`/api/admin/*`, `POST /api/jobs`, `PUT /api/jobs/<id>`, `DELETE /api/jobs/<id>`) enforce strict verification:
   ```python
   if session.get("user_role") != "admin":
       return jsonify({"message": "Admin access required"}), 403
   ```
4. **SQL Injection Mitigation**: All database queries utilize parameterized queries (`?` placeholders) throughout `src/app.py` and `src/database.py`, preventing SQL injection vectors.
5. **Time-Limited Password Resets**: Tokens are generated via `secrets.token_urlsafe(32)` and enforce a strict 15-minute expiration timestamp with automatic invalidation upon use.
