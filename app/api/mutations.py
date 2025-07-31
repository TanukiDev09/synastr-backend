# app/api/mutations.py
"""
Ensambla todas las mutaciones de GraphQL en un único tipo 'Mutation'.
"""
import strawberry

from .types import AuthPayload, LikeResponse
from .resolvers.user_resolvers import sign_up, login
from .resolvers.match_resolvers import like_user

@strawberry.type
class Mutation:
    signUp: AuthPayload = sign_up
    login: AuthPayload = login
    likeUser: LikeResponse = like_user