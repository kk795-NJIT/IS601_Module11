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
from app.models import User, Calculation
from app.factory import CalculationFactory


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


class TestCalculationIntegration:
    """Integration tests for Calculation model with database."""
    
    def test_create_calculation_in_database(self, db_session):
        """Test creating and storing a calculation in the database."""
        # Create a calculation using the factory
        operation_type = "Add"
        a, b = 10.5, 5.5
        result = CalculationFactory.calculate(operation_type, a, b)
        
        # Store in database
        calc = Calculation(
            a=a,
            b=b,
            type=operation_type,
            result=result
        )
        db_session.add(calc)
        db_session.commit()
        db_session.refresh(calc)
        
        # Verify data
        assert calc.id is not None
        assert calc.a == 10.5
        assert calc.b == 5.5
        assert calc.type == "Add"
        assert calc.result == 16.0
        assert calc.user_id is None
        assert calc.created_at is not None
    
    def test_create_calculation_with_user_id(self, db_session):
        """Test creating a calculation with associated user."""
        # Create a user first
        from app.security import hash_password
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("password123")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create calculation with user_id
        result = CalculationFactory.calculate("Multiply", 3.0, 4.0)
        calc = Calculation(
            a=3.0,
            b=4.0,
            type="Multiply",
            result=result,
            user_id=user.id
        )
        db_session.add(calc)
        db_session.commit()
        db_session.refresh(calc)
        
        # Verify
        assert calc.user_id == user.id
        assert calc.result == 12.0
    
    def test_query_calculations_by_type(self, db_session):
        """Test querying calculations by operation type."""
        # Create multiple calculations
        calculations_data = [
            ("Add", 10.0, 5.0),
            ("Add", 20.0, 10.0),
            ("Subtract", 15.0, 5.0),
            ("Multiply", 3.0, 7.0)
        ]
        
        for op_type, a, b in calculations_data:
            result = CalculationFactory.calculate(op_type, a, b)
            calc = Calculation(a=a, b=b, type=op_type, result=result)
            db_session.add(calc)
        
        db_session.commit()
        
        # Query Add operations
        add_calcs = db_session.query(Calculation).filter(
            Calculation.type == "Add"
        ).all()
        
        assert len(add_calcs) == 2
        assert all(c.type == "Add" for c in add_calcs)
    
    def test_calculation_all_operation_types(self, db_session):
        """Test storing all operation types in database."""
        test_cases = [
            ("Add", 10.0, 5.0, 15.0),
            ("Subtract", 10.0, 5.0, 5.0),
            ("Multiply", 10.0, 5.0, 50.0),
            ("Divide", 10.0, 5.0, 2.0)
        ]
        
        for op_type, a, b, expected_result in test_cases:
            result = CalculationFactory.calculate(op_type, a, b)
            assert result == expected_result
            
            calc = Calculation(a=a, b=b, type=op_type, result=result)
            db_session.add(calc)
        
        db_session.commit()
        
        # Verify all stored
        all_calcs = db_session.query(Calculation).all()
        assert len(all_calcs) == 4
    
    def test_calculation_with_negative_numbers(self, db_session):
        """Test calculations with negative numbers stored correctly."""
        result = CalculationFactory.calculate("Add", -10.5, -5.5)
        calc = Calculation(a=-10.5, b=-5.5, type="Add", result=result)
        db_session.add(calc)
        db_session.commit()
        db_session.refresh(calc)
        
        assert calc.a == -10.5
        assert calc.b == -5.5
        assert calc.result == -16.0
    
    def test_calculation_with_decimals(self, db_session):
        """Test calculations with decimal precision."""
        result = CalculationFactory.calculate("Divide", 10.0, 3.0)
        calc = Calculation(a=10.0, b=3.0, type="Divide", result=result)
        db_session.add(calc)
        db_session.commit()
        db_session.refresh(calc)
        
        assert abs(calc.result - 3.3333333333333335) < 0.0001
    
    def test_query_calculations_by_user(self, db_session):
        """Test querying calculations by user_id."""
        from app.security import hash_password
        
        # Create two users
        user1 = User(
            username="user1",
            email="user1@example.com",
            password_hash=hash_password("password123")
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            password_hash=hash_password("password123")
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create calculations for user1
        for i in range(3):
            result = CalculationFactory.calculate("Add", float(i), 1.0)
            calc = Calculation(
                a=float(i),
                b=1.0,
                type="Add",
                result=result,
                user_id=user1.id
            )
            db_session.add(calc)
        
        # Create calculation for user2
        result = CalculationFactory.calculate("Multiply", 5.0, 2.0)
        calc = Calculation(a=5.0, b=2.0, type="Multiply", result=result, user_id=user2.id)
        db_session.add(calc)
        
        db_session.commit()
        
        # Query user1's calculations
        user1_calcs = db_session.query(Calculation).filter(
            Calculation.user_id == user1.id
        ).all()
        
        assert len(user1_calcs) == 3
        assert all(c.user_id == user1.id for c in user1_calcs)
    
    def test_delete_calculation(self, db_session):
        """Test deleting a calculation from database."""
        result = CalculationFactory.calculate("Add", 10.0, 5.0)
        calc = Calculation(a=10.0, b=5.0, type="Add", result=result)
        db_session.add(calc)
        db_session.commit()
        calc_id = calc.id
        
        # Delete
        db_session.delete(calc)
        db_session.commit()
        
        # Verify deleted
        deleted_calc = db_session.query(Calculation).filter(
            Calculation.id == calc_id
        ).first()
        assert deleted_calc is None
    
    def test_calculation_ordering_by_created_at(self, db_session):
        """Test ordering calculations by creation time."""
        import time
        
        # Create calculations with slight time differences
        for i in range(3):
            result = CalculationFactory.calculate("Add", float(i), 1.0)
            calc = Calculation(a=float(i), b=1.0, type="Add", result=result)
            db_session.add(calc)
            db_session.commit()
            if i < 2:
                time.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Query ordered by created_at
        calcs = db_session.query(Calculation).order_by(
            Calculation.created_at
        ).all()
        
        assert len(calcs) == 3
        # Verify chronological order
        for i in range(len(calcs) - 1):
            assert calcs[i].created_at <= calcs[i + 1].created_at
