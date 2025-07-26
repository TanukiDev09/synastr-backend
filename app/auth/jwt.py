"""
Funciones helper para generación y verificación de JWT.

Utiliza python-jose para firmar y verificar tokens. Los valores de configuración
se leen de variables de entorno. Si no se encuentran, se usan valores por defecto
solo para desarrollo.
"""

import os
from datetime import datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt


def get_jwt_settings():
    secret_key = os.getenv("JWT_SECRET_KEY", "super-secret-key")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    return secret_key, algorithm, expire_minutes


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un JWT para el `subject` dado (por ejemplo, email)."""
    secret_key, algorithm, expire_minutes = get_jwt_settings()
    if expires_delta is None:
        expires_delta = timedelta(minutes=expire_minutes)
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def verify_access_token(token: str) -> Optional[str]:
    """Verifica un JWT y devuelve el `subject` (email) si es válido."""
    secret_key, algorithm, _ = get_jwt_settings()
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload.get("sub")
    except JWTError:
        return None
