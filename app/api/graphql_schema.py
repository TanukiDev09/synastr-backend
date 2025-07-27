"""
Ensambla el esquema principal de GraphQL para la aplicación Synastr.

Este archivo importa los tipos Query y Mutation desde sus respectivos módulos
y los utiliza para construir el objeto final de `strawberry.Schema`.
"""

import strawberry

# Se importan los ensambladores de Query y Mutation
from .queries import Query
from .mutations import Mutation

# ✅ LOS ERRORES YA NO SE DEFINEN AQUÍ

# Se crea y exporta el esquema final
schema = strawberry.Schema(query=Query, mutation=Mutation)