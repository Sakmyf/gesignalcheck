# Usa Python 3.11 base
FROM python:3.11-slim

# Instala dependencias del sistema (solo si usas PostgreSQL; para SQLite, puedes omitir libpq-dev)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia requirements.txt y instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia SOLO la carpeta backend (y sus archivos)
COPY backend/ ./backend/

# Asegura que backend tenga __init__.py (si no existe, créalo en tu repo)
# (puedes añadir: RUN touch backend/__init__.py si quieres forzarlo)

# Comando de inicio
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]