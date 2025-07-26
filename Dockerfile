# Usa una imagen oficial ligera de Python
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . /app

# Actualiza pip y corrige errores con bcrypt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir bcrypt==4.0.1 && \
    pip install --no-cache-dir -r requirements.txt

# Expone el puerto para la aplicación
EXPOSE 8000

# Comando para arrancar Uvicorn correctamente
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
