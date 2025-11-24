"""
Main FastAPI application with user management endpoints.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db, engine, Base
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate
from app.security import hash_password, verify_password

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Secure FastAPI Application",
    description="User management with secure password hashing and database integration",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Application is running"}


@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """
    Create a new user.
    
    - **username**: Unique username (3-50 characters)
    - **email**: Valid, unique email address
    - **password**: Password (minimum 8 characters)
    
    Returns the created user without password_hash.
    """
    try:
        # Hash the password before storing
        password_hash = hash_password(user_data.password)
        
        # Create new user instance
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash
        )
        
        # Add to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    except IntegrityError as e:
        db.rollback()
        if "username" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        elif "email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User creation failed due to data conflict"
        )


@app.get("/users/{user_id}", response_model=UserRead, tags=["Users"])
async def get_user(user_id: str, db: Session = Depends(get_db)) -> UserRead:
    """Get a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@app.get("/users", response_model=list[UserRead], tags=["Users"])
async def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> list[UserRead]:
    """
    List all users with pagination.
    
    - **skip**: Number of users to skip (default: 0)
    - **limit**: Maximum number of users to return (default: 10)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.put("/users/{user_id}", response_model=UserRead, tags=["Users"])
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
) -> UserRead:
    """Update user information (username or email)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        if user_data.username is not None:
            user.username = user_data.username
        if user_data.email is not None:
            user.email = user_data.email
        
        db.commit()
        db.refresh(user)
        return user
    
    except IntegrityError as e:
        db.rollback()
        if "username" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        elif "email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update failed due to data conflict"
        )


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Delete a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()


@app.post("/verify-password", tags=["Security"])
async def verify_user_password(username: str, password: str, db: Session = Depends(get_db)):
    """
    Verify a user's password (for authentication purposes).
    
    Returns success if password is correct.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    return {"message": "Password verified successfully"}
