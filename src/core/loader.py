import torch
from TTS.api import TTS
from faster_whisper import WhisperModel
from aiobotocore.session import get_session
from .. import config

# Determinar el dispositivo (GPU si está disponible, si no CPU)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
COMPUTE_TYPE = "float16" if torch.cuda.is_available() else "int8"

stt_model = None
tts_model = None
s3_client = None

def load_stt_model():
    """Carga el modelo de Speech-to-Text (faster-whisper) en memoria."""
    global stt_model
    print(f"Cargando modelo STT '{config.STT_MODEL}' en dispositivo '{DEVICE}'...")
    stt_model = WhisperModel(config.STT_MODEL, device=DEVICE, compute_type=COMPUTE_TYPE)
    print("Modelo STT cargado.")

def load_tts_model():
    """Carga el modelo de Text-to-Speech (Coqui TTS) en memoria."""
    global tts_model
    print(f"Cargando modelo TTS '{config.TTS_MODEL}' en dispositivo '{DEVICE}'...")
    tts_model = TTS(model_name=config.TTS_MODEL).to(DEVICE)
    print("Modelo TTS cargado.")

async def create_s3_client():
    """Crea y devuelve un cliente S3 asíncrono."""
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
    """Cierra la conexión del cliente S3."""
    if s3_client:
        await s3_client.close()
        print("Cliente S3 cerrado.")

def get_stt_model() -> WhisperModel:
    return stt_model

def get_tts_model() -> TTS:
    return tts_model

def get_s3_client():
    return s3_client