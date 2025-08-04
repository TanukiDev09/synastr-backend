# app/api/types.py
from __future__ import annotations
import enum
from datetime import date, time
from typing import List, Optional
import strawberry
from pydantic import BaseModel

# --- Enums ---
@strawberry.enum
class ZodiacSign(enum.Enum):
    Aries = "Aries"
    Taurus = "Taurus"
    Gemini = "Gemini"
    Cancer = "Cancer"
    Leo = "Leo"
    Virgo = "Virgo"
    Libra = "Libra"
    Scorpio = "Scorpio"
    Sagittarius = "Sagittarius"
    Capricorn = "Capricorn"
    Pisces = "Pisces"

# --- Data Types (Output) ---
@strawberry.type
class Photo:
    url: str
    sign: Optional[ZodiacSign]

@strawberry.type
class AstrologicalPositionType:
    name: str
    sign: str
    sign_icon: str
    degrees: float
    house: int

@strawberry.type
class NatalChartType:
    positions: List[AstrologicalPositionType]
    houses: List[AstrologicalPositionType]

    @classmethod
    def from_pydantic(cls, pydantic_obj: BaseModel) -> "NatalChartType":
        data = pydantic_obj.dict()
        return cls(**data)

@strawberry.type
class User:
    id: strawberry.ID
    email: str
    birth_date: date
    birth_time: time
    birth_place: str
    latitude: Optional[float]
    longitude: Optional[float]
    timezone: Optional[str]
    photos: List[Photo]
    natal_chart: Optional[NatalChartType]

@strawberry.type
class AuthPayload:
    token: str
    user: User

@strawberry.type
class LikeResponse:
    matched: bool

@strawberry.type
class CompatibilityBreakdown:
    category: str
    score: float
    description: str

# --- Input Types ---
@strawberry.input
class SignUpInput:
    email: str
    password: str
    birth_date: date
    birth_time: time
    birth_place: str

@strawberry.input
class LoginInput:
    email: str
    password: str

@strawberry.input
class LikeInput:
    user_id: strawberry.ID
    target_user_id: strawberry.ID

@strawberry.input
class PhotoInput:
    url: str
    sign: Optional[ZodiacSign] = None
    def to_dict(self) -> dict:
        return {"url": self.url, "sign": self.sign.value if self.sign else None}

@strawberry.input
class AddPhotosInput:
    user_id: strawberry.ID
    photos: List[PhotoInput]