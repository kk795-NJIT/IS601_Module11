"""
Pydantic schemas for request/response validation and serialization.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum


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


class OperationType(str, Enum):
    """Enumeration for supported calculation types."""
    ADD = "Add"
    SUBTRACT = "Subtract"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"


class CalculationCreate(BaseModel):
    """
    Schema for creating a new calculation.
    
    Validates incoming calculation data.
    """
    a: float = Field(..., description="First operand")
    b: float = Field(..., description="Second operand")
    type: OperationType = Field(..., description="Operation type (Add, Subtract, Multiply, Divide)")
    user_id: Optional[UUID] = Field(None, description="Optional user ID")

    @model_validator(mode='after')
    def validate_divisor(self):
        """Ensure divisor is not zero for division operations."""
        if self.type == OperationType.DIVIDE and self.b == 0:
            raise ValueError("Division by zero is not allowed")
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "a": 10.5,
                "b": 5.0,
                "type": "Add"
            }
        }


class CalculationRead(BaseModel):
    """
    Schema for returning calculation details.
    
    Used for API responses.
    """
    id: UUID
    a: float
    b: float
    type: str
    result: float
    user_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "a": 10.5,
                "b": 5.0,
                "type": "Add",
                "result": 15.5,
                "user_id": None,
                "created_at": "2024-01-01T12:00:00"
            }
        }
