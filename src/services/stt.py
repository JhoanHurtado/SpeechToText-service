from ..core.loader import get_stt_model
import io

def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe un stream de bytes de audio usando el modelo faster-whisper.

    :param audio_bytes: Los bytes del archivo de audio.
    :return: El texto transcrito.
    """
    stt_model = get_stt_model()
    if not stt_model:
        raise RuntimeError("El modelo STT no está cargado.")

    audio_file = io.BytesIO(audio_bytes)
    segments, _ = stt_model.transcribe(audio_file, beam_size=5)
    
    return " ".join([segment.text for segment in segments])