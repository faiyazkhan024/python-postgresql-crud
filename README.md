# Python & PostgreSQL CRUD Web Application

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL%2016%2B-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Package Manager: uv](https://img.shields.io/badge/package%20manager-uv-blueviolet.svg)](https://docs.astral.sh/uv/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A production-ready, full-stack CRUD (Create, Read, Update, Delete) web application built with **Python 3.13**, **FastAPI**, and **PostgreSQL**, managed by Astral's ultra-fast [`uv`](https://docs.astral.sh/uv/) package manager. Designed as an exemplary portfolio project showcasing clean architecture, parameterized database security, interactive UI, and containerized deployment.

---

## Highlights & Features

- **Interactive User Form**:
  - Details: **Name**, **Email**, **Mobile Number**, **Hobbies** (multi-tag interactive selector), **Gender**, **Date of Birth**, **Location (City/Country)**, **Bio**, and **Active Status**.
  - Client-side & server-side validation using Pydantic v2.
  - Automatic mobile number format sanitization and email normalization.
  - Duplicate detection for both email and mobile numbers.
- **Modern Responsive Dashboard UI**:
  - Built with Tailwind CSS and Plus Jakarta Sans typography.
  - Dark Mode and Light Mode with persistent toggle.
  - Key Metrics: Total Users, Active Profile Rate, Top Hobby with user count, Recent Signups.
  - Animated toast notifications for all CRUD operations.
- **Data Table with Advanced Controls**:
  - Real-time debounced search across Name, Email, Mobile, and City.
  - Filtering by Hobby, Gender, and Active status.
  - Multi-column sorting (Name, Date Created, etc.).
  - Configurable pagination.
  - User profile modal with complete metadata.
- **Developer Features**:
  - One-click **Seed Sample Data** generator (populates 10 realistic profiles for demonstrations).
  - One-click **Export to CSV**.
  - Interactive OpenAPI / Swagger documentation at `/docs`.
  - Health check endpoint at `/health` reporting live database connectivity.
- **Production Architecture**:
  - Layered pattern: Domain Models &rarr; Database & Connection Pool &rarr; Repository &rarr; Service &rarr; REST API &rarr; UI.
  - Connection pooling with `psycopg-pool` and automated schema migrations.
  - 100% parameterized queries guarding against SQL injection.
  - Docker Compose setup running both PostgreSQL and the FastAPI application.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) |
| **Runtime & Language** | Python 3.13+ |
| **Database** | PostgreSQL 16+ (with GIN indexes for array searching) |
| **Driver & Pooling** | [`psycopg 3`](https://www.psycopg.org/psycopg3/) with `psycopg-pool` |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) |
| **Frontend Styling** | [Tailwind CSS](https://tailwindcss.com/) (via CDN) |
| **Templating** | [Jinja2](https://jinja.palletsprojects.com/) |
| **Package Manager** | [`uv`](https://docs.astral.sh/uv/) (Astral) |
| **Testing** | [Pytest](https://pytest.org/) & [HTTPX](https://www.python-httpx.org/) |
| **Containerization** | Docker & Docker Compose |

---

## Quickstart with Docker Compose (Recommended)

Spin up the entire application (PostgreSQL + FastAPI Web App) with a single command:

```bash
# Clone the repository
git clone git@github.com:faiyazkhan024/python-postgresql-crud.git
cd python-postgresql-crud

# Copy environment variables
cp .env.example .env

# Build and start services
docker compose up --build
```

Once started:
- **Web UI:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

## Local Development with `uv`

### 1. Prerequisites
- Python `>= 3.13`
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- PostgreSQL running locally or via Docker

### 2. Start PostgreSQL with Docker
```bash
docker compose up postgres -d
```

### 3. Install Dependencies
```bash
uv sync --all-extras --dev
```

### 4. Run the Application
```bash
uv run python-postgresql-crud
```

---

## Project Structure

```
python-postgresql-crud/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI workflow
├── src/
│   └── python_postgresql_crud/
│       ├── __init__.py          # Package entrypoint & CLI runner
│       ├── config.py            # Environment settings (.env loader)
│       ├── database.py          # PostgreSQL connection pool & migrations
│       ├── models.py            # Pydantic validation models
│       ├── repository.py        # Parameterized SQL CRUD queries
│       ├── service.py           # Domain service & sample data seeder
│       ├── main.py              # FastAPI app & lifespan manager
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes.py        # REST API routes (/api/v1/users)
│       ├── templates/
│       │   ├── base.html        # Base HTML template with Tailwind CSS
│       │   └── index.html       # Dashboard, metrics, table, modals
│       └── static/
│           ├── css/
│           │   └── styles.css   # Custom animations & transitions
│           └── js/
│               └── app.js       # Frontend controller & fetch API
├── tests/
│   ├── __init__.py
│   ├── test_basic.py            # Smoke tests
│   ├── test_models.py           # Schema & field validation tests
│   ├── test_service.py          # Domain logic & mock repository tests
│   └── test_api.py              # FastAPI TestClient endpoint tests
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore rules
├── AGENT.md                     # Operational manual for AI coding agents
├── CONTRIBUTING.md              # Community contribution guide
├── Dockerfile                   # Multi-stage production container build
├── docker-compose.yml           # PostgreSQL + web app services
├── LICENSE                      # MIT License
└── pyproject.toml               # Project configuration & dependencies
```

---

## REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/users` | Create a new user |
| `GET` | `/api/v1/users` | List users with search, filtering, and pagination |
| `GET` | `/api/v1/users/{id}` | Get user details by ID |
| `PUT` | `/api/v1/users/{id}` | Update an existing user |
| `DELETE` | `/api/v1/users/{id}` | Delete a user by ID |
| `GET` | `/api/v1/users/stats` | Get directory metrics and top hobbies |
| `GET` | `/api/v1/users/export/csv` | Download all users as CSV |
| `POST` | `/api/v1/users/seed` | Seed realistic demo users |
| `GET` | `/health` | System and database health status |

### Example cURL: Create a User
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Faiyaz Khan",
    "email": "faiyaz@example.com",
    "mobile": "+919876543210",
    "hobbies": ["Coding", "Photography", "Chess"],
    "gender": "male",
    "date_of_birth": "1998-05-15",
    "city": "Bengaluru",
    "country": "India",
    "bio": "Software engineer building scalable backend applications.",
    "is_active": true
  }'
```

---

## Testing & Code Quality

Run tests using Pytest:
```bash
uv run pytest -v
```

Format code with Ruff:
```bash
uv run ruff format .
```

Lint with auto-fix:
```bash
uv run ruff check . --fix
```

---

## License

This project is licensed under the [MIT License](LICENSE).

Copyright &copy; 2026 [Faiyaz Khan](https://github.com/faiyazkhan024).
