"""
Paquete de utilidades de autenticación: JWT y OAuth.
"""

from .jwt import create_access_token, verify_access_token

__all__ = ["create_access_token", "verify_access_token"]