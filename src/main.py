import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi.concurrency import run_in_threadpool

from .core import loader, s3_handler
from . import config
from .services import stt, tts

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carga los modelos al iniciar la aplicación
    print("Cargando modelos...")
    # Ejecuta la carga de modelos (síncrona) en un hilo para no bloquear el event loop
    await run_in_threadpool(loader.load_stt_model)
    await run_in_threadpool(loader.load_tts_model)
    await loader.create_s3_client()
    yield
    # Limpieza (si es necesario) al apagar
    print("Liberando recursos...")
    await loader.close_s3_client()

app = FastAPI(
    title="API de Voz a Texto y Texto a Voz",
    description="Una API de alto rendimiento para convertir texto a voz (TTS) y voz a texto (STT).",
    version="1.0.0",
    lifespan=lifespan
)

class TTSRequest(BaseModel):
    text: str

@app.post("/stt", summary="Voz a Texto")
async def speech_to_text(audio_file: UploadFile = File(...)):
    """
    Recibe un archivo de audio y devuelve su transcripción.
    """
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser de tipo audio.")
    
    try:
        audio_content = await audio_file.read()
        transcribed_text = stt.transcribe_audio(audio_content)
        return JSONResponse(content={"transcription": transcribed_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la transcripción: {str(e)}")

@app.post("/tts", summary="Texto a Voz")
async def text_to_speech(request: TTSRequest):
    """
    Recibe un texto, genera el audio correspondiente, lo sube a S3 y devuelve la URL.
    """
    try:
        audio_data = tts.generate_speech(request.text)
        # Construye la ruta completa del archivo incluyendo el prefijo
        file_name = f"{config.S3_KEY_PREFIX}tts-audio-{uuid.uuid4()}.wav"
        audio_url = await s3_handler.upload_audio_to_s3(audio_data, file_name)
        return JSONResponse(content={"audio_url": audio_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la síntesis de voz: {str(e)}")