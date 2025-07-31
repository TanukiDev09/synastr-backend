# Usa una imagen oficial de Python optimizada para producción
FROM python:3.12-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# ---- INICIO DE LA MODIFICACIÓN ----
# Instala las herramientas de construcción necesarias (como gcc)
RUN apt-get update && apt-get install -y build-essential
# ---- FIN DE LA MODIFICACIÓN ----

# Copia los archivos del backend al contenedor
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Comando para iniciar Uvicorn desde el módulo app.main
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]