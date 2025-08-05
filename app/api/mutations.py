# app/api/mutations.py

import strawberry
from strawberry.types import Info
from typing import List, Optional

from .types import (
    AuthPayload,
    LikeResponse,
    LoginInput,
    SignUpInput,
    LikeInput,
    AddPhotosInput,
    User,
)
from .resolvers.user_resolvers import UserMutations, update_profile_resolver
from .resolvers.match_resolvers import MatchMutations
from app.services.profile import add_photos_to_user


@strawberry.type
class PhotoMutations:
    @strawberry.mutation
    async def add_photos(self, info: Info, input_data: AddPhotosInput) -> User:
        """Añade una lista de fotos al perfil de un usuario."""
        return await add_photos_to_user(
            user_id=input_data.user_id, photos_data=input_data.photos
        )


@strawberry.type
class ProfileMutations:
    @strawberry.mutation
    async def update_profile(
        self,
        info: Info,
        gender: Optional[str] = None,
        looking_for: Optional[str] = None,
        sexual_orientation: Optional[List[str]] = None,
        height: Optional[int] = None,
        weight: Optional[int] = None,
        school: Optional[str] = None,
        languages: Optional[List[str]] = None,
        interests: Optional[List[str]] = None,
        education: Optional[str] = None,
        children: Optional[str] = None,
        communication_style: Optional[str] = None,
        pets: Optional[str] = None,
        drinking: Optional[str] = None,
        smoking: Optional[str] = None,
        fitness: Optional[str] = None,
        dietary: Optional[str] = None,
        sleeping: Optional[str] = None,
        politics: Optional[str] = None,
        spirituality: Optional[str] = None,
    ) -> User:
        """Actualiza el perfil de un usuario con campos opcionales."""
        return await update_profile_resolver(
            info=info,
            gender=gender,
            looking_for=looking_for,
            sexual_orientation=sexual_orientation,
            height=height,
            weight=weight,
            school=school,
            languages=languages,
            interests=interests,
            education=education,
            children=children,
            communication_style=communication_style,
            pets=pets,
            drinking=drinking,
            smoking=smoking,
            fitness=fitness,
            dietary=dietary,
            sleeping=sleeping,
            politics=politics,
            spirituality=spirituality,
        )


@strawberry.type
class Mutation(UserMutations, MatchMutations, PhotoMutations, ProfileMutations):
    """
    Combina todas las mutaciones de los diferentes resolvers en un solo tipo raíz.
    """
    pass
