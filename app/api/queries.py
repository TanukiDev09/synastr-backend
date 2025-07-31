# app/api/queries.py
"""
Ensambla todas las queries de GraphQL en un único tipo 'Query'.
"""
from typing import List
from datetime import datetime, time
import strawberry
from bson import ObjectId

from app.db.client import get_mongo_db
from .types import User, CompatibilityBreakdown, Photo, ZodiacSign
from .zodiac_logic import calculate_compatibility_scores

async def get_compatibility(user_id: strawberry.ID, target_user_id: strawberry.ID, premium: bool = False) -> List[CompatibilityBreakdown]:
    """Resolver para calcular la compatibilidad astrológica."""
    db = get_mongo_db()
    users = db.get_collection("users")
    
    user1 = await users.find_one({"_id": ObjectId(str(user_id))})
    user2 = await users.find_one({"_id": ObjectId(str(target_user_id))})

    if not user1 or not user2:
        raise Exception("One or both users not found.")

    date1 = user1.get("birth_date")
    date2 = user2.get("birth_date")
    
    # La lógica de negocio se llama aquí
    scores = calculate_compatibility_scores(date1, date2, premium)

    return [CompatibilityBreakdown(**s) for s in scores]

async def get_feed() -> List[User]:
    """Resolver para obtener el feed de usuarios."""
    db = get_mongo_db()
    users_cursor = db.get_collection("users").find({})
    users_list: List[User] = []
    async for u in users_cursor:
        birth_dt = u.get("birth_date")
        birth_t_str = u.get("birth_time")
        users_list.append(
            User(
                id=str(u.get("_id")),
                email=u.get("email"),
                birth_date=birth_dt.date() if isinstance(birth_dt, datetime) else birth_dt,
                birth_time=time.fromisoformat(birth_t_str) if isinstance(birth_t_str, str) else birth_t_str,
                birth_place=u.get("birth_place"),
                photos=[Photo(url=p.get("url"), sign=ZodiacSign[p.get("sign")] if p.get("sign") else None) for p in u.get("photos", [])]
            )
        )
    return users_list

@strawberry.type
class Query:
    feed: List[User] = strawberry.field(resolver=get_feed)
    compatibility: List[CompatibilityBreakdown] = strawberry.field(resolver=get_compatibility)