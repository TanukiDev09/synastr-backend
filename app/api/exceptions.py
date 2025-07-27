"""
Define las excepciones personalizadas para la API de GraphQL.

Centralizar las excepciones aquí rompe las dependencias circulares
y mantiene el código organizado.
"""

class UserAlreadyExistsError(Exception):
    """Lanzado al intentar registrar un email que ya existe."""
    pass

class InvalidCredentialsError(Exception):
    """Lanzado cuando las credenciales de inicio de sesión son incorrectas."""
    pass

class DatabaseOperationError(Exception):
    """Lanzado cuando una operación de base de datos falla."""
    pass

class LikeAlreadyExistsError(Exception):
    """Lanzado al registrar un "like" duplicado."""
    pass