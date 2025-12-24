# Usamos una imagen base de Python 3.11 (versión estable y compatible con librerías de ML)
FROM python:3.11-slim

# Variables de entorno para evitar archivos .pyc y logs en buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalamos dependencias del sistema requeridas para audio y compilación
# ffmpeg y libsndfile1 son cruciales para Coqui TTS y Whisper
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos el archivo de requerimientos e instalamos las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente de la aplicación (la carpeta src)
COPY src/ src/

# Exponemos el puerto 8000
EXPOSE 8000

# Comando para ejecutar la aplicación con Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]