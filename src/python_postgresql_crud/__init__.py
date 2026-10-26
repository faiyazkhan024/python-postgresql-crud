"""python-postgresql-crud package entrypoint."""

from python_postgresql_crud.main import app, run


def main() -> None:
    """Launch the application server."""
    run()


__all__ = ["app", "main", "run"]
