"""Unit tests for UserService and business rule validation."""

from datetime import datetime, timezone
import pytest

from python_postgresql_crud.models import (
    GenderEnum,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from python_postgresql_crud.service import (
    DuplicateEmailError,
    DuplicateMobileError,
    UserNotFoundError,
    UserService,
)


class MockUserRepository:
    """In-memory mock repository for fast isolated unit testing."""

    def __init__(self) -> None:
        self.users: dict[int, UserResponse] = {}
        self.next_id = 1

    def create(self, user: UserCreate) -> UserResponse:
        now = datetime.now(timezone.utc)
        record = UserResponse(
            id=self.next_id,
            name=user.name,
            email=user.email,
            mobile=user.mobile,
            hobbies=user.hobbies,
            gender=user.gender,
            date_of_birth=user.date_of_birth,
            bio=user.bio,
            city=user.city,
            country=user.country,
            is_active=user.is_active,
            created_at=now,
            updated_at=now,
        )
        self.users[self.next_id] = record
        self.next_id += 1
        return record

    def get_by_id(self, user_id: int) -> UserResponse | None:
        return self.users.get(user_id)

    def get_by_email(self, email: str) -> UserResponse | None:
        for u in self.users.values():
            if u.email.lower() == email.lower():
                return u
        return None

    def get_by_mobile(self, mobile: str) -> UserResponse | None:
        for u in self.users.values():
            if u.mobile == mobile:
                return u
        return None

    def list_users(self, **kwargs) -> tuple[list[UserResponse], int]:
        all_users = list(self.users.values())
        return all_users, len(all_users)

    def update(self, user_id: int, user_data: UserUpdate) -> UserResponse | None:
        current = self.users.get(user_id)
        if not current:
            return None
        data = current.model_dump()
        for k, v in user_data.model_dump(exclude_unset=True).items():
            data[k] = v
        data["updated_at"] = datetime.now(timezone.utc)
        updated = UserResponse.model_validate(data)
        self.users[user_id] = updated
        return updated

    def delete(self, user_id: int) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

    def get_all_for_export(self) -> list[UserResponse]:
        return list(self.users.values())


def test_service_create_user_and_duplicates() -> None:
    """Verify unique email and mobile constraints in the service layer."""
    repo = MockUserRepository()  # type: ignore[arg-type]
    service = UserService(repository=repo)  # type: ignore[arg-type]

    user_payload = UserCreate(
        name="Test User",
        email="test@example.com",
        mobile="+919876543210",
        hobbies=["Coding"],
        gender=GenderEnum.male,
    )

    created = service.create_user(user_payload)
    assert created.id == 1
    assert created.email == "test@example.com"

    # Attempting to create duplicate email must raise DuplicateEmailError
    with pytest.raises(DuplicateEmailError):
        service.create_user(
            UserCreate(
                name="Another User",
                email="test@example.com",
                mobile="+919811111111",
                hobbies=[],
            )
        )

    # Attempting to create duplicate mobile must raise DuplicateMobileError
    with pytest.raises(DuplicateMobileError):
        service.create_user(
            UserCreate(
                name="Another User",
                email="different@example.com",
                mobile="+919876543210",
                hobbies=[],
            )
        )


def test_service_get_and_delete_not_found() -> None:
    """Verify proper exception handling for non-existent user."""
    repo = MockUserRepository()  # type: ignore[arg-type]
    service = UserService(repository=repo)  # type: ignore[arg-type]

    with pytest.raises(UserNotFoundError):
        service.get_user(999)

    with pytest.raises(UserNotFoundError):
        service.delete_user(999)


def test_service_csv_export() -> None:
    """Verify that CSV export contains valid header and rows."""
    repo = MockUserRepository()  # type: ignore[arg-type]
    service = UserService(repository=repo)  # type: ignore[arg-type]

    service.create_user(
        UserCreate(
            name="Alice",
            email="alice@example.com",
            mobile="+919999999999",
            hobbies=["Reading", "Writing"],
            city="Mumbai",
        )
    )

    csv_data = service.export_csv()
    assert "ID,Name,Email,Mobile,Hobbies" in csv_data
    assert "alice@example.com" in csv_data
    assert "Reading; Writing" in csv_data
