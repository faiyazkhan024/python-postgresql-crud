# AGENT.md

> Operational Guidelines and Architecture Guide for AI Coding Agents and Developers

This document serves as the primary technical specification, operational guide, and coding manual for AI agents (such as Google Antigravity, Claude Code, Cursor, GitHub Copilot) and human contributors working on **python-postgresql-crud**.

---

## 1. Project Overview & Mission

- **Project Name:** `python-postgresql-crud`
- **Description:** A production-grade, full-stack CRUD application built with Python 3.13, FastAPI, and PostgreSQL. Features form submission (Name, Mobile, Email, Hobbies, Gender, Date of Birth, Bio, Location), live search, sorting, filtering, automated schema migrations, and Docker Compose orchestration.
- **Package & Dependency Manager:** [`uv`](https://docs.astral.sh/uv/) by Astral.
- **Repository URL:** `git@github.com:faiyazkhan024/python-postgresql-crud.git`
- **Default Branch:** `main`

---

## 2. Technical Stack

| Component | Technology | Description |
|---|---|---|
| **Language** | Python 3.13+ | Modern Python with standard type hinting |
| **Framework** | FastAPI | High-performance asynchronous REST API framework |
| **Server** | Uvicorn | ASGI web server implementation |
| **Database** | PostgreSQL 16+ | Relational database with GIN indexing for array queries |
| **Driver & Pooling**| `psycopg` (v3) + `psycopg-pool` | Modern DBAPI driver with connection pooling |
| **Validation** | Pydantic v2 | Strict schema validation and data parsing |
| **Templates** | Jinja2 | Server-side rendered template layout |
| **Frontend UI** | Tailwind CSS + Vanilla JS | Responsive modern UI with dark mode and toasts |
| **Package Manager**| `uv` | Ultra-fast package and project manager |
| **Linter / Formatter**| `ruff` | Fast Python linter and formatter |
| **Testing** | `pytest` + `httpx` | Unit and integration test suite |
| **Containerization**| Docker & Docker Compose | Multi-container setup (PostgreSQL + FastAPI Web) |

---

## 3. Repository Architecture & Layout

```
python-postgresql-crud/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI workflow
├── src/
│   └── python_postgresql_crud/
│       ├── __init__.py          # Package entry point
│       ├── config.py            # Environment configuration & settings
│       ├── database.py          # PostgreSQL connection pool & schema migrations
│       ├── models.py            # Pydantic data models & validation schemas
│       ├── repository.py        # Database CRUD queries (Data Access Layer)
│       ├── service.py           # Business logic, CSV export, sample data seeder
│       ├── main.py              # FastAPI application, lifespan, routes & UI
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes.py        # REST API endpoints (/api/v1/users)
│       ├── templates/
│       │   ├── base.html        # Base HTML with Tailwind CSS, navbar & toast
│       │   └── index.html       # Dashboard, metrics, table, modals
│       └── static/
│           ├── css/
│           │   └── styles.css   # Custom styling, animations, scrollbars
│           └── js/
│               └── app.js       # Frontend controller (fetch API, live search, modals)
├── tests/
│   ├── __init__.py
│   ├── test_basic.py            # Smoke tests
│   ├── test_models.py           # Pydantic schema validation tests
│   ├── test_service.py          # Business logic and mock repository tests
│   └── test_api.py              # FastAPI TestClient endpoint tests
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore patterns
├── .python-version              # Pinned Python version (3.13)
├── AGENT.md                     # This file (Agent instructions)
├── CONTRIBUTING.md              # Contribution guide
├── Dockerfile                   # Multi-stage production container build
├── docker-compose.yml           # PostgreSQL + web app services
├── LICENSE                      # MIT License
├── pyproject.toml               # Project metadata & tool configs
└── README.md                    # Project documentation
```

### Architectural Principles
1. **Config Layer (`config.py`)**: Loads settings from environment variables or `.env`. No other module should directly read `os.environ`.
2. **Database Layer (`database.py`)**: Manages connection pooling, lifecycle, and provides context managers for acquiring connections and transactions. Applies DDL migration on startup.
3. **Model Layer (`models.py`)**: Clean data models representing domain entities and request/response payloads with field sanitization.
4. **Repository Layer (`repository.py`)**: Responsible exclusively for SQL interactions (CRUD). Uses parameterized queries to prevent SQL injection.
5. **Service Layer (`service.py`)**: Enforces uniqueness constraints (email, mobile), business rules, CSV export formatting, and seed data generation.
6. **API Layer (`api/routes.py`)**: Exposes RESTful endpoints conforming to HTTP status conventions.
7. **Presentation Layer (`templates/` & `static/`)**: Clean responsive interface rendered via Jinja2 with modern Tailwind CSS and asynchronous JavaScript fetch calls.

---

## 4. Database & SQL Guidelines

### Security: Strict SQL Parameterization
- **NEVER** format, interpolate, or concatenate strings into SQL queries:
  ```python
  # BAD - Vulnerable to SQL injection!
  cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")

  # GOOD - Parameterized with placeholders
  cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
  ```

### Transaction Management
- Always use context managers to handle connections and transactions:
  ```python
  with db.cursor() as cur:
      cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
  ```

---

## 5. Development & Tooling Commands

All commands should be executed through `uv`.

```bash
# Sync dependencies
uv sync --all-extras --dev

# Run application locally
uv run python-postgresql-crud

# Format code
uv run ruff format .

# Check and fix lint issues
uv run ruff check . --fix

# Run tests
uv run pytest -v

# Run full stack with Docker Compose
docker compose up --build
```

---

## 6. Instructions for Autonomous AI Agents

1. **Understand Context:** Inspect `models.py`, `repository.py`, and `service.py` before modifying any domain rules.
2. **Preserve Documentation:** Keep comments and docstrings intact.
3. **Verify Working State:**
   - Run `uv run ruff check .` and ensure no lint warnings remain.
   - Run `uv run pytest` to ensure all tests pass.
4. **Atomic Git Commits:** Keep changes cohesive and accompanied by clear commit messages following Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
