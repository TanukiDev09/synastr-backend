# app/api/queries.py

from datetime import datetime, time
from typing import List
import strawberry

from app.db.client import get_mongo_db
from .types import (
    User, Photo, ZodiacSign, NatalChartType, AstrologicalPositionType,
    CompatibilityBreakdown, UserInfo, Gender, SexualOrientation,
    Children, CommunicationStyle, Pets, Drinking, Smoking,
    Fitness, Dietary, Sleeping, Politics, Spirituality, LookingFor,
)


def build_natal_chart(natal_chart_data) -> NatalChartType | None:
    if not natal_chart_data:
        return None
    return NatalChartType(
        positions=[AstrologicalPositionType(**pos) for pos in natal_chart_data.get("positions", [])],
        houses=[AstrologicalPositionType(**house) for house in natal_chart_data.get("houses", [])],
    )


def build_user_info(user_info_data: dict) -> UserInfo:
    return UserInfo(
        height=user_info_data.get("height"),
        weight=user_info_data.get("weight"),
        school=user_info_data.get("school"),
        languages=user_info_data.get("languages"),
        interests=user_info_data.get("interests"),
        education=user_info_data.get("education"),
        children=Children(user_info_data.get("children")) if user_info_data.get("children") is not None else None,
        communication_style=CommunicationStyle(user_info_data.get("communication_style")) if user_info_data.get("communication_style") is not None else None,
        pets=Pets(user_info_data.get("pets")) if user_info_data.get("pets") is not None else None,
        drinking=Drinking(user_info_data.get("drinking")) if user_info_data.get("drinking") is not None else None,
        smoking=Smoking(user_info_data.get("smoking")) if user_info_data.get("smoking") is not None else None,
        fitness=Fitness(user_info_data.get("fitness")) if user_info_data.get("fitness") is not None else None,
        dietary=Dietary(user_info_data.get("dietary")) if user_info_data.get("dietary") is not None else None,
        sleeping=Sleeping(user_info_data.get("sleeping")) if user_info_data.get("sleeping") is not None else None,
        politics=Politics(user_info_data.get("politics")) if user_info_data.get("politics") is not None else None,
        spirituality=Spirituality(user_info_data.get("spirituality")) if user_info_data.get("spirituality") is not None else None,
    )


def build_user(doc) -> User:
    natal_chart = build_natal_chart(doc.get("natal_chart"))
    user_info = build_user_info(doc.get("user_info", {}) or {})

    birth_dt = doc.get("birth_date")
    birth_t_str = doc.get("birth_time")
    birth_date_obj = birth_dt.date() if isinstance(birth_dt, datetime) else birth_dt
    birth_time_obj = time.fromisoformat(birth_t_str) if isinstance(birth_t_str, str) else birth_t_str

    return User(
        id=str(doc["_id"]),
        email=doc.get("email"),
        birth_date=birth_date_obj,
        birth_time=birth_time_obj,
        birth_place=doc.get("birth_place"),
        latitude=doc.get("latitude"),
        longitude=doc.get("longitude"),
        timezone=doc.get("timezone"),
        natal_chart=natal_chart,
        photos=[
            Photo(
                url=p.get("url"),
                sign=ZodiacSign[p.get("sign")] if p.get("sign") else None,
            )
            for p in doc.get("photos", [])
        ],
        gender=Gender(doc["gender"]),
        looking_for=LookingFor(doc["looking_for"]),
        sexual_orientation=[SexualOrientation(so) for so in doc.get("sexual_orientation", [])],
        user_info=user_info,
    )


@strawberry.type
class Query:
    @strawberry.field(name="feed")
    async def get_feed(self) -> List[User]:
        db = get_mongo_db()
        users_collection = db.get_collection("users")
        cursor = users_collection.find({})
        return [build_user(doc) async for doc in cursor]

    @strawberry.field
    def get_compatibility(self, user_id: strawberry.ID) -> CompatibilityBreakdown:
        return CompatibilityBreakdown(
            category="Stellar",
            score=95.5,
            description="Una conexión cósmica casi perfecta. Las estrellas se alinean para ustedes."
        )
