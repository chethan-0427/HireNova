# HireNova – REST API Reference Specification

This document provides complete documentation for the RESTful API endpoints exposed by the **HireNova** backend server (`http://127.0.0.1:5000`).

---

## 1. Overview & Conventions

- **Base URL**: `http://127.0.0.1:5000`
- **Data Format**: `application/json` for requests and responses
- **Authentication**: HTTP Cookie Session (`session["user_id"]`, `session["user_role"]`)

### Standard HTTP Status Codes

| Code | Status | Meaning |
|---|---|---|
| `200` | OK | Request succeeded, response data returned. |
| `201` | Created | Resource successfully created. |
| `400` | Bad Request | Missing required parameters or failed field validation. |
| `401` | Unauthorized | User must log in to access resource. |
| `403` | Forbidden | Insufficient permissions (requires `admin` role). |
| `404` | Not Found | Target resource does not exist. |
| `409` | Conflict | Duplicate resource constraint violated (e.g. email or duplicate application). |
| `500` | Internal Server Error | Unexpected server or database exception. |

---

## 2. Authentication Endpoints

### 2.1 User Registration
- **URL**: `/api/register`
- **Method**: `POST`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "name": "Alex Applicant",
    "email": "alex@example.com",
    "password": "password123"
  }
  ```
- **Validation Rules**:
  - `name`: Non-empty string
  - `email`: Must contain `@` and `.`, converted to lowercase
  - `password`: Minimum 8 characters
- **Responses**:
  - `201 Created`:
    ```json
    { "message": "Registration successful!" }
    ```
  - `400 Bad Request`:
    ```json
    { "message": "Password must contain at least 8 characters" }
    ```
  - `409 Conflict`:
    ```json
    { "message": "Email already registered" }
    ```

---

### 2.2 User Login
- **URL**: `/api/login`
- **Method**: `POST`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "email": "alex@example.com",
    "password": "password123"
  }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    {
      "message": "Login successful!",
      "user": {
        "id": 2,
        "name": "Alex Applicant",
        "email": "alex@example.com",
        "role": "jobseeker"
      }
    }
    ```
  - `401 Unauthorized`:
    ```json
    { "message": "Invalid email or password" }
    ```

---

### 2.3 Check Current Session
- **URL**: `/api/current-user`
- **Method**: `GET`
- **Access**: Public
- **Responses**:
  - `200 OK (Logged In)`:
    ```json
    {
      "logged_in": true,
      "user": {
        "id": 2,
        "name": "Alex Applicant",
        "email": "alex@example.com",
        "role": "jobseeker"
      }
    }
    ```
  - `200 OK (Not Logged In)`:
    ```json
    { "logged_in": false }
    ```

---

### 2.4 User Logout
- **URL**: `/api/logout`
- **Method**: `POST`
- **Access**: Authenticated User
- **Responses**:
  - `200 OK`:
    ```json
    { "message": "Logout successful!" }
    ```

---

## 3. Job Listings Endpoints

### 3.1 Explore & Search Jobs
- **URL**: `/api/jobs`
- **Method**: `GET`
- **Access**: Public
- **Query Parameters**:
  - `search` (optional): Filter by title, company, or description keywords
  - `location` (optional): Filter by location keyword
- **Responses**:
  - `200 OK`:
    ```json
    [
      {
        "id": 1,
        "title": "Full Stack Python Developer",
        "company": "TechNova Solutions",
        "location": "Bangalore, India",
        "salary": "INR 8,50,000 - 12,00,000 / year",
        "description": "Looking for a Full Stack Python Developer with experience in Flask..."
      }
    ]
    ```

---

### 3.2 Get Job Details
- **URL**: `/api/jobs/<int:job_id>`
- **Method**: `GET`
- **Access**: Public
- **Responses**:
  - `200 OK`:
    ```json
    {
      "id": 1,
      "title": "Full Stack Python Developer",
      "company": "TechNova Solutions",
      "location": "Bangalore, India",
      "salary": "INR 8,50,000 - 12,00,000 / year",
      "description": "Full job description text..."
    }
    ```
  - `404 Not Found`:
    ```json
    { "message": "Job not found" }
    ```

---

### 3.3 Create New Job
- **URL**: `/api/jobs`
- **Method**: `POST`
- **Access**: Admin Role Only
- **Request Body**:
  ```json
  {
    "title": "Cloud Architect",
    "company": "SkyHigh Systems",
    "location": "Hyderabad, India",
    "salary": "INR 18,00,000 / year",
    "description": "Lead multi-cloud deployments..."
  }
  ```
- **Responses**:
  - `201 Created`:
    ```json
    { "message": "Job added successfully!" }
    ```
  - `401 Unauthorized`:
    ```json
    { "message": "Please login first" }
    ```
  - `403 Forbidden`:
    ```json
    { "message": "Admin access required" }
    ```

---

### 3.4 Update Existing Job
- **URL**: `/api/admin/jobs/<int:job_id>`
- **Method**: `PUT`
- **Access**: Admin Role Only
- **Request Body**: (same fields as Create Job)
- **Responses**:
  - `200 OK`:
    ```json
    { "message": "Job updated successfully!" }
    ```
  - `404 Not Found`:
    ```json
    { "message": "Job not found" }
    ```

---

### 3.5 Delete Job
- **URL**: `/api/admin/jobs/<int:job_id>`
- **Method**: `DELETE`
- **Access**: Admin Role Only
- **Responses**:
  - `200 OK`:
    ```json
    { "message": "Job deleted successfully!" }
    ```
  - `409 Conflict`:
    ```json
    { "message": "Cannot delete job because applications exist" }
    ```

---

## 4. Job Applications Endpoints

### 4.1 Apply for a Job
- **URL**: `/api/jobs/<int:job_id>/apply`
- **Method**: `POST`
- **Access**: Authenticated Jobseeker
- **Responses**:
  - `201 Created`:
    ```json
    { "message": "Application submitted successfully!" }
    ```
  - `401 Unauthorized`:
    ```json
    { "message": "Please login first" }
    ```
  - `404 Not Found`:
    ```json
    { "message": "Job not found" }
    ```
  - `409 Conflict`:
    ```json
    { "message": "You have already applied for this job" }
    ```

---

### 4.2 View My Applications
- **URL**: `/api/my-applications`
- **Method**: `GET`
- **Access**: Authenticated Jobseeker
- **Responses**:
  - `200 OK`:
    ```json
    [
      {
        "application_id": 1,
        "title": "Full Stack Python Developer",
        "company": "TechNova Solutions",
        "location": "Bangalore, India",
        "status": "Pending"
      }
    ]
    ```

---

### 4.3 View All Applications (Admin)
- **URL**: `/api/admin/applications`
- **Method**: `GET`
- **Access**: Admin Role Only
- **Responses**:
  - `200 OK`:
    ```json
    [
      {
        "application_id": 1,
        "applicant_name": "Jane Jobseeker",
        "applicant_email": "jane@example.com",
        "job_title": "Full Stack Python Developer",
        "company": "TechNova Solutions",
        "status": "Pending"
      }
    ]
    ```

---

### 4.4 Update Application Status
- **URL**: `/api/admin/applications/<int:application_id>`
- **Method**: `PUT`
- **Access**: Admin Role Only
- **Request Body**:
  ```json
  { "status": "Shortlisted" }
  ```
  *(Allowed values: `"Pending"`, `"Shortlisted"`, `"Rejected"`)*
- **Responses**:
  - `200 OK`:
    ```json
    {
      "message": "Application status updated successfully!",
      "status": "Shortlisted"
    }
    ```
  - `400 Bad Request`:
    ```json
    { "message": "Invalid application status" }
    ```

---

## 5. Password Recovery Endpoints

### 5.1 Request Password Reset Token
- **URL**: `/api/forgot-password`
- **Method**: `POST`
- **Access**: Public
- **Request Body**:
  ```json
  { "email": "alex@example.com" }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    { "message": "If the account exists, a reset link will be generated." }
    ```
  *(Note: Token is logged in backend terminal for development / offline environments).*

---

### 5.2 Reset Password With Token
- **URL**: `/api/reset-password`
- **Method**: `POST`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "token": "dGhpcy1pcy1hLXNhbXBsZS10b2tlbg",
    "new_password": "newsecurepassword123"
  }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    { "message": "Password reset successfully!" }
    ```
  - `400 Bad Request`:
    ```json
    { "message": "Invalid or expired token" }
    ```
