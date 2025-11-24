"""
SQLAlchemy models for the application.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
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
