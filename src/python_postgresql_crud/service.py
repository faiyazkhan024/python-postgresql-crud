"""Business logic and service orchestration layer for User domain."""

import csv
from datetime import date
import io
import logging
import math

from python_postgresql_crud.models import (
    GenderEnum,
    PaginatedUsersResponse,
    UserCreate,
    UserResponse,
    UserStatsResponse,
    UserUpdate,
)
from python_postgresql_crud.repository import UserRepository, user_repository

logger = logging.getLogger(__name__)


class UserNotFoundError(Exception):
    """Raised when a requested user ID does not exist."""

    pass


class DuplicateEmailError(Exception):
    """Raised when an email address is already taken."""

    pass


class DuplicateMobileError(Exception):
    """Raised when a mobile number is already taken."""

    pass


# Realistic seed dataset for showcase and testing
SAMPLE_USERS: list[dict[str, object]] = [
    {
        "name": "Aarav Sharma",
        "email": "aarav.sharma@example.com",
        "mobile": "+919876543210",
        "hobbies": ["Coding", "Chess", "Gaming"],
        "gender": GenderEnum.male,
        "date_of_birth": date(1996, 4, 12),
        "bio": "Full-stack developer who loves building distributed systems and playing blitz chess.",
        "city": "Bengaluru",
        "country": "India",
        "is_active": True,
    },
    {
        "name": "Priya Patel",
        "email": "priya.patel@example.com",
        "mobile": "+919812345678",
        "hobbies": ["Photography", "Traveling", "Writing"],
        "gender": GenderEnum.female,
        "date_of_birth": date(1998, 9, 23),
        "bio": "Landscape photographer and tech writer exploring the intersection of AI and visual arts.",
        "city": "Mumbai",
        "country": "India",
        "is_active": True,
    },
    {
        "name": "Rohan Verma",
        "email": "rohan.verma@example.com",
        "mobile": "+919923456789",
        "hobbies": ["Music", "Cycling", "Cooking"],
        "gender": GenderEnum.male,
        "date_of_birth": date(1994, 11, 5),
        "bio": "Acoustic guitarist, weekend cyclist, and sourdough bread enthusiast.",
        "city": "Pune",
        "country": "India",
        "is_active": True,
    },
    {
        "name": "Ananya Iyer",
        "email": "ananya.iyer@example.com",
        "mobile": "+919734567890",
        "hobbies": ["Reading", "Art & Design", "Podcasts"],
        "gender": GenderEnum.female,
        "date_of_birth": date(2000, 2, 18),
        "bio": "UI/UX designer focused on accessible interfaces and typography.",
        "city": "Chennai",
        "country": "India",
        "is_active": True,
    },
    {
        "name": "Kabir Mehta",
        "email": "kabir.mehta@example.com",
        "mobile": "+919645678901",
        "hobbies": ["Fitness", "Hiking", "Sports"],
        "gender": GenderEnum.male,
        "date_of_birth": date(1992, 7, 30),
        "bio": "Marathon runner and product manager building fintech products.",
        "city": "Delhi",
        "country": "India",
        "is_active": False,
    },
    {
        "name": "Zoya Akhtar",
        "email": "zoya.akhtar@example.com",
        "mobile": "+919556789012",
        "hobbies": ["Gardening", "Cooking", "Reading"],
        "gender": GenderEnum.female,
        "date_of_birth": date(1997, 12, 14),
        "bio": "Urban gardener cultivating microgreens and experimenting with Mediterranean cuisine.",
        "city": "Hyderabad",
        "country": "India",
        "is_active": True,
    },
    {
        "name": "David Miller",
        "email": "david.miller@example.com",
        "mobile": "+14155552671",
        "hobbies": ["Coding", "Podcasts", "Cycling"],
        "gender": GenderEnum.male,
        "date_of_birth": date(1991, 3, 8),
        "bio": "Backend engineer specializing in PostgreSQL tuning and asynchronous architectures.",
        "city": "San Francisco",
        "country": "United States",
        "is_active": True,
    },
    {
        "name": "Elena Rostova",
        "email": "elena.rostova@example.com",
        "mobile": "+442079460912",
        "hobbies": ["Art & Design", "Photography", "Traveling"],
        "gender": GenderEnum.female,
        "date_of_birth": date(1995, 6, 25),
        "bio": "Visual artist and creative director working between London and Berlin.",
        "city": "London",
        "country": "United Kingdom",
        "is_active": True,
    },
    {
        "name": "Siddharth Rao",
        "email": "siddharth.rao@example.com",
        "mobile": "+919467890123",
        "hobbies": ["Gaming", "Coding", "Music"],
        "gender": GenderEnum.male,
        "date_of_birth": date(2001, 8, 19),
        "bio": "Indie game developer experimenting with procedural generation in Rust and Python.",
        "city": "Bengaluru",
        "country": "India",
        "is_active": True,
    },
    {
        "name": "Meera Joshi",
        "email": "meera.joshi@example.com",
        "mobile": "+919378901234",
        "hobbies": ["Hiking", "Writing", "Fitness"],
        "gender": GenderEnum.female,
        "date_of_birth": date(1999, 10, 3),
        "bio": "Trekking guide and travel blogger documenting Himalayan expeditions.",
        "city": "Dehradun",
        "country": "India",
        "is_active": True,
    },
]


class UserService:
    """Service layer enforcing validation rules and domain logic."""

    def __init__(self, repository: UserRepository = user_repository) -> None:
        self.repo = repository

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a user after ensuring unique constraints on email and mobile."""
        if self.repo.get_by_email(user_data.email):
            raise DuplicateEmailError(
                f"A user with email '{user_data.email}' already exists."
            )

        if self.repo.get_by_mobile(user_data.mobile):
            raise DuplicateMobileError(
                f"A user with mobile '{user_data.mobile}' already exists."
            )

        logger.info("Creating user with email: %s", user_data.email)
        return self.repo.create(user_data)

    def get_user(self, user_id: int) -> UserResponse:
        """Fetch user by ID or raise UserNotFoundError."""
        user = self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} was not found.")
        return user

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
    ) -> PaginatedUsersResponse:
        """Fetch filtered and paginated user records with navigation metrics."""
        items, total = self.repo.list_users(
            search=search,
            hobby=hobby,
            gender=gender,
            is_active=is_active,
            city=city,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return PaginatedUsersResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

    def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        """Update an existing user, verifying uniqueness if email or mobile changed."""
        current = self.get_user(user_id)

        # Check duplicate email if modified
        if user_data.email and user_data.email.lower() != current.email.lower():
            existing = self.repo.get_by_email(user_data.email)
            if existing and existing.id != user_id:
                raise DuplicateEmailError(
                    f"Email '{user_data.email}' is already taken by another user."
                )

        # Check duplicate mobile if modified
        if user_data.mobile and user_data.mobile != current.mobile:
            existing_m = self.repo.get_by_mobile(user_data.mobile)
            if existing_m and existing_m.id != user_id:
                raise DuplicateMobileError(
                    f"Mobile '{user_data.mobile}' is already registered to another user."
                )

        updated = self.repo.update(user_id, user_data)
        if not updated:
            raise UserNotFoundError(f"User with ID {user_id} was not found.")
        return updated

    def delete_user(self, user_id: int) -> None:
        """Delete user or raise UserNotFoundError if record does not exist."""
        # Ensure user exists before deleting
        self.get_user(user_id)
        self.repo.delete(user_id)
        logger.info("Deleted user with ID %s", user_id)

    def get_stats(self) -> UserStatsResponse:
        """Fetch dashboard statistics."""
        return self.repo.get_statistics()

    def export_csv(self) -> str:
        """Export all user data as formatted CSV string."""
        users = self.repo.get_all_for_export()
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(
            [
                "ID",
                "Name",
                "Email",
                "Mobile",
                "Hobbies",
                "Gender",
                "Date of Birth",
                "Bio",
                "City",
                "Country",
                "Status",
                "Created At",
                "Updated At",
            ]
        )

        for u in users:
            writer.writerow(
                [
                    u.id,
                    u.name,
                    u.email,
                    u.mobile,
                    "; ".join(u.hobbies),
                    u.gender.value if hasattr(u.gender, "value") else str(u.gender),
                    u.date_of_birth.isoformat() if u.date_of_birth else "",
                    u.bio or "",
                    u.city or "",
                    u.country or "",
                    "Active" if u.is_active else "Inactive",
                    u.created_at.isoformat(),
                    u.updated_at.isoformat(),
                ]
            )

        return output.getvalue()

    def seed_sample_data(self) -> int:
        """Populate database with sample realistic users. Return number of inserted users."""
        users_to_insert = [UserCreate.model_validate(raw) for raw in SAMPLE_USERS]
        count = self.repo.bulk_create(users_to_insert)
        logger.info("Seeded %d sample users into database.", count)
        return count


# Global service instance
user_service = UserService()
