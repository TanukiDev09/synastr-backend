# app/services/profile.py

from bson import ObjectId
from typing import List

# Importamos las piezas necesarias desde sus ubicaciones correctas en tu proyecto
from app.api.types import PhotoInput, User, Photo, ZodiacSign, NatalChartType, AstrologicalPositionType
from app.db.client import get_mongo_db

async def add_photos_to_user(user_id: str, photos_data: List[PhotoInput]) -> User:
    """
    Añade fotos a un usuario existente en la base de datos MongoDB.
    Esta función es asíncrona porque usa 'motor' para las operaciones de base de datos.
    """
    db = get_mongo_db()
    
    try:
        # MongoDB usa un tipo de dato especial para los IDs llamado ObjectId.
        # Es necesario convertir el ID de texto a este tipo para poder buscar.
        user_object_id = ObjectId(user_id)
    except Exception:
        raise ValueError(f"El formato de user_id '{user_id}' no es válido.")

    users_collection = db.get_collection("users")
    
    # Preparamos los datos de las fotos para ser insertados en MongoDB.
    # Usamos el método 'to_dict' que añadimos en el paso anterior.
    photos_to_add = [photo.to_dict() for photo in photos_data]
    
    # Usamos el comando '$push' de MongoDB para añadir los nuevos elementos
    # al array 'photos' del documento del usuario, en lugar de reemplazarlo.
    await users_collection.update_one(
        {"_id": user_object_id},
        {"$push": {"photos": {"$each": photos_to_add}}}
    )

    # Después de actualizar, volvemos a buscar el documento completo del usuario
    # para poder devolverlo en la respuesta de la API.
    updated_user_doc = await users_collection.find_one({"_id": user_object_id})

    if not updated_user_doc:
        raise ValueError(f"No se pudo encontrar al usuario con id {user_id} después de la actualización.")
    
    # El código refactorizado por Sourcery se aplica aquí para mayor legibilidad.
    if natal_chart_data := updated_user_doc.get("natal_chart"):
        natal_chart_obj = NatalChartType(
            positions=[AstrologicalPositionType(**p) for p in natal_chart_data.get("positions", [])],
            houses=[AstrologicalPositionType(**h) for h in natal_chart_data.get("houses", [])]
        )
    else:
        natal_chart_obj = None

    return User(
        id=str(updated_user_doc["_id"]),
        email=updated_user_doc.get("email"),
        birth_date=updated_user_doc.get("birth_date"),
        birth_time=updated_user_doc.get("birth_time"),
        birth_place=updated_user_doc.get("birth_place"),
        latitude=updated_user_doc.get("latitude"),
        longitude=updated_user_doc.get("longitude"),
        timezone=updated_user_doc.get("timezone"),
        photos=[Photo(url=p.get("url"), sign=ZodiacSign[p.get("sign")] if p.get("sign") else None) for p in updated_user_doc.get("photos", [])],
        natal_chart=natal_chart_obj,
    )