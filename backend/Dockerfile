# 1. Usamos una imagen base de Python ligera (asumo Python 3.10 o superior por FastAPI)
FROM python:3.11-slim

# 2. Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
# 3. Copiamos los "ingredientes" primero para aprovechar la caché de Docker
COPY requirements.txt .

# 4. Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos el resto de tu código (main.py, carpetas, etc.) al contenedor
COPY . .

# 6. Comando para encontrar ruta
ENV PYTHONPATH=/app
# OJO: Usamos host 0.0.0.0 para que sea visible fuera del contensedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]