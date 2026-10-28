# Healthcare Backend API

A Django REST API for healthcare management, featuring JWT authentication, patient record management, doctor discovery, and patient-doctor assignments. Includes interactive Swagger documentation for API testing.

## Key Features

- **JWT Authentication:** User registration, login, and token refresh.
- **Patient Management:** CRUD operations with user-level ownership isolation.
- **Doctor Directory:** Doctor management, search, and specialization filtering.
- **Patient-Doctor Mapping:** Secure assignments, duplicate prevention, and filtering.
- **API Documentation:** Interactive Swagger UI and ReDoc.
- **Validation & Testing:** Input validation, authorization checks, and automated tests.

## Tech Stack

`Python` · `Django` · `Django REST Framework` · `PostgreSQL` · `SimpleJWT` · `drf-spectacular`

##  Project Structure

```text
├── accounts/     # Registration and authentication
├── patients/     # Patient records and ownership
├── doctors/      # Doctor directory and search
├── mappings/     # Patient-doctor assignments
├── config/       # Django settings and URL routing
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Healthcare-backend-django-main
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the environment

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Configure the required variables in `.env`, including:

- `SECRET_KEY`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

Ensure PostgreSQL is running and the configured database exists. Never commit `.env` or real credentials.

### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Start the server

```bash
python manage.py runserver
```

## 📖 API Documentation

Once the server is running, explore and test the endpoints interactively:

| Resource | URL |
|---|---|
| **Swagger UI** | [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/) |
| ReDoc | [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/) |
| OpenAPI Schema | [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/) |
| Django Admin | [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) |

### Main API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register a user |
| POST | `/api/auth/login/` | Obtain JWT tokens |
| POST | `/api/auth/refresh/` | Refresh access token |
| GET, POST | `/api/patients/` | List or create patients |
| GET, PUT, PATCH, DELETE | `/api/patients/{id}/` | Manage a patient |
| GET, POST | `/api/doctors/` | List or create doctors |
| GET, PUT, PATCH, DELETE | `/api/doctors/{id}/` | Manage a doctor |
| GET, POST | `/api/mappings/` | List or create mappings |
| GET, PUT, PATCH, DELETE | `/api/mappings/{id}/` | Manage a mapping |

Protected endpoints require a JWT access token in the `Authorization: Bearer <access_token>` header. See Swagger for request schemas, filters, and response details.

##  Testing

Run the automated test suite:

```bash
python manage.py check
python manage.py test
```

The project has **54 passing automated tests**, as verified in the current development environment.

##  Security Highlights

- Passwords are hashed using Django's authentication system.
- Patient records are restricted by ownership, with staff access governed by permissions.
- Mapping operations validate patient ownership and prevent duplicate assignments.
- Environment secrets are kept outside source control.

---

**Note:** This project is intended for educational and assessment purposes. Configure appropriate security settings before any production deployment.