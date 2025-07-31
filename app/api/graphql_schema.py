# app/api/graphql_schema.py
"""
Ensambla el esquema principal de GraphQL para la aplicación.
Importa los tipos Query y Mutation y los une en el esquema de Strawberry.
"""
import strawberry
from .queries import Query
from .mutations import Mutation

# Se crea y exporta el esquema final, limpio y sin lógica de negocio.
schema = strawberry.Schema(query=Query, mutation=Mutation)