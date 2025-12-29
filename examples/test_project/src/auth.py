"""
Authentication module for the test project.
"""

class AuthManager:
    """Manages user authentication and authorization."""

    def __init__(self):
        self.users = {}

    def login(self, username, password):
        """Authenticate user with username and password."""
        # Simple mock authentication
        if username in self.users and self.users[username] == password:
            return True
        return False

    def register(self, username, password):
        """Register a new user."""
        if username not in self.users:
            self.users[username] = password
            return True
        return False