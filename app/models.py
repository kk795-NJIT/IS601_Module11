"""
SQLAlchemy models for the application.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class User(Base):
    """
    User model with secure password storage and unique constraints.
    
    Attributes:
        id: UUID primary key
        username: Unique username (max 50 chars)
        email: Unique email address (max 100 chars)
        password_hash: Hashed password using bcrypt
        created_at: Timestamp when user was created
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class Calculation(Base):
    """
    Calculation model for storing arithmetic operations.
    
    Attributes:
        id: UUID primary key
        a: First operand (float)
        b: Second operand (float)
        type: Operation type (Add, Subtract, Multiply, Divide)
        result: Computed result of the operation
        user_id: Optional foreign key to User model
        created_at: Timestamp when calculation was created
    """
    __tablename__ = "calculations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)
    result = Column(Float, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationship to User (optional)
    user = relationship("User", backref="calculations")

    def __repr__(self) -> str:
        return f"<Calculation(id={self.id}, type={self.type}, a={self.a}, b={self.b}, result={self.result})>"
