"""
Defines the custom exceptions for the GraphQL API.

Centralizing exceptions here breaks circular dependencies
and keeps the code organized.
"""

class UserAlreadyExistsError(Exception):
    """Raised when trying to register an email that already exists."""
    pass

class InvalidCredentialsError(Exception):
    """Raised when login credentials are incorrect."""
    pass

class DatabaseOperationError(Exception):
    """Raised when a database operation fails."""
    pass

class LikeAlreadyExistsError(Exception):
    """Raised when registering a duplicate "like"."""
    pass

class AstrologicalCalculationError(Exception):
    """Raised when natal chart calculation or geocoding fails."""
    pass