# Contributing to python-postgresql-crud

Thank you for considering contributing to `python-postgresql-crud`! We welcome contributions from the community.

## Code of Conduct

Please be respectful, constructive, and considerate when communicating in issues, pull requests, and discussions.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone git@github.com:<your-username>/python-postgresql-crud.git
   cd python-postgresql-crud
   ```
3. **Ensure prerequisites are installed**:
   - Python `>= 3.13`
   - [`uv`](https://docs.astral.sh/uv/) package manager
   - PostgreSQL 16+ or Docker

4. **Install project dependencies**:
   ```bash
   uv sync --all-extras --dev
   ```

5. **Start PostgreSQL database** (using Docker Compose):
   ```bash
   docker compose up -d
   ```

## Development Workflow

### Creating a Branch
Create a descriptive feature branch:
```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/issue-description
```

### Code Style & Quality
We use [Ruff](https://docs.astral.sh/ruff/) for formatting and linting.

```bash
# Format code
uv run ruff format .

# Check and auto-fix linting issues
uv run ruff check . --fix
```

### Running Tests
Write tests for any new features or bug fixes.
```bash
uv run pytest
```

### Commit Messages
We encourage [Conventional Commits](https://www.conventionalcommits.org/):
- `feat: add user update repository method`
- `fix: handle closed database connection pool`
- `docs: update setup instructions in README`
- `test: add integration test for user deletion`
- `refactor: extract connection management context manager`

## Submitting a Pull Request

1. Push your branch to your GitHub fork:
   ```bash
   git push origin feature/your-feature-name
   ```
2. Open a Pull Request against the `main` branch of `faiyazkhan024/python-postgresql-crud`.
3. Provide a clear description of the changes made, relevant issue numbers, and how you tested the code.
4. Ensure all CI checks pass.
