# app/api/mutations.py

import strawberry
from strawberry.types import Info
from typing import List

from .types import (
    AuthPayload,
    LikeResponse,
    LoginInput,
    SignUpInput,
    LikeInput,
    AddPhotosInput,
    User,
)
from .resolvers.user_resolvers import UserMutations
from .resolvers.match_resolvers import MatchMutations
from app.services.profile import add_photos_to_user


@strawberry.type
class PhotoMutations:
    @strawberry.mutation
    async def add_photos(self, info: Info, input_data: AddPhotosInput) -> User:
        """Añade una lista de fotos al perfil de un usuario."""
        # Se corrige el nombre del argumento de 'photos' a 'photos_data'
        return await add_photos_to_user(
            user_id=input_data.user_id, photos_data=input_data.photos
        )

@strawberry.type
class Mutation(UserMutations, MatchMutations, PhotoMutations):
    """
    Combina todas las mutaciones de los diferentes resolvers en un solo tipo raíz.
    """
    pass