# app/api/resolvers/user_resolvers.py

"""
Contiene los resolvers de GraphQL para las mutaciones relacionadas con
la gestión de usuarios, como el registro, inicio de sesión y la
gestión de fotos.
"""

from datetime import date, time, datetime
from typing import List

import strawberry
from bson import ObjectId

from app.db.client import get_mongo_db
from app.models.user import UserModel
from app.auth.jwt import create_access_token

# Importamos los tipos y excepciones necesarios
from ..types import (
    User,
    AuthPayload,
    SignUpInput,
    LoginInput,
    AddPhotosInput,
    Photo,
    ZodiacSign,
)
# ✅ ¡AQUÍ ESTÁ LA CORRECCIÓN!
# Importa las excepciones desde el nuevo archivo 'exceptions.py'
from ..exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    DatabaseOperationError,
)

# -----------------------------------------------------------------------------
# Resolvers de Mutations (mutaciones)
# -----------------------------------------------------------------------------

@strawberry.mutation
async def sign_up(input: SignUpInput) -> AuthPayload:
    """
    Registra un nuevo usuario, guarda en la base de datos y devuelve un token JWT.
    """
    db = get_mongo_db()
    users_collection = db.get_collection("users")
    existing = await users_collection.find_one({"email": input.email})
    if existing:
        raise UserAlreadyExistsError("User with this email already exists")

    user_model = UserModel(
        email=input.email,
        password_hash=UserModel.hash_password(input.password),
        birth_date=input.birth_date,
        birth_time=input.birth_time,
        birth_place=input.birth_place,
    )

    user_data_to_insert = user_model.model_dump(by_alias=True)
    user_data_to_insert["birth_date"] = datetime.combine(user_model.birth_date, time.min)
    user_data_to_insert["birth_time"] = user_model.birth_time.isoformat()
    
    result = await users_collection.insert_one(user_data_to_insert)
    inserted_id = result.inserted_id

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
async def login(input: LoginInput) -> AuthPayload:
    """
    Autentica a un usuario y devuelve un token JWT si las credenciales son válidas.
    """
    db = get_mongo_db()
    users_collection = db.get_collection("users")
    user_data = await users_collection.find_one({"email": input.email})
    if not user_data:
        raise InvalidCredentialsError("Invalid credentials")

    user_model = UserModel(**user_data)
    if not user_model.verify_password(input.password):
        raise InvalidCredentialsError("Invalid credentials")

    photos = [Photo(url=p.get("url"), sign=ZodiacSign[p.get("sign")] if p.get("sign") else None) for p in user_data.get("photos", [])]
    
    birth_datetime = user_data.get("birth_date")
    birth_date_obj = birth_datetime.date() if isinstance(birth_datetime, datetime) else birth_datetime
    birth_time_str = user_data.get("birth_time")
    birth_time_obj = time.fromisoformat(birth_time_str) if isinstance(birth_time_str, str) else birth_time_obj

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
async def add_photos(input: AddPhotosInput) -> User:
    """
    Actualiza o inserta fotos en el perfil de un usuario, asegurando una
    foto por signo y una de perfil.
    """
    db = get_mongo_db()
    users_collection = db.get_collection("users")

    try:
        oid = ObjectId(str(input.user_id))
    except Exception as e:
        raise DatabaseOperationError("Invalid user ID format.") from e

    user = await users_collection.find_one({"_id": oid})
    if not user:
        raise DatabaseOperationError("User not found.")

    existing_photos = {p.get("sign"): p for p in user.get("photos", [])}

    for new_photo in input.photos:
        sign_key = new_photo.sign.name if new_photo.sign else None
        existing_photos[sign_key] = {
            "url": new_photo.url,
            "sign": sign_key,
        }
    
    updated_photos_list = list(existing_photos.values())

    await users_collection.update_one(
        {"_id": oid},
        {"$set": {"photos": updated_photos_list}}
    )

    updated_user_data = await users_collection.find_one({"_id": oid})
    if not updated_user_data:
        raise DatabaseOperationError("Failed to fetch user after photo update.")

    photos = [Photo(url=p.get("url"), sign=ZodiacSign[p.get("sign")] if p.get("sign") else None) for p in updated_user_data.get("photos", [])]
    birth_datetime = updated_user_data.get("birth_date")
    birth_date_obj = birth_datetime.date() if isinstance(birth_datetime, datetime) else birth_datetime
    birth_time_str = updated_user_data.get("birth_time")
    birth_time_obj = time.fromisoformat(birth_time_str) if isinstance(birth_time_str, str) else birth_time_obj
    
    return User(
        id=str(updated_user_data.get("_id")),
        email=updated_user_data.get("email"),
        birth_date=birth_date_obj,
        birth_time=birth_time_obj,
        birth_place=updated_user_data.get("birth_place"),
        photos=photos,
    )