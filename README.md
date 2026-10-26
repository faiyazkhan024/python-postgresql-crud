# python-postgresql-crud

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![Package Manager](https://img.shields.io/badge/package%20manager-uv-blueviolet.svg)](https://docs.astral.sh/uv/)
[![Database](https://img.shields.io/badge/database-PostgreSQL%2016%2B-336791.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A clean, modern, and production-ready Python application implementing CRUD (Create, Read, Update, Delete) operations against a PostgreSQL database. Managed with Astral's ultra-fast [`uv`](https://docs.astral.sh/uv/) package and project manager.

---

## Features

- **Full CRUD Support**: Complete implementation of Create, Read, Update, and Delete data operations.
- **Modern Database Driver**: Utilizes `psycopg` (v3) with native connection pooling for high performance and reliability.
- **SQL Injection Prevention**: 100% parameterized queries.
- **Type-Safe Validation**: Data schemas validated using `pydantic`.
- **Environment-Driven Configuration**: Flexible 12-factor configuration using `.env` files via `python-dotenv`.
- **Docker Compose Ready**: One-command local PostgreSQL database setup with persistent volume storage and healthchecks.
- **Blazing Fast Tooling**: Managed with Astral's `uv` for dependency management and `ruff` for linting and formatting.
- **Automated CI/CD**: Pre-configured GitHub Actions workflow for linting, formatting, and automated testing.

---

## Tech Stack

- **Language:** Python `>= 3.13`
- **Database:** PostgreSQL `16+`
- **Driver / Pooling:** `psycopg[binary,pool]`
- **Validation:** `pydantic`
- **Dependency Manager:** `uv`
- **Linter & Formatter:** `ruff`
- **Testing:** `pytest`
- **Containerization:** Docker & Docker Compose

---

## Project Structure

```
python-postgresql-crud/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI workflow
├── src/
│   └── python_postgresql_crud/
│       ├── __init__.py          # Entry point and CLI runner
│       ├── config.py            # App & database configuration
│       ├── database.py          # PostgreSQL connection & pool manager
│       ├── models.py            # Pydantic data schemas
│       ├── repository.py        # SQL queries & CRUD data access layer
│       └── service.py           # Core business logic
├── tests/
│   ├── __init__.py
│   ├── test_basic.py            # Smoke tests
│   └── test_crud.py             # CRUD functionality tests
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore rules
├── .python-version              # Python version lock (3.13)
├── AGENT.md                     # Instructions and guidelines for AI agents
├── CONTRIBUTING.md              # Guidelines for contributing
├── docker-compose.yml           # Local PostgreSQL container service
├── LICENSE                      # MIT License
├── pyproject.toml               # Project metadata & tool configuration
└── README.md                    # Project documentation
```

---

## Getting Started

### Prerequisites

- **Python 3.13+**
- [**uv**](https://docs.astral.sh/uv/getting-started/installation/) (Astral's fast Python package manager)
- [**Docker & Docker Compose**](https://docs.docker.com/get-docker/) (recommended for local PostgreSQL) or a running PostgreSQL server.

### 1. Clone the Repository

```bash
git clone git@github.com:faiyazkhan024/python-postgresql-crud.git
cd python-postgresql-crud
```

### 2. Configure Environment Variables

Copy the example environment configuration:

```bash
cp .env.example .env
```

Adjust the credentials in `.env` if necessary.

### 3. Start the PostgreSQL Database

Start the database container using Docker Compose:

```bash
docker compose up -d
```

Check that the container is healthy:

```bash
docker compose ps
```

### 4. Install Dependencies

Install project dependencies into a virtual environment using `uv`:

```bash
uv sync --all-extras --dev
```

### 5. Run the Application

Execute the application entry point:

```bash
uv run python-postgresql-crud
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `POSTGRES_HOST` | Database host address | `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |
| `POSTGRES_DB` | Database name | `crud_db` |
| `POSTGRES_USER` | Database username | `postgres` |
| `POSTGRES_PASSWORD` | Database user password | `postgres` |
| `DATABASE_URL` | Full database connection URI | `postgresql://postgres:postgres@localhost:5432/crud_db` |
| `DB_POOL_MIN_SIZE` | Minimum connections in pool | `1` |
| `DB_POOL_MAX_SIZE` | Maximum connections in pool | `10` |
| `APP_ENV` | Environment name | `development` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

---

## Development & Code Quality

### Format Code
Format Python files according to project standards:
```bash
uv run ruff format .
```

### Linting
Analyze and auto-fix code style issues:
```bash
uv run ruff check . --fix
```

### Running Tests
Execute the test suite with Pytest:
```bash
uv run pytest -v
```

---

## AI Agent Integration

This repository includes a dedicated [`AGENT.md`](AGENT.md) specification that defines coding conventions, transaction handling rules, security standards, and workflow rules for AI coding assistants (such as Google Antigravity, Claude Code, Cursor, and Copilot).

---

## Contributing

Contributions, bug reports, and suggestions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) guide before submitting a pull request.

---

## License

This project is licensed under the terms of the [MIT License](LICENSE).

Copyright (c) 2026 [Faiyaz Khan](https://github.com/faiyazkhan024).
