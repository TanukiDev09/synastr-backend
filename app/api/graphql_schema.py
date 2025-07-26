"""
GraphQL schema for Synastr backend.

This module defines GraphQL types, queries and mutations for the Synastr
application. It includes persistence for user sign‑up and a login mutation
that issues JWT tokens. Comments and logs are written in English, as per
project conventions.
"""

import enum
# 1. Import 'datetime' para la conversión
from datetime import date, time, datetime
from typing import List, Optional

import strawberry
from bson import ObjectId
from pydantic import BaseModel

from app.auth.jwt import create_access_token
from app.models.user import UserModel
from app.db.client import get_mongo_db


@strawberry.enum
class ZodiacSign(enum.Enum):
    Aries = "Aries"
    Tauro = "Tauro"
    Geminis = "Géminis"
    Cancer = "Cáncer"
    Leo = "Leo"
    Virgo = "Virgo"
    Libra = "Libra"
    Escorpio = "Escorpio"
    Sagitario = "Sagitario"
    Capricornio = "Capricornio"
    Acuario = "Acuario"
    Piscis = "Piscis"


@strawberry.type
class Photo:
    url: str
    sign: Optional[ZodiacSign]


@strawberry.type
class User:
    id: strawberry.ID
    email: str
    birth_date: date
    birth_time: time
    birth_place: str
    photos: List[Photo]


@strawberry.type
class AuthPayload:
    token: str
    user: User


class SignUpInputModel(BaseModel):
    email: str
    password: str
    birth_date: date
    birth_time: time
    birth_place: str


@strawberry.input
class SignUpInput:
    email: str
    password: str
    birth_date: date
    birth_time: time
    birth_place: str


@strawberry.input
class LoginInput:
    """
    Input for user login. Accepts email and password.
    """
    email: str
    password: str


@strawberry.type
class CompatibilityBreakdown:
    category: str
    score: float
    description: str


@strawberry.type
class Query:
    @strawberry.field
    async def compatibility(self, user_id: strawberry.ID) -> List[CompatibilityBreakdown]:
        """
        Returns a dummy compatibility breakdown for the given user. Replace with
        real astrology calculations when implementing production logic.
        """
        return [
            CompatibilityBreakdown(category="Amor & afecto", score=85.0, description="High compatibility based on Moon and Venus"),
            CompatibilityBreakdown(category="Sexo & deseo", score=70.0, description="Good physical chemistry"),
            CompatibilityBreakdown(category="Comunicación", score=90.0, description="Excellent communication"),
            CompatibilityBreakdown(category="Pareja estable", score=60.0, description="Work on long‑term stability"),
        ]

    @strawberry.field
    async def feed(self, info) -> List[User]:
        """
        Returns a list of users for the feed. For now this function queries
        MongoDB for all users and maps them to GraphQL types. If the
        collection is empty, it returns an empty list.
        """
        db = get_mongo_db()
        users_collection = db.get_collection("users")
        users_cursor = users_collection.find({})
        users = []
        async for u in users_cursor:
            photos = [Photo(url=p["url"], sign=ZodiacSign[p.get("sign")] if p.get("sign") else None) for p in u.get("photos", [])]
            # MongoDB devuelve un datetime, pero Strawberry espera un date y un time
            birth_datetime = u.get("birth_date")
            birth_date_obj = birth_datetime.date() if birth_datetime else None
            birth_time_str = u.get("birth_time")
            birth_time_obj = time.fromisoformat(birth_time_str) if birth_time_str else None

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


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def sign_up(self, input: SignUpInput) -> AuthPayload:
        """
        Registers a new user. Persists the user to MongoDB, generates a JWT,
        and returns the token and user payload. If a user with the same email
        already exists, raises an exception.
        """
        db = get_mongo_db()
        users_collection = db.get_collection("users")
        existing = await users_collection.find_one({"email": input.email})
        if existing:
            raise Exception("User with this email already exists")

        user_model = UserModel(
            email=input.email,
            password_hash=UserModel.hash_password(input.password),
            birth_date=input.birth_date,
            birth_time=input.birth_time,
            birth_place=input.birth_place,
        )

        # 2. ✅ AQUÍ ESTÁ LA SOLUCIÓN
        # Convertimos el modelo a un diccionario y corregimos los tipos manualmente
        # para que sean compatibles con la base de datos (BSON).
        user_data_to_insert = user_model.model_dump(by_alias=True)
        user_data_to_insert["birth_date"] = datetime.combine(user_model.birth_date, time.min)
        user_data_to_insert["birth_time"] = user_model.birth_time.isoformat()

        # Insertamos el diccionario corregido en MongoDB
        result = await users_collection.insert_one(user_data_to_insert)
        inserted_id = result.inserted_id

        # Construimos la respuesta de GraphQL
        user = User(
            id=str(inserted_id),
            email=user_model.email,
            birth_date=user_model.birth_date,
            birth_time=user_model.birth_time,
            birth_place=user_model.birth_place,
            photos=[],
        )

        token = create_access_token(user_model.email)
        return AuthPayload(token=token, user=user)

    @strawberry.mutation
    async def login(self, input: LoginInput) -> AuthPayload:
        """
        Authenticates a user. Retrieves the user from MongoDB, verifies the
        password, and returns a JWT and the user payload. Raises an
        exception if credentials are invalid.
        """
        db = get_mongo_db()
        users_collection = db.get_collection("users")
        user_data = await users_collection.find_one({"email": input.email})
        if not user_data:
            raise Exception("Invalid credentials")

        user_model = UserModel(**user_data)
        if not user_model.verify_password(input.password):
            raise Exception("Invalid credentials")

        photos = [Photo(url=p["url"], sign=ZodiacSign[p.get("sign")] if p.get("sign") else None) for p in user_data.get("photos", [])]
        
        # Reconvertimos los tipos para la respuesta de GraphQL
        birth_datetime = user_data.get("birth_date")
        birth_date_obj = birth_datetime.date() if birth_datetime else None
        birth_time_str = user_data.get("birth_time")
        birth_time_obj = time.fromisoformat(birth_time_str) if birth_time_str else None

        user = User(
            id=str(user_data.get("_id")),
            email=user_model.email,
            birth_date=birth_date_obj,
            birth_time=birth_time_obj,
            birth_place=user_model.birth_place,
            photos=photos,
        )

        token = create_access_token(user_model.email)
        return AuthPayload(token=token, user=user)


schema = strawberry.Schema(query=Query, mutation=Mutation)