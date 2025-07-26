"""
Inicialización de clientes de base de datos para MongoDB y Redis.

Se exponen variables globales `mongo_client` y `redis_client` que pueden
importarse desde otros módulos. Llama a `init_db_clients()` en el startup de
FastAPI para inicializar las conexiones.
"""

import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis

mongo_client: Optional[AsyncIOMotorClient] = None
redis_client: Optional[aioredis.Redis] = None


async def init_db_clients() -> None:
    """Inicializa las conexiones a MongoDB y Redis basadas en variables de entorno."""
    global mongo_client, redis_client
    if mongo_client is None:
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/synastr")
        mongo_client = AsyncIOMotorClient(mongo_uri)
    if redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = aioredis.from_url(redis_url)


def get_mongo_db(name: str = "synastr"):
    """Devuelve una referencia a la base de datos MongoDB."""
    if not mongo_client:
        raise RuntimeError("Mongo client is not initialized. Call init_db_clients() first.")
    return mongo_client.get_database(name)


def get_redis() -> aioredis.Redis:
    """Devuelve una referencia al cliente Redis."""
    if not redis_client:
        raise RuntimeError("Redis client is not initialized. Call init_db_clients() first.")
    return redis_client
