"""Data models and validation schemas using Pydantic v2."""

from datetime import date, datetime
from enum import Enum
import re
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class GenderEnum(str, Enum):
    """User gender options."""

    male = "male"
    female = "female"
    non_binary = "non_binary"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"


# Popular hobbies list for easy suggestions and validation
POPULAR_HOBBIES = [
    "Reading",
    "Coding",
    "Gaming",
    "Photography",
    "Traveling",
    "Music",
    "Cooking",
    "Sports",
    "Fitness",
    "Art & Design",
    "Writing",
    "Gardening",
    "Hiking",
    "Podcasts",
    "Cycling",
]


class UserBase(BaseModel):
    """Base user schema containing shared attributes and strict validators."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the user",
        examples=["Faiyaz Khan"],
    )
    email: EmailStr = Field(
        ...,
        max_length=255,
        description="Valid and unique email address",
        examples=["faiyaz@example.com"],
    )
    mobile: str = Field(
        ...,
        min_length=7,
        max_length=20,
        description="Mobile or phone number (7-15 digits, optional + prefix)",
        examples=["+919876543210"],
    )
    hobbies: list[str] = Field(
        default_factory=list,
        description="List of personal hobbies and interests",
        examples=[["Coding", "Reading", "Photography"]],
    )
    gender: GenderEnum = Field(
        default=GenderEnum.prefer_not_to_say,
        description="Gender identity",
    )
    date_of_birth: date | None = Field(
        default=None,
        description="User's date of birth (YYYY-MM-DD)",
        examples=["1998-05-15"],
    )
    bio: str | None = Field(
        default=None,
        max_length=500,
        description="Short biography or personal notes",
        examples=["Software engineer passionate about databases and open-source."],
    )
    city: str | None = Field(
        default=None,
        max_length=100,
        description="City of residence",
        examples=["Bengaluru"],
    )
    country: str | None = Field(
        default="India",
        max_length=100,
        description="Country of residence",
        examples=["India"],
    )
    is_active: bool = Field(
        default=True,
        description="Whether the user profile is active",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return clean

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        clean = re.sub(r"[\s\-\(\)]", "", v.strip())
        if not re.match(r"^\+?[0-9]{7,15}$", clean):
            raise ValueError(
                "Mobile number must contain between 7 and 15 digits, optionally prefixed with '+'"
            )
        return clean

    @field_validator("hobbies", mode="before")
    @classmethod
    def normalize_hobbies(cls, v: Any) -> list[str]:
        """Support both list of strings and comma-separated string from forms."""
        if isinstance(v, str):
            raw_items = v.split(",")
        elif isinstance(v, list):
            raw_items = v
        elif v is None:
            return []
        else:
            raise ValueError("Hobbies must be a list of strings or comma-separated text")

        cleaned: list[str] = []
        for item in raw_items:
            if isinstance(item, str):
                s = item.strip()
                if s and s not in cleaned:
                    cleaned.append(s)
        return cleaned

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date | None) -> date | None:
        if v and v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v


class UserCreate(UserBase):
    """Payload schema for creating a new user record."""

    pass


class UserUpdate(BaseModel):
    """Payload schema for partially or fully updating an existing user record."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=255)
    mobile: str | None = Field(default=None, min_length=7, max_length=20)
    hobbies: list[str] | None = None
    gender: GenderEnum | None = None
    date_of_birth: date | None = None
    bio: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name_opt(cls, v: str | None) -> str | None:
        if v is not None:
            clean = v.strip()
            if len(clean) < 2:
                raise ValueError("Name must be at least 2 characters long")
            return clean
        return v

    @field_validator("email")
    @classmethod
    def validate_email_opt(cls, v: str | None) -> str | None:
        return v.strip().lower() if v is not None else None

    @field_validator("mobile")
    @classmethod
    def validate_mobile_opt(cls, v: str | None) -> str | None:
        if v is not None:
            clean = re.sub(r"[\s\-\(\)]", "", v.strip())
            if not re.match(r"^\+?[0-9]{7,15}$", clean):
                raise ValueError(
                    "Mobile number must contain between 7 and 15 digits, optionally prefixed with '+'"
                )
            return clean
        return v

    @field_validator("hobbies", mode="before")
    @classmethod
    def normalize_hobbies_opt(cls, v: Any) -> list[str] | None:
        if v is None:
            return None
        if isinstance(v, str):
            raw_items = v.split(",")
        elif isinstance(v, list):
            raw_items = v
        else:
            return None

        cleaned: list[str] = []
        for item in raw_items:
            if isinstance(item, str):
                s = item.strip()
                if s and s not in cleaned:
                    cleaned.append(s)
        return cleaned

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob_opt(cls, v: date | None) -> date | None:
        if v and v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v


class UserResponse(UserBase):
    """Database representation of a user including system IDs and timestamps."""

    id: int
    created_at: datetime
    updated_at: datetime


class PaginatedUsersResponse(BaseModel):
    """Paginated user list with navigation metadata."""

    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class TopHobby(BaseModel):
    """Statistic representation for a hobby."""

    hobby: str
    count: int


class UserStatsResponse(BaseModel):
    """Aggregated dashboard metrics."""

    total_users: int
    active_users: int
    inactive_users: int
    top_hobbies: list[TopHobby]
    recent_users_count: int
    total_cities: int
