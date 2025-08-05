from datetime import datetime, time, timezone
import strawberry
from strawberry.types import Info
from bson import ObjectId

from app.db.client import get_mongo_db
from app.models.user import UserModel
from app.auth.jwt import create_access_token, get_current_user_from_token
from app.services.astrology_service import calculate_natal_chart
from ..types import (
    User,
    AuthPayload,
    SignUpInput,
    LoginInput,
    Photo,
    ZodiacSign,
    NatalChartType,
    AstrologicalPositionType,
    UserInfo,
    Gender,
    SexualOrientation,
    Children,
    CommunicationStyle,
    Pets,
    Drinking,
    Smoking,
    Fitness,
    Dietary,
    Sleeping,
    Politics,
    Spirituality,
    LookingFor,
)
from ..exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    AstrologicalCalculationError,
)


@strawberry.type
class UserMutations:
    @strawberry.mutation
    async def sign_up(self, signup_input: SignUpInput) -> AuthPayload:
        db = get_mongo_db()
        users_collection = db.get_collection("users")
        if await users_collection.find_one({"email": signup_input.email}):
            raise UserAlreadyExistsError("User with this email already exists")

        birth_datetime = datetime.combine(signup_input.birth_date, signup_input.birth_time)
        try:
            natal_chart, latitude, longitude, timezone_name = await calculate_natal_chart(
                birth_datetime, signup_input.birth_place
            )
        except ValueError as e:
            raise AstrologicalCalculationError(f"Could not process astrological data: {e}") from e

        user_data_to_insert = {
            "email": signup_input.email,
            "password_hash": UserModel.hash_password(signup_input.password),
            "birth_date": datetime.combine(signup_input.birth_date, time.min),
            "birth_time": signup_input.birth_time.isoformat(),
            "birth_place": signup_input.birth_place,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_name,
            "natal_chart": natal_chart.dict(),
            "plan": "free",
            "photos": [],
            "gender": signup_input.gender.value,
            "looking_for": signup_input.looking_for.value,
            "sexual_orientation": [],
            "user_info": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        result = await users_collection.insert_one(user_data_to_insert)

        user = build_user_object(user_data_to_insert | {"_id": result.inserted_id})
        token = create_access_token(signup_input.email)
        return AuthPayload(token=token, user=user)

    @strawberry.mutation
    async def login(self, login_input: LoginInput) -> AuthPayload:
        user_data = await fetch_user_data(login_input.email)
        if not user_data:
            raise InvalidCredentialsError("Invalid credentials")

        user_model = UserModel(**user_data)
        if not user_model.verify_password(login_input.password):
            raise InvalidCredentialsError("Invalid credentials")

        user = build_user_object(user_data)
        token = create_access_token(user_model.email)
        return AuthPayload(token=token, user=user)


async def fetch_user_data(email: str) -> dict:
    db = get_mongo_db()
    users_collection = db.get_collection("users")
    return await users_collection.find_one({"email": email})


def build_user_object(user_data: dict) -> User:
    natal_chart_obj = build_natal_chart(user_data.get("natal_chart"))
    user_info_obj = build_user_info(user_data.get("user_info"))

    return User(
        id=str(user_data["_id"]),
        email=user_data["email"],
        birth_date=user_data["birth_date"].date() if isinstance(user_data["birth_date"], datetime) else user_data["birth_date"],
        birth_time=time.fromisoformat(user_data["birth_time"]) if isinstance(user_data["birth_time"], str) else user_data["birth_time"],
        birth_place=user_data["birth_place"],
        latitude=user_data.get("latitude"),
        longitude=user_data.get("longitude"),
        timezone=user_data.get("timezone"),
        photos=[Photo(url=p["url"], sign=ZodiacSign[p["sign"]]) for p in user_data.get("photos", []) if p.get("sign")],
        natal_chart=natal_chart_obj,
        gender=Gender(user_data["gender"]),
        looking_for=LookingFor(user_data["looking_for"]),
        sexual_orientation=[SexualOrientation(so) for so in user_data.get("sexual_orientation", [])],
        user_info=user_info_obj,
    )


def build_natal_chart(chart: dict) -> NatalChartType | None:
    if not chart:
        return None
    return NatalChartType(
        positions=[AstrologicalPositionType(**p) for p in chart.get("positions", [])],
        houses=[AstrologicalPositionType(**h) for h in chart.get("houses", [])],
    )


def build_user_info(info: dict) -> UserInfo | None:
    if not info:
        return None
    return UserInfo(
        height=info.get("height"),
        weight=info.get("weight"),
        school=info.get("school"),
        languages=info.get("languages"),
        interests=info.get("interests"),
        education=info.get("education"),
        children=Children(info["children"]) if info.get("children") is not None else None,
        communication_style=CommunicationStyle(info["communication_style"]) if info.get("communication_style") is not None else None,
        pets=Pets(info["pets"]) if info.get("pets") is not None else None,
        drinking=Drinking(info["drinking"]) if info.get("drinking") is not None else None,
        smoking=Smoking(info["smoking"]) if info.get("smoking") is not None else None,
        fitness=Fitness(info["fitness"]) if info.get("fitness") is not None else None,
        dietary=Dietary(info["dietary"]) if info.get("dietary") is not None else None,
        sleeping=Sleeping(info["sleeping"]) if info.get("sleeping") is not None else None,
        politics=Politics(info["politics"]) if info.get("politics") is not None else None,
        spirituality=Spirituality(info["spirituality"]) if info.get("spirituality") is not None else None,
    )


async def get_current_user(info: Info) -> User:
    user_data = await get_current_user_from_token(info)
    return build_user_object(user_data)


async def update_profile_resolver(
    info: Info,
    gender: str = None,
    looking_for: str = None,
    sexual_orientation: list[str] = None,
    height: int = None,
    weight: int = None,
    school: str = None,
    languages: list[str] = None,
    interests: list[str] = None,
    education: str = None,
    children: str = None,
    communication_style: str = None,
    pets: str = None,
    drinking: str = None,
    smoking: str = None,
    fitness: str = None,
    dietary: str = None,
    sleeping: str = None,
    politics: str = None,
    spirituality: str = None,
) -> User:
    db = get_mongo_db()
    user_data = await get_current_user_from_token(info)
    users_collection = db.get_collection("users")

    update_fields = {}
    if gender:
        update_fields["gender"] = gender
    if looking_for:
        update_fields["looking_for"] = looking_for
    if sexual_orientation is not None:
        update_fields["sexual_orientation"] = sexual_orientation

    if user_info_update := {
        k: v
        for k, v in {
            "height": height,
            "weight": weight,
            "school": school,
            "languages": languages,
            "interests": interests,
            "education": education,
            "children": children,
            "communication_style": communication_style,
            "pets": pets,
            "drinking": drinking,
            "smoking": smoking,
            "fitness": fitness,
            "dietary": dietary,
            "sleeping": sleeping,
            "politics": politics,
            "spirituality": spirituality,
        }.items()
        if v is not None
    }:
        update_fields["user_info"] = user_info_update

    update_fields["updated_at"] = datetime.now(timezone.utc)

    await users_collection.update_one(
        {"_id": ObjectId(user_data["_id"])},
        {"$set": update_fields}
    )

    updated_user = await users_collection.find_one({"_id": ObjectId(user_data["_id"])})
    return build_user_object(updated_user)
