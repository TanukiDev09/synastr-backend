"""
GraphQL schema for Synastr backend.

This module defines GraphQL types, queries and mutations for the Synastr
application. It includes persistence for user sign‑up and login, logic for
recording likes, discovering who has liked you and retrieving matches.
Comments and logs are written in English, as per project conventions.
"""

import enum
from datetime import date, time, datetime, timezone
from typing import List, Optional

import strawberry
from bson import ObjectId
from pydantic import BaseModel

from app.auth.jwt import create_access_token
from app.models.user import UserModel
from app.db.client import get_mongo_db


# Custom exception classes for clearer error handling
class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class DatabaseOperationError(Exception):
    pass


# Raised when a like already exists between two users
class LikeAlreadyExistsError(Exception):
    pass


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


@strawberry.input
class LikeInput:
    """
    Represents a like action from one user to another. Both user IDs are
    required because authentication has not yet been implemented at resolver
    level. Once authentication context is available, the `user_id` can be
    derived from the JWT and omitted from the input.
    """
    user_id: strawberry.ID
    target_user_id: strawberry.ID


@strawberry.type
class LikeResponse:
    """
    Response returned by the `like_user` mutation. It indicates whether
    the action resulted in a new match being created.
    """
    matched: bool


@strawberry.type
class Match:
    """
    Represents a match between the current user and another user. The `id`
    field corresponds to the MongoDB `_id` of the match document and is
    used later as a conversation identifier for chat.
    """
    id: strawberry.ID
    user: User


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
        users: List[User] = []
        async for u in users_cursor:
            photos = [Photo(url=p["url"], sign=ZodiacSign[p.get("sign")] if p.get("sign") else None) for p in u.get("photos", [])]
            # Convert stored date and time back to Python objects
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

    @strawberry.field
    async def likers(self, user_id: strawberry.ID) -> List[User]:
        """
        Returns a list of users who have liked the given user. It looks up
        all like records where `target_user_id` matches the provided ID
        and then fetches the corresponding user documents. If no likes are
        found an empty list is returned.
        """
        db = get_mongo_db()
        likes_collection = db.get_collection("likes")
        users_collection = db.get_collection("users")

        likes_cursor = likes_collection.find({"target_user_id": str(user_id)})
        liker_ids: List[str] = []
        async for like in likes_cursor:
            liker_ids.append(like.get("user_id"))

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

    @strawberry.field
    async def matches(self, user_id: strawberry.ID) -> List[Match]:
        """
        Returns a list of matches for the specified user. A match is created
        when two users mutually like each other. Each returned `Match`
        contains the match document ID and the other user involved in the
        match. This can later be used as an index for chat conversations.
        """
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


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def sign_up(self, input: SignUpInput) -> AuthPayload:
        """
        Registers a new user. Persists the user to MongoDB, generates a JWT,
        and returns the token and user payload. If a user with the same
        email already exists, raises an exception.
        """
        db = get_mongo_db()
        users_collection = db.get_collection("users")
        existing = await users_collection.find_one({"email": input.email})
        if existing:
            raise UserAlreadyExistsError("User with this email already exists")

        # Create Pydantic user model and hash password
        user_model = UserModel(
            email=input.email,
            password_hash=UserModel.hash_password(input.password),
            birth_date=input.birth_date,
            birth_time=input.birth_time,
            birth_place=input.birth_place,
        )

        # Prepare user data for MongoDB: birth_date stored as datetime and birth_time as ISO string
        user_data_to_insert = user_model.model_dump(by_alias=True)
        user_data_to_insert["birth_date"] = datetime.combine(user_model.birth_date, time.min)
        user_data_to_insert["birth_time"] = user_model.birth_time.isoformat()

        result = await users_collection.insert_one(user_data_to_insert)
        inserted_id = result.inserted_id

        # Build GraphQL user instance
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
            raise InvalidCredentialsError("Invalid credentials")

        user_model = UserModel(**user_data)
        if not user_model.verify_password(input.password):
            raise InvalidCredentialsError("Invalid credentials")

        photos = [Photo(url=p["url"], sign=ZodiacSign[p.get("sign")] if p.get("sign") else None) for p in user_data.get("photos", [])]
        birth_datetime = user_data.get("birth_date")
        birth_date_obj = birth_datetime.date() if isinstance(birth_datetime, datetime) else birth_datetime
        birth_time_str = user_data.get("birth_time")
        birth_time_obj = time.fromisoformat(birth_time_str) if isinstance(birth_time_str, str) else birth_time_str

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

    @strawberry.mutation
    async def like_user(self, input: LikeInput) -> LikeResponse:
        """
        Records a "like" from one user to another and checks for a reciprocal
        like. If both users have liked each other, a new match record is
        created. Prevents duplicate likes by raising `LikeAlreadyExistsError`.
        Returns whether a match occurred.
        """
        db = get_mongo_db()
        likes_collection = db.get_collection("likes")

        # Verify if the like already exists
        existing_like = await likes_collection.find_one({
            "user_id": str(input.user_id),
            "target_user_id": str(input.target_user_id),
        })
        if existing_like:
            raise LikeAlreadyExistsError(f"User {input.user_id} has already liked {input.target_user_id}")

        # Persist the like action
        like_document = {
            "user_id": str(input.user_id),
            "target_user_id": str(input.target_user_id),
            "created_at": datetime.now(timezone.utc),
        }
        await likes_collection.insert_one(like_document)

        # Check if the target user has already liked the current user
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


schema = strawberry.Schema(query=Query, mutation=Mutation)