"""
Ensambla todas las mutaciones de GraphQL en un único tipo 'Mutation'.

Este archivo importa los resolvers de mutaciones desde los archivos de lógica
separados (como user_resolvers.py y match_resolvers.py) y los une
para que el esquema principal de GraphQL los pueda utilizar.
"""

import strawberry

# ✅ 1. SE IMPORTAN LOS TIPOS NECESARIOS DESDE types.py
from .types import AuthPayload, User, LikeResponse

# 2. Se importan los resolvers de mutaciones desde sus respectivos archivos
from .resolvers.user_resolvers import (
    sign_up,
    login,
    add_photos,
)
from .resolvers.match_resolvers import (
    like_user,
)

# 3. Se define el tipo 'Mutation' que Strawberry usará
@strawberry.type
class Mutation:
    # Mutaciones relacionadas con el usuario
    signUp: AuthPayload = sign_up
    login: AuthPayload = login
    addPhotos: User = add_photos

    # Mutaciones relacionadas con likes y matches
    likeUser: LikeResponse = like_user