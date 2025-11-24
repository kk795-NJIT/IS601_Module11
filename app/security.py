"""
Password hashing utilities using bcrypt.

Provides secure password hashing and verification functions.
"""
import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    
    Args:
        password: Plain-text password to hash
        
    Returns:
        Hashed password string
        
    Raises:
        ValueError: If password is empty or invalid
    """
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")
    
    # bcrypt generates a random salt and includes it in the hash
    # Default cost factor is 12, which is secure and reasonably fast
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    
    Args:
        password: Plain-text password to verify
        password_hash: Bcrypt hash to verify against
        
    Returns:
        True if password matches hash, False otherwise
        
    Raises:
        ValueError: If either parameter is invalid
    """
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")
    if not password_hash or not isinstance(password_hash, str):
        raise ValueError("Password hash must be a non-empty string")
    
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except ValueError:
        # Invalid hash format
        return False
