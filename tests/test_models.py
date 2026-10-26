"""Unit tests for Pydantic domain models and field validation rules."""

from datetime import date, timedelta
import pytest
from pydantic import ValidationError

from python_postgresql_crud.models import GenderEnum, UserCreate, UserUpdate


def test_valid_user_create() -> None:
    """Test valid user creation with standard fields."""
    user = UserCreate(
        name="Faiyaz Khan",
        email="faiyaz@example.com",
        mobile="+919876543210",
        hobbies=["Coding", "Photography"],
        gender=GenderEnum.male,
        date_of_birth=date(1998, 5, 15),
        city="Bengaluru",
        country="India",
        bio="Software engineer.",
        is_active=True,
    )
    assert user.name == "Faiyaz Khan"
    assert user.email == "faiyaz@example.com"
    assert user.mobile == "+919876543210"
    assert user.hobbies == ["Coding", "Photography"]
    assert user.gender == GenderEnum.male
    assert user.is_active is True


def test_name_min_length_validation() -> None:
    """Ensure name with less than 2 characters fails validation."""
    with pytest.raises(ValidationError):
        UserCreate(
            name="A",
            email="valid@example.com",
            mobile="+919876543210",
            hobbies=[],
        )


def test_invalid_email_validation() -> None:
    """Ensure malformed email fails validation."""
    with pytest.raises(ValidationError):
        UserCreate(
            name="Faiyaz Khan",
            email="not-an-email",
            mobile="+919876543210",
            hobbies=[],
        )


def test_mobile_sanitization_and_validation() -> None:
    """Ensure mobile numbers with spaces and dashes are sanitized correctly."""
    user = UserCreate(
        name="Faiyaz Khan",
        email="test@example.com",
        mobile=" +91 (987) 654-3210 ",
        hobbies=[],
    )
    assert user.mobile == "+919876543210"

    with pytest.raises(ValidationError):
        UserCreate(
            name="Faiyaz Khan",
            email="test@example.com",
            mobile="123",  # Too short (< 7 digits)
            hobbies=[],
        )


def test_hobbies_comma_separated_normalization() -> None:
    """Ensure comma-separated string from HTML form is parsed, trimmed, and deduplicated."""
    user = UserCreate(
        name="Faiyaz Khan",
        email="test@example.com",
        mobile="+919876543210",
        hobbies="Coding, Reading, Coding, Gaming  ",  # type: ignore[arg-type]
    )
    assert user.hobbies == ["Coding", "Reading", "Gaming"]


def test_future_date_of_birth_rejected() -> None:
    """Ensure future date of birth is rejected."""
    future_date = date.today() + timedelta(days=5)
    with pytest.raises(ValidationError):
        UserCreate(
            name="Faiyaz Khan",
            email="test@example.com",
            mobile="+919876543210",
            hobbies=[],
            date_of_birth=future_date,
        )


def test_user_update_optional_fields() -> None:
    """Ensure UserUpdate allows partial field modifications."""
    update = UserUpdate(name="Updated Name", is_active=False)
    dumped = update.model_dump(exclude_unset=True)
    assert dumped == {"name": "Updated Name", "is_active": False}
    assert "email" not in dumped
