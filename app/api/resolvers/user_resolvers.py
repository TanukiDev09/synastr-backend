# app/api/resolvers/user_resolvers.py
"""
Contains the GraphQL resolvers for user management mutations.
"""
from datetime import datetime, time, timezone
from bson import ObjectId
import strawberry

from app.db.client import get_mongo_db
from app.models.user import UserModel
from app.auth.jwt import create_access_token
from app.services.astrology_service import calculate_natal_chart
from ..types import User, AuthPayload, SignUpInput, LoginInput, Photo, ZodiacSign, NatalChartType, AstrologicalPositionType
from ..exceptions import UserAlreadyExistsError, InvalidCredentialsError, AstrologicalCalculationError

@strawberry.mutation
async def sign_up(input: SignUpInput) -> AuthPayload:
    """Registers a new user, calculates their natal chart, and returns a JWT."""
    db = get_mongo_db()
    users_collection = db.get_collection("users")
    if await users_collection.find_one({"email": input.email}):
        raise UserAlreadyExistsError("User with this email already exists")

    birth_datetime = datetime.combine(input.birth_date, input.birth_time)

    try:
        natal_chart = await calculate_natal_chart(birth_datetime, input.birth_place)
    except ValueError as e:
        raise AstrologicalCalculationError(f"Could not process astrological data: {e}") from e

    user_data_to_insert = {
        "email": input.email,
        "password_hash": UserModel.hash_password(input.password),
        "birth_date": datetime.combine(input.birth_date, time.min),
        "birth_time": input.birth_time.isoformat(),
        "birth_place": input.birth_place,
        "natal_chart": natal_chart.dict(),
        "plan": "free",
        "photos": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    result = await users_collection.insert_one(user_data_to_insert)

    user = User(
        id=str(result.inserted_id),
        email=input.email,
        birth_date=input.birth_date,
        birth_time=input.birth_time,
        birth_place=input.birth_place,
        photos=[],
        natal_chart=None
    )
    token = create_access_token(input.email)
    return AuthPayload(token=token, user=user)

@strawberry.mutation
async def login(input: LoginInput) -> AuthPayload:
    """Authenticates a user and returns a JWT."""
    db = get_mongo_db()
    users_collection = db.get_collection("users")
    user_data = await users_collection.find_one({"email": input.email})
    if not user_data:
        raise InvalidCredentialsError("Invalid credentials")

    user_model = UserModel(**user_data)
    if not user_model.verify_password(input.password):
        raise InvalidCredentialsError("Invalid credentials")

    birth_dt = user_data.get("birth_date")
    birth_t_str = user_data.get("birth_time")

    natal_chart_data = user_data.get("natal_chart")
    natal_chart_obj = None

    # ---- INICIO DE LA CORRECCIÓN ----
    # Construimos el objeto completo, incluyendo los objetos anidados.
    if natal_chart_data:
        natal_chart_obj = NatalChartType(
            positions=[AstrologicalPositionType(**p) for p in natal_chart_data.get("positions", [])],
            houses=[AstrologicalPositionType(**h) for h in natal_chart_data.get("houses", [])]
        )
    # ---- FIN DE LA CORRECCIÓN ----

    user = User(
        id=str(user_data.get("_id")),
        email=user_model.email,
        birth_date=birth_dt.date() if isinstance(birth_dt, datetime) else birth_dt,
        birth_time=time.fromisoformat(birth_t_str) if isinstance(birth_t_str, str) else birth_t_str,
        birth_place=user_model.birth_place,
        photos=[Photo(url=p.get("url"), sign=ZodiacSign[p.get("sign")] if p.get("sign") else None) for p in user_data.get("photos", [])],
        natal_chart=natal_chart_obj
    )
    
    token = create_access_token(user_model.email)
    return AuthPayload(token=token, user=user)