FROM python:3.11-slim

WORKDIR /app

# Instalar solo lo necesario (sin libpq, porque usas SQLite)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Verificar que uvicorn esté disponible
RUN python -c "import uvicorn; print('✅ uvicorn OK')"

# Copiar SOLO la carpeta backend
COPY backend/ ./backend/

# Asegurar que __init__.py exista (si no, créalo localmente)
RUN touch backend/__init__.py

# Iniciar
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]