"""
Contiene los resolvers de GraphQL para toda la lógica de "likes" y "matches".
"""
from datetime import datetime, timezone, time
from typing import List

import strawberry
from bson import ObjectId

from app.db.client import get_mongo_db
from ..types import (
    User,
    Match,
    LikeResponse,
    LikeInput,
    ZodiacSign,
    Photo,
)
# ✅ SE IMPORTA EL ERROR DESDE EL NUEVO ARCHIVO 'exceptions.py'
from ..exceptions import LikeAlreadyExistsError

# (El resto del archivo no cambia)
async def get_likers(user_id: strawberry.ID) -> List[User]:
    db = get_mongo_db()
    likes_collection = db.get_collection("likes")
    users_collection = db.get_collection("users")

    likes_cursor = likes_collection.find({"target_user_id": str(user_id)})
    liker_ids: List[str] = [like.get("user_id") async for like in likes_cursor]

    users: List[User] = []
    for uid in liker_ids:
        try:
            oid = uid if isinstance(uid, ObjectId) else ObjectId(uid)
        except Exception:
            continue
        
        data = await users_collection.find_one({"_id": oid})
        if data:
            photos = [Photo(url=p.get("url"), sign=ZodiacSign[p.get("sign")] if p.get("sign") else None) for p in data.get("photos", [])]
            birth_datetime = data.get("birth_date")
            birth_date_obj = birth_datetime.date() if isinstance(birth_datetime, datetime) else birth_datetime
            birth_time_str = data.get("birth_time")
            birth_time_obj = time.fromisoformat(birth_time_str) if isinstance(birth_time_str, str) else birth_time_str
            users.append(
                User(
                    id=str(data.get("_id")),
                    email=data.get("email"),
                    birth_date=birth_date_obj,
                    birth_time=birth_time_obj,
                    birth_place=data.get("birth_place"),
                    photos=photos,
                )
            )
    return users

async def get_matches(user_id: strawberry.ID) -> List[Match]:
    db = get_mongo_db()
    matches_collection = db.get_collection("matches")
    users_collection = db.get_collection("users")
    matches_cursor = matches_collection.find({"users": str(user_id)})
    result: List[Match] = []
    async for m in matches_cursor:
        match_id = str(m.get("_id"))
        participants = m.get("users", [])
        for uid in participants:
            if str(uid) != str(user_id):
                try:
                    oid = uid if isinstance(uid, ObjectId) else ObjectId(uid)
                except Exception:
                    continue
                data = await users_collection.find_one({"_id": oid})
                if data:
                    photos = [Photo(url=p.get("url"), sign=ZodiacSign[p.get("sign")] if p.get("sign") else None) for p in data.get("photos", [])]
                    birth_datetime = data.get("birth_date")
                    birth_date_obj = birth_datetime.date() if isinstance(birth_datetime, datetime) else birth_datetime
                    birth_time_str = data.get("birth_time")
                    birth_time_obj = time.fromisoformat(birth_time_str) if isinstance(birth_time_str, str) else birth_time_str
                    user_obj = User(
                        id=str(data.get("_id")),
                        email=data.get("email"),
                        birth_date=birth_date_obj,
                        birth_time=birth_time_obj,
                        birth_place=data.get("birth_place"),
                        photos=photos,
                    )
                    result.append(Match(id=match_id, user=user_obj))
    return result

@strawberry.mutation
async def like_user(input: LikeInput) -> LikeResponse:
    db = get_mongo_db()
    likes_collection = db.get_collection("likes")

    existing_like = await likes_collection.find_one({
        "user_id": str(input.user_id),
        "target_user_id": str(input.target_user_id),
    })
    if existing_like:
        raise LikeAlreadyExistsError(f"User {input.user_id} has already liked {input.target_user_id}")

    like_document = {
        "user_id": str(input.user_id),
        "target_user_id": str(input.target_user_id),
        "created_at": datetime.now(timezone.utc),
    }
    await likes_collection.insert_one(like_document)

    reciprocal = await likes_collection.find_one({
        "user_id": str(input.target_user_id),
        "target_user_id": str(input.user_id),
    })
    if reciprocal:
        matches_collection = db.get_collection("matches")
        await matches_collection.insert_one({
            "users": [str(input.user_id), str(input.target_user_id)],
            "created_at": datetime.now(timezone.utc),
        })
        return LikeResponse(matched=True)

    return LikeResponse(matched=False)