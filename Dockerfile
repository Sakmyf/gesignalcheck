FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema (opcional para SQLite)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Verificar que uvicorn esté instalado
RUN python -c "import uvicorn; print('✅ uvicorn instalado')"

# Copiar solo el backend
COPY backend/ ./backend/

# Comando de inicio
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]