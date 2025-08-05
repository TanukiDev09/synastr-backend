# app/api/exceptions.py

import strawberry

@strawberry.type
class UserAlreadyExistsError(Exception):
    """Error para cuando un email ya está registrado."""
    message: str = "User with this email already exists"

    def __init__(self, message: str = "User with this email already exists"):
        super().__init__(message)
        self.message = message


@strawberry.type
class InvalidCredentialsError(Exception):
    """Error para credenciales de login incorrectas."""
    message: str = "Invalid email or password"

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message)
        self.message = message


@strawberry.type
class AstrologicalCalculationError(Exception):
    """Error durante el cálculo de la carta natal."""
    message: str

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@strawberry.type
class AuthenticationError(Exception):
    """
    Error para cuando un usuario no está autenticado o el token no es válido.
    """
    message: str

    def __init__(self, message: str = "Not authenticated: Authorization header is missing or invalid"):
        super().__init__(message)
        self.message = message
