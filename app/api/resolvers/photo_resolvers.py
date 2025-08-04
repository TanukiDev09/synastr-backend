# app/api/resolvers/photo_resolvers.py

import strawberry
from strawberry.types import Info
from typing import List

# Importamos las piezas necesarias desde sus ubicaciones correctas en tu proyecto
from app.api.types import AddPhotosInput, User
from app.services.profile import add_photos_to_user # <-- La lógica que creamos anteriormente

@strawberry.type
class PhotoMutations:
    """
    Contiene todas las mutaciones relacionadas con la gestión de fotos.
    """
    # El nombre del parámetro se ha cambiado de 'input' a 'input_data'
    @strawberry.mutation
    async def add_photos(self, info: Info, input_data: AddPhotosInput) -> User:
        """
        Añade una lista de fotos al perfil de un usuario.
        """
        # Se usa 'input_data' para acceder a los datos
        return await add_photos_to_user(
            user_id=input_data.user_id, photos=input_data.photos
        )