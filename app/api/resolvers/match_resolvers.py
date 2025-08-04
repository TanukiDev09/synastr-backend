# app/api/resolvers/match_resolvers.py

from datetime import datetime, timezone
import strawberry
from strawberry.types import Info

from app.db.client import get_mongo_db
from ..types import LikeResponse, LikeInput
from .user_resolvers import get_current_user # <-- Esta importación es segura gracias a la nueva estructura

@strawberry.type
class MatchMutations:
    """
    Agrupa todas las mutaciones relacionadas con las interacciones entre usuarios (likes, matches).
    """
    @strawberry.mutation
    async def like_user(self, info: Info, input_data: LikeInput) -> LikeResponse:
        """Registra un 'like' y comprueba si hay un 'match'."""
        db = get_mongo_db()
        likes_collection = db.get_collection("likes")
        
        # Obtenemos el usuario actual desde el token para mayor seguridad
        current_user = await get_current_user(info)
        user_id = current_user.id

        # Renombramos el parámetro 'input' a 'input_data' para seguir buenas prácticas
        await likes_collection.insert_one({
            "user_id": str(user_id),
            "target_user_id": str(input_data.target_user_id),
            "created_at": datetime.now(timezone.utc)
        })

        # Comprobamos si el like es recíproco para crear un 'match'
        reciprocal = await likes_collection.find_one({
            "user_id": str(input_data.target_user_id),
            "target_user_id": str(user_id),
        })
        if reciprocal:
            await db.get_collection("matches").insert_one({
                "users": [str(user_id), str(input_data.target_user_id)],
                "created_at": datetime.now(timezone.utc),
            })
            return LikeResponse(matched=True)

        return LikeResponse(matched=False)