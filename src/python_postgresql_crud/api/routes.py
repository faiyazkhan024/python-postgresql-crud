"""REST API routes for user CRUD operations and metrics."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import PlainTextResponse

from python_postgresql_crud.models import (
    GenderEnum,
    PaginatedUsersResponse,
    UserCreate,
    UserResponse,
    UserStatsResponse,
    UserUpdate,
)
from python_postgresql_crud.service import (
    DuplicateEmailError,
    DuplicateMobileError,
    UserNotFoundError,
    user_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Registers a new user record with validation for unique email, mobile, and hobby lists.",
)
def create_user(payload: UserCreate) -> UserResponse:
    """Register a new user."""
    try:
        return user_service.create_user(payload)
    except (DuplicateEmailError, DuplicateMobileError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("Failed to create user: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user record.",
        ) from exc


@router.get(
    "",
    response_model=PaginatedUsersResponse,
    status_code=status.HTTP_200_OK,
    summary="List and filter users",
    description="Returns a paginated list of users supporting search, hobby, gender, city, and active status filters.",
)
def list_users(
    search: str | None = Query(
        default=None,
        description="Search substring across name, email, mobile, or city",
    ),
    hobby: str | None = Query(
        default=None,
        description="Filter by specific hobby (e.g., Coding, Photography)",
    ),
    gender: GenderEnum | None = Query(
        default=None,
        description="Filter by gender",
    ),
    is_active: bool | None = Query(
        default=None,
        description="Filter by active status",
    ),
    city: str | None = Query(
        default=None,
        description="Filter by city",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of items per page",
    ),
    sort_by: str = Query(
        default="created_at",
        description="Field to sort by (id, name, email, city, created_at, updated_at)",
    ),
    sort_order: str = Query(
        default="desc",
        regex="^(asc|desc)$",
        description="Sort direction (asc or desc)",
    ),
) -> PaginatedUsersResponse:
    """Retrieve users matching criteria."""
    try:
        gender_val = gender.value if gender else None
        return user_service.list_users(
            search=search,
            hobby=hobby,
            gender=gender_val,
            is_active=is_active,
            city=city,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except Exception as exc:
        logger.error("Error listing users: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users.",
        ) from exc


@router.get(
    "/stats",
    response_model=UserStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user directory metrics",
    description="Returns aggregated metrics including total users, active count, top hobbies, and recent signups.",
)
def get_user_stats() -> UserStatsResponse:
    """Fetch user statistics."""
    try:
        return user_service.get_stats()
    except Exception as exc:
        logger.error("Error fetching statistics: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute directory statistics.",
        ) from exc


@router.get(
    "/export/csv",
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK,
    summary="Export all users to CSV",
    description="Generates and streams a CSV export file containing all user records.",
)
def export_users_csv() -> PlainTextResponse:
    """Generate downloadable CSV file of all users."""
    try:
        csv_data = user_service.export_csv()
        return PlainTextResponse(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=users_export.csv"},
        )
    except Exception as exc:
        logger.error("Error exporting users to CSV: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export users.",
        ) from exc


@router.post(
    "/seed",
    status_code=status.HTTP_200_OK,
    summary="Seed sample users",
    description="Inserts realistic sample records for demonstration and portfolio showcasing.",
)
def seed_sample_users() -> dict[str, Any]:
    """Seed sample database entries."""
    try:
        count = user_service.seed_sample_data()
        return {
            "success": True,
            "message": f"Successfully seeded {count} sample users into the database.",
            "count": count,
        }
    except Exception as exc:
        logger.error("Error seeding sample data: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to seed sample users.",
        ) from exc


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a user by ID",
    description="Retrieves a single user's detailed information by primary key.",
)
def get_user(user_id: int) -> UserResponse:
    """Retrieve user details."""
    try:
        return user_service.get_user(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("Error fetching user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user.",
        ) from exc


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a user",
    description="Updates one or more fields of an existing user record.",
)
def update_user(user_id: int, payload: UserUpdate) -> UserResponse:
    """Update user information."""
    try:
        return user_service.update_user(user_id, payload)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (DuplicateEmailError, DuplicateMobileError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("Error updating user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user.",
        ) from exc


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Permanently removes a user record from the database.",
)
def delete_user(user_id: int) -> None:
    """Delete user record."""
    try:
        user_service.delete_user(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("Error deleting user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user.",
        ) from exc
