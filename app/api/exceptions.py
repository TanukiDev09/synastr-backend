# app/api/exceptions.py

import strawberry

@strawberry.type
class UserAlreadyExistsError:
    """Error para cuando un email ya está registrado."""
    message: str = "User with this email already exists"

@strawberry.type
class InvalidCredentialsError:
    """Error para credenciales de login incorrectas."""
    message: str = "Invalid email or password"

@strawberry.type
class AstrologicalCalculationError:
    """Error durante el cálculo de la carta natal."""
    message: str

# =================================================================
# == INICIO: CÓDIGO AÑADIDO PARA LA EXCEPCIÓN DE AUTENTICACIÓN ==
# =================================================================

@strawberry.type
class AuthenticationError:
    """
    Error para cuando un usuario no está autenticado o el token no es válido.
    Se define aquí para que pueda ser importado y utilizado en otras partes de la API.
    """
    message: str

# =================================================================
# == FIN: CÓDIGO AÑADIDO PARA LA EXCEPCIÓN DE AUTENTICACIÓN ==
# =================================================================