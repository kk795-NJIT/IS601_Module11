"""
Integration tests for FastAPI application with real database.

These tests use PostgreSQL for testing.
"""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app, Base
from app.database import get_db
from app.models import User


# Use PostgreSQL test database
DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://user:password@localhost:5433/secure_app_test")


@pytest.fixture(scope="module")
def setup_database():
    """Create test database and tables."""
    # Create engine for test database
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    """Provide a database session for each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=setup_database
    )
    
    db = TestingSessionLocal()
    
    # Clear all data before each test
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    
    yield db
    
    db.close()


@pytest.fixture
def client(db_session):
    """Provide a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test that health check endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestUserCreation:
    """Test user creation endpoints and constraints."""
    
    def test_create_user_success(self, client):
        """Test successful user creation."""
        user_data = {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "johndoe"
        assert data["email"] == "john@example.com"
        assert "password" not in data
        assert "password_hash" not in data
        assert "id" in data
        assert "created_at" in data
    
    def test_create_user_duplicate_username(self, client):
        """Test that duplicate username is rejected."""
        user_data = {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        
        # Create first user
        response1 = client.post("/users", json=user_data)
        assert response1.status_code == 201
        
        # Try to create second user with same username
        user_data2 = {
            "username": "johndoe",
            "email": "john2@example.com",
            "password": "securepassword456"
        }
        response2 = client.post("/users", json=user_data2)
        assert response2.status_code == 409
        assert "Username already exists" in response2.json()["detail"]
    
    def test_create_user_duplicate_email(self, client):
        """Test that duplicate email is rejected."""
        user_data = {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        
        # Create first user
        response1 = client.post("/users", json=user_data)
        assert response1.status_code == 201
        
        # Try to create second user with same email (and different username)
        user_data2 = {
            "username": "janedoe",
            "email": "john@example.com",
            "password": "securepassword456"
        }
        response2 = client.post("/users", json=user_data2)
        assert response2.status_code == 409
        # Check for either email or username conflict error
        assert "already exists" in response2.json()["detail"]
    
    def test_create_user_invalid_email(self, client):
        """Test that invalid email format is rejected."""
        user_data = {
            "username": "johndoe",
            "email": "invalidemail",
            "password": "securepassword123"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 422
    
    def test_create_user_short_password(self, client):
        """Test that short password is rejected."""
        user_data = {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "short"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 422
    
    def test_create_user_short_username(self, client):
        """Test that short username is rejected."""
        user_data = {
            "username": "ab",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 422


class TestUserRetrieval:
    """Test user retrieval endpoints."""
    
    def test_list_users_empty(self, client):
        """Test listing users when database is empty."""
        response = client.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_list_users_with_pagination(self, client):
        """Test listing users with pagination."""
        # Create multiple users
        for i in range(5):
            user_data = {
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "password": "securepassword123"
            }
            client.post("/users", json=user_data)
        
        # Get all users
        response = client.get("/users?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        
        # Get paginated users
        response = client.get("/users?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_user_by_id(self, client):
        """Test retrieving a specific user by ID."""
        # Create a user
        user_data = {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        create_response = client.post("/users", json=user_data)
        user_id = create_response.json()["id"]
        
        # Retrieve the user
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "johndoe"
        assert data["email"] == "john@example.com"
    
    def test_get_nonexistent_user(self, client):
        """Test retrieving a non-existent user."""
        response = client.get("/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]


class TestPasswordVerification:
    """Test password verification."""
    
    def test_verify_password_success(self, client):
        """Test successful password verification."""
        # Create a user
        user_data = {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        client.post("/users", json=user_data)
        
        # Verify password
        response = client.post(
            "/verify-password",
            params={
                "username": "johndoe",
                "password": "securepassword123"
            }
        )
        assert response.status_code == 200
        assert "successfully" in response.json()["message"].lower()
    
    def test_verify_password_incorrect(self, client):
        """Test password verification with incorrect password."""
        # Create a user
        user_data = {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        client.post("/users", json=user_data)
        
        # Verify with wrong password
        response = client.post(
            "/verify-password",
            params={
                "username": "johndoe",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "Invalid password" in response.json()["detail"]
    
    def test_verify_password_nonexistent_user(self, client):
        """Test password verification for non-existent user."""
        response = client.post(
            "/verify-password",
            params={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]


class TestUserUpdate:
    """Test user update endpoints."""
    
    def test_update_user_username(self, client):
        """Test updating user username."""
        # Create a user
        user_data = {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        create_response = client.post("/users", json=user_data)
        user_id = create_response.json()["id"]
        
        # Update username
        update_data = {"username": "newusername"}
        response = client.put(f"/users/{user_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newusername"
        assert data["email"] == "john@example.com"
    
    def test_update_user_email(self, client):
        """Test updating user email."""
        # Create a user
        user_data = {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        create_response = client.post("/users", json=user_data)
        user_id = create_response.json()["id"]
        
        # Update email
        update_data = {"email": "newemail@example.com"}
        response = client.put(f"/users/{user_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@example.com"
    
    def test_update_user_duplicate_username(self, client):
        """Test updating with duplicate username is rejected."""
        # Create two users
        user_data1 = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "securepassword123"
        }
        user_data2 = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "securepassword123"
        }
        response1 = client.post("/users", json=user_data1)
        response2 = client.post("/users", json=user_data2)
        user_id2 = response2.json()["id"]
        
        # Try to update user2 with user1's username
        update_data = {"username": "user1"}
        response = client.put(f"/users/{user_id2}", json=update_data)
        assert response.status_code == 409
        assert "Username already exists" in response.json()["detail"]


class TestUserDeletion:
    """Test user deletion endpoints."""
    
    def test_delete_user(self, client):
        """Test deleting a user."""
        # Create a user
        user_data = {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        create_response = client.post("/users", json=user_data)
        user_id = create_response.json()["id"]
        
        # Delete the user
        response = client.delete(f"/users/{user_id}")
        assert response.status_code == 204
        
        # Verify user is deleted
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 404
    
    def test_delete_nonexistent_user(self, client):
        """Test deleting a non-existent user."""
        response = client.delete("/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
