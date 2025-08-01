"""
Punto de entrada para la aplicación FastAPI.

Carga la configuración desde variables de entorno, inicializa la conexión a la base de datos
y monta el servidor GraphQL a través de Strawberry.
"""

import os
from typing import List

# ✅ 1. Importar asynccontextmanager
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request
from strawberry.asgi import GraphQL

from app.api.graphql_schema import schema
from app.db.client import init_db_clients

load_dotenv()

# ✅ 2. Crear el manejador de ciclo de vida "lifespan"
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lo que se ejecuta ANTES de que la aplicación empiece a aceptar peticiones
    print("Iniciando aplicación...")
    await init_db_clients()
    print("Clientes de base de datos inicializados.")
    
    yield  # La aplicación se ejecuta aquí
    
    # Lo que se ejecuta DESPUÉS de que la aplicación se apaga
    print("Apagando aplicación...")
    # Aquí iría el código para cerrar conexiones si fuera necesario


def create_app() -> FastAPI:
    """Crea y configura una instancia de FastAPI."""
    # ✅ 3. Pasar el "lifespan" a la instancia de FastAPI
    app = FastAPI(title="Synastr Backend", version="0.1.0", lifespan=lifespan)

    # Configuración CORS para permitir peticiones desde el frontend local
    origins: List[str] = [
        "http://localhost:5173",  # Vite (Vue) por defecto
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://synastr.vercel.app",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    graphql_app = GraphQL(schema, graphiql=True)
    # Monta GraphQL en la ruta /graphql
    app.add_route("/graphql", graphql_app)
    app.add_websocket_route("/graphql", graphql_app)

    # ✅ 4. El antiguo bloque @app.on_event("startup") se elimina
    
    @app.get("/")
    async def root() -> JSONResponse:
        return JSONResponse(content={"message": "Synastr backend en funcionamiento"})

    return app


app = create_app()