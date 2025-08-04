# app/auth/__init__.py
"""
Módulo de autenticación.

Expone las funciones principales para la creación y verificación de tokens.
"""
# Se corrige la importación para que apunte a las funciones que sí existen en jwt.py
from .jwt import create_access_token, get_current_user_from_token

# Opcional: Puedes exportar los nombres para que otros módulos los vean.
__all__ = ["create_access_token", "get_current_user_from_token"]