# app/api/resolvers/user_resolvers.py

from datetime import datetime, time, timezone
import strawberry
from strawberry.types import Info

from app.db.client import get_mongo_db
from app.models.user import UserModel
from app.auth.jwt import create_access_token, get_current_user_from_token
from app.services.astrology_service import calculate_natal_chart
from ..types import User, AuthPayload, SignUpInput, LoginInput, Photo, ZodiacSign, NatalChartType, AstrologicalPositionType
from ..exceptions import UserAlreadyExistsError, InvalidCredentialsError, AstrologicalCalculationError, AuthenticationError

@strawberry.type
class UserMutations:
    @strawberry.mutation
    async def sign_up(self, signup_input: SignUpInput) -> AuthPayload:
        # La lógica de sign_up permanece igual...
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
            "latitude": latitude, "longitude": longitude, "timezone": timezone_name,
            "natal_chart": natal_chart.dict(), "plan": "free", "photos": [],
            "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
        }
        result = await users_collection.insert_one(user_data_to_insert)
        
        user = User(
            id=str(result.inserted_id), email=signup_input.email,
            birth_date=signup_input.birth_date, birth_time=signup_input.birth_time,
            birth_place=signup_input.birth_place, latitude=latitude,
            longitude=longitude, timezone=timezone_name, photos=[], natal_chart=None
        )
        token = create_access_token(signup_input.email)
        return AuthPayload(token=token, user=user)

    @strawberry.mutation
    async def login(self, login_input: LoginInput) -> AuthPayload:
        db = get_mongo_db()
        users_collection = db.get_collection("users")
        user_data = await users_collection.find_one({"email": login_input.email})
        if not user_data:
            raise InvalidCredentialsError("Invalid credentials")
        
        user_model = UserModel(**user_data)
        if not user_model.verify_password(login_input.password):
            raise InvalidCredentialsError("Invalid credentials")
            
        birth_dt = user_data.get("birth_date")
        birth_t_str = user_data.get("birth_time")
        
        if natal_chart_data := user_data.get("natal_chart"):
            natal_chart_obj = NatalChartType(
                positions=[AstrologicalPositionType(**p) for p in natal_chart_data.get("positions", [])],
                houses=[AstrologicalPositionType(**h) for h in natal_chart_data.get("houses", [])]
            )
        else:
            natal_chart_obj = None
            
        user = User(
            id=str(user_data.get("_id")), email=user_model.email,
            birth_date=birth_dt.date() if isinstance(birth_dt, datetime) else birth_dt,
            birth_time=time.fromisoformat(birth_t_str) if isinstance(birth_t_str, str) else birth_t_str,
            birth_place=user_model.birth_place, latitude=user_data.get("latitude"),
            longitude=user_data.get("longitude"), timezone=user_data.get("timezone"),
            photos=[Photo(url=p.get("url"), sign=ZodiacSign[p.get("sign")] if p.get("sign") else None) for p in user_data.get("photos", [])],
            natal_chart=natal_chart_obj
        )
        token = create_access_token(user_model.email)
        return AuthPayload(token=token, user=user)

# =================================================================
# == INICIO: CÓDIGO CORREGIDO PARA OBTENER EL USUARIO ACTUAL ==
# =================================================================

async def get_current_user(info: Info) -> User:
    """
    Helper para obtener el usuario actual desde el token en el contexto de la petición.
    """
    # 1. Llama a la función que decodifica el token y obtiene los datos de la BD
    user_data = await get_current_user_from_token(info)

    # 2. Mapea el diccionario de la base de datos al tipo User de GraphQL
    birth_dt = user_data.get("birth_date")
    birth_t_str = user_data.get("birth_time")
        
    if natal_chart_data := user_data.get("natal_chart"):
        natal_chart_obj = NatalChartType(
            positions=[AstrologicalPositionType(**p) for p in natal_chart_data.get("positions", [])],
            houses=[AstrologicalPositionType(**h) for h in natal_chart_data.get("houses", [])]
        )
    else:
        natal_chart_obj = None

    return User(
        id=str(user_data.get("_id")),
        email=user_data.get("email"),
        birth_date=birth_dt.date() if isinstance(birth_dt, datetime) else birth_dt,
        birth_time=time.fromisoformat(birth_t_str) if isinstance(birth_t_str, str) else birth_t_str,
        birth_place=user_data.get("birth_place"),
        latitude=user_data.get("latitude"),
        longitude=user_data.get("longitude"),
        timezone=user_data.get("timezone"),
        photos=[Photo(url=p.get("url"), sign=ZodiacSign[p.get("sign")] if p.get("sign") else None) for p in user_data.get("photos", [])],
        natal_chart=natal_chart_obj
    )

# =================================================================
# == FIN: CÓDIGO CORREGIDO PARA OBTENER EL USUARIO ACTUAL ==
# =================================================================