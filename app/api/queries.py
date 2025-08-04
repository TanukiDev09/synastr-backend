# app/api/queries.py

from datetime import datetime, time
from typing import List, Optional
import strawberry

from app.db.client import get_mongo_db
from .types import User, Photo, ZodiacSign, NatalChartType, AstrologicalPositionType, CompatibilityBreakdown

@strawberry.type
class Query:
    
    # =================================================================
    # == INICIO: CORRECCIÓN DEFINITIVA DEL NOMBRE DE LA QUERY ==
    # =================================================================
    @strawberry.field(name="feed")
    # =================================================================
    # == FIN: CORRECCIÓN DEFINITIVA DEL NOMBRE DE LA QUERY ==
    # =================================================================
    async def get_feed(self) -> List[User]:
        """
        Obtiene una lista de perfiles de usuario para el feed principal (swipe).
        """
        db = get_mongo_db()
        users_collection = db.get_collection("users")
        
        users_cursor = users_collection.find({})
        users_list = []
        
        async for user_doc in users_cursor:
            
            natal_chart_obj = None
            if natal_chart_data := user_doc.get("natal_chart"):
                natal_chart_obj = NatalChartType(
                    positions=[AstrologicalPositionType(**p) for p in natal_chart_data.get("positions", [])],
                    houses=[AstrologicalPositionType(**h) for h in natal_chart_data.get("houses", [])]
                )

            birth_dt = user_doc.get("birth_date")
            birth_t_str = user_doc.get("birth_time")
            
            birth_date_obj = birth_dt.date() if isinstance(birth_dt, datetime) else birth_dt
            birth_time_obj = time.fromisoformat(birth_t_str) if isinstance(birth_t_str, str) else birth_t_str

            user = User(
                id=str(user_doc["_id"]),
                email=user_doc.get("email"),
                birth_date=birth_date_obj,
                birth_time=birth_time_obj,
                birth_place=user_doc.get("birth_place"),
                latitude=user_doc.get("latitude"),
                longitude=user_doc.get("longitude"),
                timezone=user_doc.get("timezone"),
                natal_chart=natal_chart_obj,
                photos=[
                    Photo(
                        url=p.get("url"),
                        sign=ZodiacSign[p.get("sign")] if p.get("sign") else None
                    )
                    for p in user_doc.get("photos", [])
                ]
            )
            users_list.append(user)
            
        return users_list

    @strawberry.field
    def get_compatibility(self, user_id: strawberry.ID) -> CompatibilityBreakdown:
        """
        Calcula la compatibilidad entre el usuario actual y otro usuario.
        (Esta es una implementación de ejemplo).
        """
        return CompatibilityBreakdown(
            category="Stellar",
            score=95.5,
            description="Una conexión cósmica casi perfecta. Las estrellas se alinean para ustedes."
        )