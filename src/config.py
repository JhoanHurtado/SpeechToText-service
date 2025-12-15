"""
Módulo de configuración para cargar variables de entorno y parámetros de la aplicación.
Utiliza python-dotenv para cargar un archivo .env en el entorno de ejecución.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Configuración de AWS S3 ---
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_KEY_PREFIX = os.getenv("S3_KEY_PREFIX", "") # prefijo o carpeta en el bucket

# --- Configuración de Modelos de IA ---
STT_MODEL = os.getenv("STT_MODEL", "base") # "base", "small", "medium", "large-v2"
# Modelos TTS Tacotron2-DDC para inglés y español.
TTS_MODEL_EN = os.getenv("TTS_MODEL_EN", "tts_models/en/ljspeech/tacotron2-DDC")
TTS_MODEL_ES = os.getenv("TTS_MODEL_ES", "tts_models/es/mai/tacotron2-DDC")