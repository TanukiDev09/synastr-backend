"""
Definición del modelo de usuario usando Pydantic.

Este modelo representa la estructura de datos que se almacenará en MongoDB y que
se enviará/recibirá a través del API GraphQL. Incluye utilidades para
hashing de contraseñas.
"""

from datetime import date, time
from typing import List, Optional

from bson import ObjectId
# 1. Se importa ConfigDict para la nueva configuración de Pydantic
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PhotoModel(BaseModel):
    url: str
    sign: Optional[str]


class UserModel(BaseModel):
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    email: EmailStr
    password_hash: str
    birth_date: date
    birth_time: time
    birth_place: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    plan: str = "free"
    photos: List[PhotoModel] = []

    # 2. Se reemplaza la 'class Config' por 'model_config'
    #    y se actualiza 'allow_population_by_field_name' a 'validate_by_name'
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        validate_by_name=True,
    )

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)