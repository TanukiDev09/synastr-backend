# app/api/queries.py

"""
Ensambla todas las queries de GraphQL en un único tipo 'Query'.

Este archivo importa los resolvers de queries desde los archivos de lógica
separados y los une para que el esquema principal de GraphQL los pueda utilizar.
"""
from __future__ import annotations

import strawberry
from typing import List
from datetime import datetime, time

from bson import ObjectId

from app.db.client import get_mongo_db
from app.seeds import ZODIAC_PHOTO_SUGGESTIONS

# 1. Importar los tipos necesarios desde types.py
from .types import (
    User,
    Match,
    CompatibilityBreakdown,
    Photo,
    ZodiacSign,
)

# 2. Importar los resolvers que ya hemos separado
from .resolvers.match_resolvers import get_likers, get_matches


# --- Definición de tipos adicionales para las nuevas queries ---

@strawberry.type
class PhotoSuggestion:
    """Representa una sugerencia de foto con su signo zodiacal asociado."""
    sign: str
    prompt: str


# --- Lógica de los Resolvers ---

async def get_feed() -> List[User]:
    """
    Devuelve una lista de todos los usuarios para el feed.
    """
    db = get_mongo_db()
    users_collection = db.get_collection("users")
    users_cursor = users_collection.find({})
    users: List[User] = []
    async for u in users_cursor:
        photos = [Photo(url=p.get("url"), sign=ZodiacSign[p.get("sign")] if p.get("sign") else None) for p in u.get("photos", [])]
        
        birth_datetime = u.get("birth_date")
        birth_date_obj = birth_datetime.date() if isinstance(birth_datetime, datetime) else birth_datetime
        birth_time_str = u.get("birth_time")
        birth_time_obj = time.fromisoformat(birth_time_str) if isinstance(birth_time_str, str) else birth_time_str
        
        users.append(
            User(
                id=str(u.get("_id")),
                email=u.get("email"),
                birth_date=birth_date_obj,
                birth_time=birth_time_obj,
                birth_place=u.get("birth_place"),
                photos=photos,
            )
        )
    return users

async def get_compatibility(user_id: strawberry.ID) -> List[CompatibilityBreakdown]:
    """
    Devuelve un análisis de compatibilidad de ejemplo.
    """
    return [
        CompatibilityBreakdown(category="Amor & afecto", score=85.0, description="High compatibility based on Moon and Venus"),
        CompatibilityBreakdown(category="Sexo & deseo", score=70.0, description="Good physical chemistry"),
        CompatibilityBreakdown(category="Comunicación", score=90.0, description="Excellent communication"),
        CompatibilityBreakdown(category="Pareja estable", score=60.0, description="Work on long‑term stability"),
    ]

async def get_photo_suggestions() -> List[PhotoSuggestion]:
    """
    Devuelve la lista de sugerencias de fotos por signo desde los datos de semillas.
    """
    return [
        PhotoSuggestion(sign=sign, prompt=prompt)
        for sign, prompt in ZODIAC_PHOTO_SUGGESTIONS.items()
    ]


# --- Ensamblaje del tipo Query ---

@strawberry.type
class Query:
    # Asignar cada campo a su función resolver correspondiente
    feed: List[User] = strawberry.field(resolver=get_feed)
    compatibility: List[CompatibilityBreakdown] = strawberry.field(resolver=get_compatibility)
    likers: List[User] = strawberry.field(resolver=get_likers)
    matches: List[Match] = strawberry.field(resolver=get_matches)
    
    # ✅ Se añade el nuevo campo para obtener las sugerencias de fotos
    photoSuggestions: List[PhotoSuggestion] = strawberry.field(resolver=get_photo_suggestions)