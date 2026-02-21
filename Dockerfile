# Usa Python 3.11 base
FROM python:3.11-slim

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia solo requirements.txt primero (para cachear dependencias)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Comando de inicio
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]