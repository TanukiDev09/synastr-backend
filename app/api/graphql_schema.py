"""
Define el esquema GraphQL usando Strawberry.

Este módulo define tipos, queries y mutaciones de ejemplo que pueden ampliarse
para cubrir todas las necesidades del backend de Synastr.
"""

import enum
from datetime import date, time
from typing import List, Optional

import strawberry
from bson import ObjectId
from pydantic import BaseModel

from app.auth.jwt import create_access_token
from app.models.user import UserModel


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
        Calcula una compatibilidad ficticia para el usuario dado.
        Sustituye esta implementación con lógica real de astrología.
        """
        # Lógica simplificada: devuelve valores aleatorios o estáticos
        return [
            CompatibilityBreakdown(category="Amor & afecto", score=85.0, description="Compatibilidad alta basada en Lunas y Venus"),
            CompatibilityBreakdown(category="Sexo & deseo", score=70.0, description="Buena química física"),
            CompatibilityBreakdown(category="Comunicación", score=90.0, description="Excelente comunicación"),
            CompatibilityBreakdown(category="Pareja estable", score=60.0, description="Trabajar en la estabilidad a largo plazo"),
        ]

    @strawberry.field
    async def feed(self, info) -> List[User]:
        """Devuelve una lista de usuarios ficticios para el feed."""
        # Retorna usuarios de ejemplo; en producción deberías consultar la base de datos
        dummy_user = User(
            id=str(ObjectId()),
            email="dummy@example.com",
            birth_date=date(1990, 1, 1),
            birth_time=time(12, 0),
            birth_place="Bogotá",
            photos=[Photo(url="https://placehold.co/600x600", sign=ZodiacSign.Aries)],
        )
        return [dummy_user]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def sign_up(self, input: SignUpInput) -> AuthPayload:
        """Ejemplo de registro de usuario que devuelve un token JWT."""
        # Validar y crear usuario (simplificado)
        user_model = UserModel(
            email=input.email,
            password_hash=UserModel.hash_password(input.password),
            birth_date=input.birth_date,
            birth_time=input.birth_time,
            birth_place=input.birth_place,
        )
        # Persistir usuario en base de datos (omitir en este stub)
        # Generar token
        token = create_access_token(user_model.email)
        # Convertir a tipo Strawberry
        user = User(
            id=str(ObjectId()),
            email=user_model.email,
            birth_date=user_model.birth_date,
            birth_time=user_model.birth_time,
            birth_place=user_model.birth_place,
            photos=[],
        )
        return AuthPayload(token=token, user=user)


schema = strawberry.Schema(query=Query, mutation=Mutation)
