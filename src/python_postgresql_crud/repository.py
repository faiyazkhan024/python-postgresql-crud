"""Repository layer implementing parameterized CRUD operations on PostgreSQL."""

import logging
from typing import Any

from python_postgresql_crud.database import db
from python_postgresql_crud.models import (
    TopHobby,
    UserCreate,
    UserResponse,
    UserStatsResponse,
    UserUpdate,
)

logger = logging.getLogger(__name__)

# Allowed sort columns to guard against SQL injection in ORDER BY
ALLOWED_SORT_COLUMNS = {
    "id": "id",
    "name": "name",
    "email": "email",
    "mobile": "mobile",
    "city": "city",
    "created_at": "created_at",
    "updated_at": "updated_at",
}


class UserRepository:
    """PostgreSQL Data Access Object (DAO) for User entity."""

    def __init__(self) -> None:
        self.db = db

    def create(self, user: UserCreate) -> UserResponse:
        """Insert a new user record and return the created entity."""
        query = """
            INSERT INTO users (
                name, email, mobile, hobbies, gender,
                date_of_birth, bio, city, country, is_active
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            RETURNING *;
        """
        params = (
            user.name,
            user.email,
            user.mobile,
            user.hobbies,
            user.gender.value if hasattr(user.gender, "value") else str(user.gender),
            user.date_of_birth,
            user.bio,
            user.city,
            user.country,
            user.is_active,
        )

        with self.db.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            assert row is not None
            return UserResponse.model_validate(row)

    def get_by_id(self, user_id: int) -> UserResponse | None:
        """Fetch a single user by primary key ID."""
        query = "SELECT * FROM users WHERE id = %s;"
        with self.db.cursor() as cur:
            cur.execute(query, (user_id,))
            row = cur.fetchone()
            if not row:
                return None
            return UserResponse.model_validate(row)

    def get_by_email(self, email: str) -> UserResponse | None:
        """Fetch a single user by email address (case-insensitive)."""
        query = "SELECT * FROM users WHERE LOWER(email) = LOWER(%s);"
        with self.db.cursor() as cur:
            cur.execute(query, (email.strip(),))
            row = cur.fetchone()
            if not row:
                return None
            return UserResponse.model_validate(row)

    def get_by_mobile(self, mobile: str) -> UserResponse | None:
        """Fetch a single user by mobile number."""
        query = "SELECT * FROM users WHERE mobile = %s;"
        with self.db.cursor() as cur:
            cur.execute(query, (mobile.strip(),))
            row = cur.fetchone()
            if not row:
                return None
            return UserResponse.model_validate(row)

    def list_users(
        self,
        search: str | None = None,
        hobby: str | None = None,
        gender: str | None = None,
        is_active: bool | None = None,
        city: str | None = None,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[UserResponse], int]:
        """List users with dynamic filtering, sorting, and pagination."""
        where_clauses: list[str] = []
        params: list[Any] = []

        if search and search.strip():
            term = f"%{search.strip()}%"
            where_clauses.append(
                "(name ILIKE %s OR email ILIKE %s OR mobile ILIKE %s OR city ILIKE %s)"
            )
            params.extend([term, term, term, term])

        if hobby and hobby.strip():
            where_clauses.append("%s = ANY(hobbies)")
            params.append(hobby.strip())

        if gender and gender.strip():
            where_clauses.append("gender = %s")
            params.append(gender.strip())

        if is_active is not None:
            where_clauses.append("is_active = %s")
            params.append(is_active)

        if city and city.strip():
            where_clauses.append("city ILIKE %s")
            params.append(f"%{city.strip()}%")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Validate order parameters
        safe_sort = ALLOWED_SORT_COLUMNS.get(sort_by.lower(), "created_at")
        safe_direction = "ASC" if sort_order.lower() == "asc" else "DESC"

        # Calculate offset
        offset = max(0, (page - 1) * page_size)

        # Count total matching rows
        count_query = f"SELECT COUNT(*) AS total FROM users {where_sql};"

        # Select paginated rows
        select_query = f"""
            SELECT * FROM users
            {where_sql}
            ORDER BY {safe_sort} {safe_direction}
            LIMIT %s OFFSET %s;
        """

        with self.db.cursor() as cur:
            cur.execute(count_query, params)
            count_row = cur.fetchone()
            total = count_row["total"] if count_row else 0

            # Execute paginated select
            cur.execute(select_query, params + [page_size, offset])
            rows = cur.fetchall()
            items = [UserResponse.model_validate(r) for r in rows]

            return items, total

    def update(self, user_id: int, user_data: UserUpdate) -> UserResponse | None:
        """Update selected fields of an existing user and return the updated entity."""
        update_dict = user_data.model_dump(exclude_unset=True)
        if not update_dict:
            return self.get_by_id(user_id)

        set_clauses: list[str] = []
        params: list[Any] = []

        for field, value in update_dict.items():
            if field == "gender" and value is not None:
                val = value.value if hasattr(value, "value") else str(value)
            else:
                val = value

            set_clauses.append(f"{field} = %s")
            params.append(val)

        params.append(user_id)
        query = f"""
            UPDATE users
            SET {', '.join(set_clauses)}
            WHERE id = %s
            RETURNING *;
        """

        with self.db.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            if not row:
                return None
            return UserResponse.model_validate(row)

    def delete(self, user_id: int) -> bool:
        """Delete a user record by ID. Returns True if deleted, False otherwise."""
        query = "DELETE FROM users WHERE id = %s RETURNING id;"
        with self.db.cursor() as cur:
            cur.execute(query, (user_id,))
            row = cur.fetchone()
            return row is not None

    def get_statistics(self) -> UserStatsResponse:
        """Aggregate high-level user statistics for the dashboard."""
        summary_query = """
            SELECT
                COUNT(*) AS total_users,
                COUNT(*) FILTER (WHERE is_active = TRUE) AS active_users,
                COUNT(*) FILTER (WHERE is_active = FALSE) AS inactive_users,
                COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') AS recent_users_count,
                COUNT(DISTINCT city) AS total_cities
            FROM users;
        """

        hobbies_query = """
            SELECT unnest(hobbies) AS hobby, COUNT(*) AS count
            FROM users
            GROUP BY hobby
            ORDER BY count DESC
            LIMIT 5;
        """

        with self.db.cursor() as cur:
            cur.execute(summary_query)
            summary = cur.fetchone() or {}

            cur.execute(hobbies_query)
            hobby_rows = cur.fetchall()

            top_hobbies = [
                TopHobby(hobby=row["hobby"], count=row["count"])
                for row in hobby_rows
                if row.get("hobby")
            ]

            return UserStatsResponse(
                total_users=summary.get("total_users", 0),
                active_users=summary.get("active_users", 0),
                inactive_users=summary.get("inactive_users", 0),
                recent_users_count=summary.get("recent_users_count", 0),
                total_cities=summary.get("total_cities", 0),
                top_hobbies=top_hobbies,
            )

    def get_all_for_export(self) -> list[UserResponse]:
        """Fetch all users sorted by ID for CSV/JSON export."""
        query = "SELECT * FROM users ORDER BY id ASC;"
        with self.db.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return [UserResponse.model_validate(r) for r in rows]

    def bulk_create(self, users: list[UserCreate]) -> int:
        """Insert multiple users, ignoring duplicate email constraints. Return count."""
        if not users:
            return 0

        query = """
            INSERT INTO users (
                name, email, mobile, hobbies, gender,
                date_of_birth, bio, city, country, is_active
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            ON CONFLICT (email) DO NOTHING
            RETURNING id;
        """

        inserted_count = 0
        with self.db.cursor() as cur:
            for user in users:
                params = (
                    user.name,
                    user.email,
                    user.mobile,
                    user.hobbies,
                    user.gender.value
                    if hasattr(user.gender, "value")
                    else str(user.gender),
                    user.date_of_birth,
                    user.bio,
                    user.city,
                    user.country,
                    user.is_active,
                )
                cur.execute(query, params)
                if cur.fetchone():
                    inserted_count += 1

        return inserted_count


# Global repository instance
user_repository = UserRepository()
