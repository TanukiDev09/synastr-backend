"""
Define todos los tipos de datos y entradas de GraphQL para la aplicación.

Este archivo centraliza las definiciones de Strawberry para que los resolvers
puedan importarlos, manteniendo el código limpio y organizado.
"""
from __future__ import annotations

import enum
from datetime import date, time
from typing import List, Optional

import strawberry

# --- Enums ---
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

# --- Tipos de Datos (Salida) ---
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

@strawberry.type
class LikeResponse:
    matched: bool

@strawberry.type
class Match:
    id: strawberry.ID
    user: User

@strawberry.type
class CompatibilityBreakdown:
    category: str
    score: float
    description: str

# --- Tipos de Entrada (Input) ---
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

@strawberry.input
class AddPhotosInput:
    user_id: strawberry.ID
    photos: List[PhotoInput]