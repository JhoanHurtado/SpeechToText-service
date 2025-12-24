"""
Punto de entrada principal de la API.
Define los endpoints, la configuración de la aplicación y el ciclo de vida (startup/shutdown).
"""
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Literal
from contextlib import asynccontextmanager
from fastapi.concurrency import run_in_threadpool

from .core import loader, s3_handler, security
from . import config
from .services import stt, tts

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación. Carga los modelos al inicio
    y libera los recursos al final.
    """
    # --- Startup ---
    print("Cargando modelos...")
    # Ejecuta las cargas de modelos (síncronas y pesadas) en un hilo separado
    # para no bloquear el event loop de asyncio.
    await run_in_threadpool(loader.load_stt_model)
    await run_in_threadpool(loader.load_tts_models)
    await loader.create_s3_client()
    yield
    # --- Shutdown ---
    print("Liberando recursos...")
    await loader.close_s3_client()

app = FastAPI(
    title="API de Voz a Texto y Texto a Voz",
    description="Una API de alto rendimiento para convertir texto a voz (TTS) y voz a texto (STT).",
    version="1.0.0",
    lifespan=lifespan
)

class TTSRequest(BaseModel):
    """Modelo de datos para las peticiones al endpoint /tts."""
    text: str
    language: Literal["en", "es"] = Field("en", description="Idioma para la síntesis de voz ('en' o 'es').")

@app.post(
    "/stt",
    summary="Voz a Texto",
    dependencies=[Depends(security.get_api_key)])
async def speech_to_text(audio_file: UploadFile = File(...)):
    """
    Endpoint para convertir voz a texto.

    Recibe un archivo de audio, lo transcribe usando el modelo STT y devuelve el texto.

    Args:
        audio_file (UploadFile): El archivo de audio a transcribir.
    """
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser de tipo audio.")
    
    try:
        audio_content = await audio_file.read()
        transcribed_text = stt.transcribe_audio(audio_content)
        return JSONResponse(content={"transcription": transcribed_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la transcripción: {str(e)}")

@app.post(
    "/tts",
    summary="Texto a Voz",
    dependencies=[Depends(security.get_api_key)])
async def text_to_speech(request: TTSRequest):
    """
    Endpoint para convertir texto a voz.

    Recibe un texto y un idioma, genera el audio correspondiente, lo sube a S3
    y devuelve una URL prefirmada para su descarga.

    Args:
        request (TTSRequest): El cuerpo de la petición con el texto y el idioma.
    """
    try:
        audio_data = tts.generate_speech(request.text, request.language)
        # Construye la ruta completa del archivo incluyendo el prefijo
        file_name = f"{config.S3_KEY_PREFIX}tts-audio-{uuid.uuid4()}.wav"
        audio_url = await s3_handler.upload_audio_to_s3(audio_data, file_name)
        return JSONResponse(content={"audio_url": audio_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la síntesis de voz: {str(e)}")