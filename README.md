# Synastr – Backend

Este directorio contiene el backend para **Synastr**, una aplicación de dating y matchmaking basada en astrología.

## Stack

- **Python 3.12** con [FastAPI](https://fastapi.tiangolo.com/)
- **Strawberry GraphQL** para esquemas GraphQL
- **MongoDB 6** para almacenamiento de datos (ejecutar una instancia local o usar Atlas)
- **Redis 7** para caché y comunicación en tiempo real (WebSockets Pub/Sub)
- **OAuth 2.0 + JWT** para autenticación

## Estructura del proyecto

```
synastr-backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── graphql_schema.py  # Esquema GraphQL de Strawberry
│   ├── auth/
│   │   ├── __init__.py
│   │   └── jwt.py             # Utilidades de JWT y OAuth (stub)
│   ├── db/
│   │   ├── __init__.py
│   │   └── client.py          # Clientes MongoDB y Redis
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py            # Modelo de usuario básico
│   ├── seeds/
│   │   └── zodiac_seeds.py     # Datos iniciales para sugerencias de fotos
│   └── main.py                # Instancia FastAPI y montaje de GraphQL
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```

### `app/api/graphql_schema.py`

Define los tipos y resolvers de Strawberry. Incluye un ejemplo de mutación `signUp` y consulta `compatibility`. Puedes extender este esquema añadiendo más tipos y resolvers siguiendo los modelos de la especificación.

### `app/db/client.py`

Inicializa las conexiones a MongoDB y Redis usando variables de entorno. En producción se conecta a la instancia de Atlas o Railway; en local puedes apuntar a `localhost` si tienes Mongo y Redis corriendo de manera local.

### `app/auth/jwt.py`

Proporciona funciones helper para generar y verificar JWTs. Incluye también un stub para OAuth 2.0 (usar librerías como `authlib` o `fastapi-users` en un despliegue real).

### `app/models/user.py`

Define el modelo de usuario con los campos especificados en el diseño. Utiliza `pydantic` para validar entradas y `bson` para convertir `ObjectId`.

### `app/seeds/zodiac_seeds.py`

Contiene un diccionario de semillas para las sugerencias de fotos por signo y elemento. Esto te permite poblar la base de datos o mantener estos textos en memoria para mostrarlos en el onboarding.

## Variables de entorno

Crea un archivo `.env` basado en `.env.example` y completa los valores correspondientes:

```
MONGODB_URI=mongodb://localhost:27017/synastr
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=super-secret-key
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLIMATE_URL=your-cloudinary-api-url
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
```

## Uso local

1. Instala las dependencias:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copia `.env.example` a `.env` y modifica los valores según tu entorno.

3. Asegúrate de tener servicios de **MongoDB** y **Redis** ejecutándose localmente.

4. Ejecuta el servidor:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Accede a la documentación interactiva de la API GraphQL en `http://localhost:8000/graphql`.

## Docker / Docker Compose

Se incluye un `Dockerfile` y un `docker-compose.yml` para facilitar el despliegue local o en producción. Ejecuta:

```bash
docker-compose up --build
```

Esto levantará contenedores para la aplicación, MongoDB y Redis.

## Pruebas

Se recomienda añadir pruebas con **pytest**. Puedes crear un directorio `tests/` y estructurar tus tests allí.
