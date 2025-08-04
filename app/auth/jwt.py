# app/auth/jwt.py

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from strawberry.types import Info

# Importaciones necesarias para la nueva función, verificadas contra tu repositorio
from app.db.client import get_mongo_db
from app.api.exceptions import AuthenticationError

# Clave secreta y algoritmo para JWT, leídos desde las variables de entorno
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a_super_secret_key_that_is_long_and_secure")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(subject: str) -> str:
    """
    Crea un nuevo token de acceso JWT para un sujeto (típicamente el email del usuario).
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": subject}
    # Se aplica la sugerencia de Sourcery: se retorna el valor directamente.
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# =================================================================
# == INICIO: CÓDIGO AÑADIDO PARA OBTENER EL USUARIO DESDE EL TOKEN ==
# =================================================================

async def get_current_user_from_token(info: Info) -> dict:
    """
    Decodifica el token JWT de la cabecera de la petición, valida al usuario
    y devuelve su documento de la base de datos.
    """
    request = info.context["request"]
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise AuthenticationError(message="Not authenticated: Authorization header is missing or invalid")

    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise AuthenticationError(message="Invalid token: subject missing")
    except JWTError as e:
        raise AuthenticationError(message=f"Invalid token: {e}") from e

    db = get_mongo_db()
    users_collection = db.get_collection("users")
    user_data = await users_collection.find_one({"email": email})

    if user_data is None:
        raise AuthenticationError(message="User not found")

    return user_data

# =================================================================
# == FIN: CÓDIGO AÑADIDO PARA OBTENER EL USUARIO DESDE EL TOKEN ==
# =================================================================