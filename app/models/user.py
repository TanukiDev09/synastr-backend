"""
Definición del modelo de usuario usando Pydantic.

Este modelo representa la estructura de datos que se almacenará en MongoDB y que
se enviará/recibirá a través del API GraphQL. Incluye utilidades para
hashing de contraseñas.
"""

# Se importa datetime para la conversión
from datetime import date, time, datetime
from typing import List, Optional

from bson import ObjectId
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

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_by_name=True,
        # ✅ AQUÍ ESTÁ LA SOLUCIÓN:
        # Le decimos a Pydantic cómo convertir 'date' y 'time'
        # a formatos que MongoDB entiende.
        json_encoders={
            ObjectId: str,
            # La fecha se convierte en un objeto datetime (a medianoche)
            date: lambda d: datetime.combine(d, time.min),
            # La hora se convierte en un string (ej: "14:30:00")
            time: lambda t: t.isoformat(),
        },
    )

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)