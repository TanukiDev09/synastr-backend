"""
Definición del modelo de usuario usando Pydantic.

Este modelo representa la estructura de datos que se almacenará en MongoDB y que
se enviará/recibirá a través del API GraphQL. Incluye utilidades para
hashing de contraseñas.
"""

from datetime import date, time, datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PhotoModel(BaseModel):
    url: str
    sign: Optional[str]


class AstrologicalPosition(BaseModel):
    """Represents the position of a celestial body in the zodiac."""
    name: str
    sign: str
    sign_icon: str
    degrees: float
    house: int


class NatalChart(BaseModel):
    """Contains all the positions of the natal chart."""
    positions: List[AstrologicalPosition] = []
    houses: List[AstrologicalPosition] = []


class UserModel(BaseModel):
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    email: EmailStr
    password_hash: str
    birth_date: date
    birth_time: time
    birth_place: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    natal_chart: Optional[NatalChart] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    plan: str = "free"
    photos: List[PhotoModel] = []

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_by_name=True,
        json_encoders={
            ObjectId: str,
            date: lambda d: datetime.combine(d, time.min),
            time: lambda t: t.isoformat(),
        },
    )

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)
