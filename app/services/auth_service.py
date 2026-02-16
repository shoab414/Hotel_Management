"""Authentication Service - Handles user login and credential verification."""

from typing import Optional, Dict, Any


class AuthService:
    """Service for handling user authentication and login."""

    def __init__(self, db):
        """Initialize authentication service.
        
        Args:
            db: DatabaseManager instance
        """
        self.db = db

    def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user credentials and return user record if valid.
        
        Args:
            username: User's username
            password: User's password (will be hashed for comparison)
            
        Returns:
            User record dictionary if credentials are valid, None otherwise
        """
        return self.db.verify_user(username, password)
