"""
Unit tests for password hashing and security utilities.
"""
import pytest
from app.security import hash_password, verify_password


class TestPasswordHashing:
    """Test suite for password hashing functionality."""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "testpassword123"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_password_different_hashes_for_same_password(self):
        """Test that hashing same password produces different hashes (due to salt)."""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        # Each hash should be different due to random salt
        assert hash1 != hash2
    
    def test_hash_password_with_empty_string_raises_error(self):
        """Test that hashing empty password raises ValueError."""
        with pytest.raises(ValueError, match="Password must be a non-empty string"):
            hash_password("")
    
    def test_hash_password_with_none_raises_error(self):
        """Test that hashing None raises ValueError."""
        with pytest.raises(ValueError, match="Password must be a non-empty string"):
            hash_password(None)
    
    def test_hash_password_with_non_string_raises_error(self):
        """Test that hashing non-string raises ValueError."""
        with pytest.raises(ValueError, match="Password must be a non-empty string"):
            hash_password(12345)


class TestPasswordVerification:
    """Test suite for password verification functionality."""
    
    def test_verify_password_correct_password(self):
        """Test that verify_password returns True for correct password."""
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password("wrongpassword", hashed) is False
    
    def test_verify_password_empty_password_raises_error(self):
        """Test that verifying with empty password raises ValueError."""
        hashed = hash_password("testpassword123")
        with pytest.raises(ValueError, match="Password must be a non-empty string"):
            verify_password("", hashed)
    
    def test_verify_password_none_password_raises_error(self):
        """Test that verifying with None password raises ValueError."""
        hashed = hash_password("testpassword123")
        with pytest.raises(ValueError, match="Password must be a non-empty string"):
            verify_password(None, hashed)
    
    def test_verify_password_empty_hash_raises_error(self):
        """Test that verifying with empty hash raises ValueError."""
        with pytest.raises(ValueError, match="Password hash must be a non-empty string"):
            verify_password("testpassword123", "")
    
    def test_verify_password_none_hash_raises_error(self):
        """Test that verifying with None hash raises ValueError."""
        with pytest.raises(ValueError, match="Password hash must be a non-empty string"):
            verify_password("testpassword123", None)
    
    def test_verify_password_invalid_hash_format_returns_false(self):
        """Test that verifying with invalid hash format returns False."""
        result = verify_password("testpassword123", "invalihashformat")
        assert result is False
    
    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "TestPassword123"
        hashed = hash_password(password)
        assert verify_password("testpassword123", hashed) is False
        assert verify_password("TestPassword123", hashed) is True
    
    def test_verify_password_with_special_characters(self):
        """Test password verification with special characters."""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password("p@ssw0rd!#$%^&*()", hashed) is False
    
    def test_verify_password_with_unicode_characters(self):
        """Test password verification with unicode characters."""
        password = "Пароль123密码🔐"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False
