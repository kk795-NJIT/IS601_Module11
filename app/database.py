"""
Database configuration and connection setup.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

Base = declarative_base()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    database_url: str = "postgresql://user:password@localhost:5432/secure_app"
    environment: str = "development"

    model_config = ConfigDict(env_file=".env", extra="ignore")


def get_database_url() -> str:
    """Get the database URL from settings."""
    settings = Settings()
    return settings.database_url


def get_engine():
    """Create and return the SQLAlchemy engine."""
    url = get_database_url()
    # SQLite requires connect_args for check_same_thread
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url)


def get_session_local():
    """Get the session factory."""
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Convenience exports
engine = get_engine()
SessionLocal = get_session_local()


def get_db():
    """
    Dependency for FastAPI to get a database session.
    Usage: async def endpoint(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
