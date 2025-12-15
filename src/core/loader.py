"""
Módulo para la carga y gestión centralizada de los modelos de IA y clientes externos.
Carga los modelos una sola vez al inicio de la aplicación para optimizar el rendimiento.
"""
import torch
from TTS.api import TTS
from faster_whisper import WhisperModel
from aiobotocore.session import get_session
from .. import config
import collections

try:
    from TTS.utils.radam import RAdam
    # Añadimos RAdam, defaultdict y dict a la lista global de objetos seguros para la deserialización.
    torch.serialization.add_safe_globals([RAdam, collections.defaultdict, dict])
except ImportError:
    print("Advertencia: No se pudo importar RAdam. Esto puede no ser un problema si no se usan modelos antiguos.")

# Determinar el dispositivo (GPU si está disponible, si no CPU)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
COMPUTE_TYPE = "float16" if torch.cuda.is_available() else "int8"

# --- Variables Globales para Modelos y Clientes ---
# Se inicializan como None y se cargan durante el ciclo de vida de la aplicación.
stt_model = None
_tts_models = {} # Diccionario para almacenar los modelos TTS por idioma
s3_client = None

def load_stt_model():
    """Carga el modelo de Speech-to-Text (faster-whisper) en la variable global `stt_model`."""
    global stt_model
    print(f"Cargando modelo STT '{config.STT_MODEL}' en dispositivo '{DEVICE}'...")
    stt_model = WhisperModel(config.STT_MODEL, device=DEVICE, compute_type=COMPUTE_TYPE)
    print("Modelo STT cargado.")

def load_tts_models():
    """Carga los modelos de Text-to-Speech (inglés y español) en memoria."""
    global _tts_models # Almacena los modelos en un diccionario cacheado por idioma.
    models_to_load = {
        "en": config.TTS_MODEL_EN,
        "es": config.TTS_MODEL_ES
    }
    for lang, model_name in models_to_load.items():
        print(f"Cargando modelo TTS para '{lang}' ('{model_name}') en dispositivo '{DEVICE}'...")
        _tts_models[lang] = TTS(model_name=model_name).to(DEVICE)
        print(f"Modelo TTS para '{lang}' cargado.")


async def create_s3_client():
    """Crea un cliente S3 asíncrono y lo almacena en la variable global `s3_client`."""
    global s3_client
    print("Creando cliente S3...")
    session = get_session()
    # session.create_client devuelve un contexto, no un cliente directamente.
    # Usamos __aenter__ para obtener el cliente y guardarlo globalmente.
    s3_client = await session.create_client(
        's3',
        region_name=config.AWS_REGION,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID
    ).__aenter__()
    print("Cliente S3 creado.")

async def close_s3_client():
    """Cierra la conexión del cliente S3 si existe."""
    if s3_client:
        await s3_client.close()
        print("Cliente S3 cerrado.")

def get_stt_model() -> WhisperModel:
    """
    Retorna la instancia global del modelo STT.

    Returns:
        WhisperModel: La instancia del modelo faster-whisper.
    """
    return stt_model

def get_tts_model(lang: str) -> TTS:
    """
    Obtiene un modelo TTS precargado para un idioma específico.

    Args:
        lang (str): El código del idioma ('en' o 'es').

    Returns:
        TTS: La instancia del modelo Coqui TTS para el idioma solicitado.
    
    Raises:
        RuntimeError: Si el modelo para el idioma solicitado no está cargado.
    """
    model = _tts_models.get(lang)
    if not model:
        raise RuntimeError(f"El modelo TTS para el idioma '{lang}' no está cargado.")
    return model

def get_s3_client():
    """Retorna la instancia global del cliente S3."""
    return s3_client