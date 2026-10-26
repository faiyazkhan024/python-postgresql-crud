# AGENT.md

> Operational Guidelines and Architecture Guide for AI Coding Agents and Developers

This document serves as the primary technical specification, operational guide, and coding manual for AI agents (such as Google Antigravity, Claude Code, Cursor, GitHub Copilot) and human contributors working on **python-postgresql-crud**.

---

## 1. Project Overview & Mission

- **Project Name:** `python-postgresql-crud`
- **Description:** A simple, high-performance, and modular CRUD (Create, Read, Update, Delete) application built in Python 3.13+ interfacing with PostgreSQL.
- **Package & Dependency Manager:** [`uv`](https://docs.astral.sh/uv/) by Astral.
- **Repository URL:** `git@github.com:faiyazkhan024/python-postgresql-crud.git`
- **Default Branch:** `main`

---

## 2. Technical Stack

| Component | Technology | Description |
|---|---|---|
| **Language** | Python 3.13+ | Modern Python with standard type hinting |
| **Database** | PostgreSQL 16+ | Relational database storage |
| **Driver** | `psycopg` (v3) | Modern PostgreSQL DBAPI driver with connection pooling |
| **Validation** | `pydantic` (v2) | Schema validation and data modeling |
| **Config** | `python-dotenv` | Twelve-factor configuration via `.env` files |
| **Package Manager** | `uv` | Ultra-fast Python package and project manager |
| **Linter / Formatter**| `ruff` | Fast, unified linter and formatter |
| **Testing** | `pytest` | Test runner and assertion library |
| **Containerization** | `docker-compose` | Local containerized PostgreSQL instance |

---

## 3. Repository Architecture & Layout

When implementing or extending features, adhere to the layered architecture pattern:

```
python-postgresql-crud/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI workflow
├── src/
│   └── python_postgresql_crud/
│       ├── __init__.py          # Package entry point
│       ├── config.py            # Environment configuration & settings
│       ├── database.py          # PostgreSQL connection & pool management
│       ├── models.py            # Pydantic data models / entities
│       ├── repository.py        # Database CRUD queries (Data Access Layer)
│       └── service.py           # Business logic & orchestration
├── tests/
│   ├── __init__.py
│   ├── test_basic.py            # Smoke tests
│   └── test_crud.py             # CRUD unit & integration tests
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore patterns
├── .python-version              # Pinned Python version (3.13)
├── AGENT.md                     # This file (Agent instructions)
├── CONTRIBUTING.md              # Contribution guide
├── docker-compose.yml           # Local PostgreSQL service
├── LICENSE                      # MIT License
├── pyproject.toml               # Project metadata & tool configs
└── README.md                    # Project documentation
```

### Architectural Principles
1. **Config Layer (`config.py`)**: Loads settings from environment variables or `.env`. No other module should directly read `os.environ`.
2. **Database Layer (`database.py`)**: Manages connection pooling, lifecycle, and provides context managers for acquiring connections and transactions.
3. **Model Layer (`models.py`)**: Clean data models representing domain entities and request/response payloads.
4. **Repository Layer (`repository.py`)**: Responsible exclusively for SQL interactions (CRUD). Contains raw SQL with parameterized queries.
5. **Service Layer (`service.py`)**: Orchestrates operations, enforces business rules, and communicates with the repository.

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
  with db_pool.connection() as conn:
      with conn.cursor() as cur:
          cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
      conn.commit()
  ```
- Roll back automatically on unhandled exceptions to maintain database consistency.

### Connection Pooling
- Prefer connection pooling (`psycopg_pool.ConnectionPool`) over opening and closing a new TCP socket per query.
- Configure pool min/max sizes via environment variables (`DB_POOL_MIN_SIZE`, `DB_POOL_MAX_SIZE`).

---

## 5. Development & Tooling Commands

All commands should be executed through `uv`. Do not invoke `pip` or global Python executables directly.

### Dependency Management
```bash
# Sync dependencies with lockfile
uv sync

# Add a production dependency
uv add <package_name>

# Add a development dependency
uv add --dev <package_name>
```

### Running the Application
```bash
# Run the package script
uv run python-postgresql-crud
```

### Code Formatting & Linting
```bash
# Format code
uv run ruff format .

# Check and auto-fix linter issues
uv run ruff check . --fix
```

### Running Tests
```bash
# Run all tests
uv run pytest -v

# Run tests with output printing
uv run pytest -s
```

### Local Database with Docker
```bash
# Start PostgreSQL in background
docker compose up -d

# Stop PostgreSQL
docker compose down

# View database logs
docker compose logs -f postgres
```

---

## 6. Code Style & Engineering Standards

- **Python Version:** 3.13 syntax. Use modern union types (`int | None` instead of `Optional[int]`), standard collection types (`list[str]`, `dict[str, Any]`), and pattern matching where applicable.
- **Type Annotations:** All function parameters, return values, and module constants must be typed.
- **Error Handling:** Catch specific exceptions (`psycopg.Error`, `KeyError`, `ValueError`). Never write bare `except:`. Provide actionable error context.
- **Logging:** Use Python's built-in `logging` module rather than scattered `print()` statements in production code.

---

## 7. Instructions for Autonomous AI Agents

When tasked with modifications or feature implementations:
1. **Understand Context:** Inspect `pyproject.toml`, existing source code in `src/`, and existing tests before creating or changing files.
2. **Preserve Documentation:** Do not delete existing comments or documentation unless explicitly obsolete or requested.
3. **Verify Working State:**
   - Run `uv run ruff check .` and ensure no lint warnings remain.
   - Run `uv run ruff format .` to keep styling consistent.
   - Run `uv run pytest` to ensure all tests pass.
4. **Atomic Git Commits:** Keep changes cohesive and accompanied by clear commit messages following Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
