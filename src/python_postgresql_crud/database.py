"""Database connection pool and schema migration manager using psycopg3."""

from collections.abc import Generator
from contextlib import contextmanager
import logging
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from python_postgresql_crud.config import get_settings

logger = logging.getLogger(__name__)

# Schema DDL definitions
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    mobile VARCHAR(25) NOT NULL,
    hobbies TEXT[] NOT NULL DEFAULT '{}',
    gender VARCHAR(30) NOT NULL DEFAULT 'prefer_not_to_say',
    date_of_birth DATE,
    bio TEXT,
    city VARCHAR(100),
    country VARCHAR(100) DEFAULT 'India',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_mobile ON users(mobile);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_hobbies ON users USING GIN (hobbies);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""


class DatabaseManager:
    """Manages the PostgreSQL connection pool and lifecycle."""

    def __init__(self) -> None:
        self._pool: ConnectionPool | None = None

    def initialize_pool(self) -> None:
        """Create and start the connection pool if not already active."""
        if self._pool is not None and not self._pool.closed:
            return

        settings = get_settings()
        logger.info(
            "Initializing PostgreSQL connection pool to %s:%s/%s (min: %s, max: %s)",
            settings.POSTGRES_HOST,
            settings.POSTGRES_PORT,
            settings.POSTGRES_DB,
            settings.DB_POOL_MIN_SIZE,
            settings.DB_POOL_MAX_SIZE,
        )

        try:
            self._pool = ConnectionPool(
                conninfo=settings.db_url,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                timeout=settings.DB_TIMEOUT_SECONDS,
                kwargs={"row_factory": dict_row},
                open=True,
            )
            logger.info("Connection pool successfully created and opened.")
        except Exception as e:
            logger.error("Failed to connect to PostgreSQL database: %s", e)
            raise

    def close_pool(self) -> None:
        """Close all connections and tear down the pool."""
        if self._pool is not None and not self._pool.closed:
            logger.info("Closing database connection pool.")
            self._pool.close()
            self._pool = None

    @property
    def is_connected(self) -> bool:
        """Check if connection pool is active."""
        return self._pool is not None and not self._pool.closed

    @contextmanager
    def connection(self) -> Generator[psycopg.Connection[dict[str, Any]], None, None]:
        """Acquire a connection from the pool as a context manager."""
        if self._pool is None or self._pool.closed:
            self.initialize_pool()

        assert self._pool is not None
        with self._pool.connection() as conn:
            yield conn

    @contextmanager
    def cursor(self) -> Generator[psycopg.Cursor[dict[str, Any]], None, None]:
        """Acquire a cursor with transaction autocommit/rollback management."""
        with self.connection() as conn:
            with conn.cursor() as cur:
                try:
                    yield cur
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise

    def init_db(self) -> None:
        """Apply the initial schema migrations and create necessary tables/indexes."""
        logger.info("Checking and applying schema migrations...")
        with self.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        logger.info("Schema migration completed successfully.")


# Global singleton database manager
db = DatabaseManager()
