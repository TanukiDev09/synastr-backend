"""
Exporta los clientes de MongoDB y Redis para usarlos en otros módulos.
"""

from .client import mongo_client, redis_client

__all__ = ["mongo_client", "redis_client"]
