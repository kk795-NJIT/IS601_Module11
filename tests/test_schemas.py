"""
Unit tests for Pydantic schemas and validation.
"""
import pytest
from pydantic import ValidationError
from app.schemas import UserCreate, UserRead, UserUpdate
from uuid import UUID
from datetime import datetime


class TestUserCreateSchema:
    """Test suite for UserCreate schema validation."""
    
    def test_valid_user_create(self):
        """Test creating user with valid data."""
        user_data = {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        user = UserCreate(**user_data)
        assert user.username == "johndoe"
        assert user.email == "john@example.com"
        assert user.password == "securepassword123"
    
    def test_username_too_short(self):
        """Test that username shorter than 3 chars is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="ab",
                email="test@example.com",
                password="securepassword123"
            )
        assert "at least 3 characters" in str(exc_info.value)
    
    def test_username_too_long(self):
        """Test that username longer than 50 chars is rejected."""
        long_username = "a" * 51
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username=long_username,
                email="test@example.com",
                password="securepassword123"
            )
        assert "at most 50 characters" in str(exc_info.value)
    
    def test_invalid_email(self):
        """Test that invalid email is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="johndoe",
                email="invalidemail",
                password="securepassword123"
            )
        assert "email" in str(exc_info.value).lower()
    
    def test_password_too_short(self):
        """Test that password shorter than 8 chars is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="johndoe",
                email="john@example.com",
                password="short"
            )
        assert "at least 8 characters" in str(exc_info.value)
    
    def test_password_too_long(self):
        """Test that password longer than 100 chars is rejected."""
        long_password = "a" * 101
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="johndoe",
                email="john@example.com",
                password=long_password
            )
        assert "at most 100 characters" in str(exc_info.value)
    
    def test_missing_required_fields(self):
        """Test that missing required fields raises error."""
        with pytest.raises(ValidationError):
            UserCreate(username="johndoe")  # Missing email and password
    
    def test_email_with_plus_addressing(self):
        """Test email with plus addressing (valid format)."""
        user = UserCreate(
            username="johndoe",
            email="john+filter@example.com",
            password="securepassword123"
        )
        assert user.email == "john+filter@example.com"
    
    def test_email_case_insensitive(self):
        """Test that email validation normalizes domain to lowercase."""
        user = UserCreate(
            username="johndoe",
            email="John@EXAMPLE.COM",
            password="securepassword123"
        )
        # Pydantic normalizes domain to lowercase but preserves local part case
        assert user.email == "John@example.com"


class TestUserReadSchema:
    """Test suite for UserRead schema."""
    
    def test_user_read_from_attributes(self):
        """Test creating UserRead from model attributes."""
        user_data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "johndoe",
            "email": "john@example.com",
            "created_at": datetime.now()
        }
        user = UserRead(**user_data)
        assert user.username == "johndoe"
        assert user.email == "john@example.com"
        assert isinstance(user.id, UUID)
    
    def test_user_read_serialization(self):
        """Test UserRead serialization to dict."""
        user_data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "johndoe",
            "email": "john@example.com",
            "created_at": datetime(2024, 1, 1, 12, 0, 0)
        }
        user = UserRead(**user_data)
        user_dict = user.model_dump()
        assert user_dict["username"] == "johndoe"
        assert user_dict["email"] == "john@example.com"
        assert str(user_dict["id"]) == "550e8400-e29b-41d4-a716-446655440000"
        assert "password_hash" not in user_dict


class TestUserUpdateSchema:
    """Test suite for UserUpdate schema."""
    
    def test_partial_update_username_only(self):
        """Test updating only username."""
        update = UserUpdate(username="newusername")
        assert update.username == "newusername"
        assert update.email is None
    
    def test_partial_update_email_only(self):
        """Test updating only email."""
        update = UserUpdate(email="newemail@example.com")
        assert update.username is None
        assert update.email == "newemail@example.com"
    
    def test_partial_update_both_fields(self):
        """Test updating both username and email."""
        update = UserUpdate(
            username="newusername",
            email="newemail@example.com"
        )
        assert update.username == "newusername"
        assert update.email == "newemail@example.com"
    
    def test_empty_update(self):
        """Test empty update (all fields optional)."""
        update = UserUpdate()
        assert update.username is None
        assert update.email is None
    
    def test_invalid_email_in_update(self):
        """Test that invalid email is rejected in update."""
        with pytest.raises(ValidationError):
            UserUpdate(email="invalidemail")
    
    def test_username_too_short_in_update(self):
        """Test that username too short is rejected in update."""
        with pytest.raises(ValidationError):
            UserUpdate(username="ab")
