# app/api/resolvers/match_resolvers.py
"""
Contiene los resolvers para la lógica de 'likes' y 'matches'.
"""
from datetime import datetime, timezone
import strawberry

from app.db.client import get_mongo_db
from ..types import LikeResponse, LikeInput

@strawberry.mutation
async def like_user(input: LikeInput) -> LikeResponse:
    """Registra un 'like' y comprueba si hay un 'match'."""
    db = get_mongo_db()
    likes_collection = db.get_collection("likes")

    await likes_collection.insert_one({
        "user_id": str(input.user_id),
        "target_user_id": str(input.target_user_id),
        "created_at": datetime.now(timezone.utc)
    })

    reciprocal = await likes_collection.find_one({
        "user_id": str(input.target_user_id),
        "target_user_id": str(input.user_id),
    })
    if reciprocal:
        await db.get_collection("matches").insert_one({
            "users": [str(input.user_id), str(input.target_user_id)],
            "created_at": datetime.now(timezone.utc),
        })
        return LikeResponse(matched=True)

    return LikeResponse(matched=False)