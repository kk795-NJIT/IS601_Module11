"""
Pydantic schemas for request/response validation and serialization.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    
    Validates incoming user data during user registration.
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username must be 3-50 characters"
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password must be at least 8 characters"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }


class UserRead(BaseModel):
    """
    Schema for returning user details.
    
    Excludes sensitive information like password_hash.
    Used for API responses.
    """
    id: UUID
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "johndoe",
                "email": "john@example.com",
                "created_at": "2024-01-01T12:00:00"
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50
    )
    email: Optional[EmailStr] = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "newusername",
                "email": "newemail@example.com"
            }
        }
