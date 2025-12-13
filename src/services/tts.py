from ..core.loader import get_tts_model
import io

def generate_speech(text: str) -> bytes:
    """
    Sintetiza texto a voz usando el modelo Coqui TTS.

    :param text: El texto a convertir.
    :return: Un stream de bytes con el audio en formato WAV.
    """
    tts_model = get_tts_model()
    if not tts_model:
        raise RuntimeError("El modelo TTS no está cargado.")

    # Usamos un buffer en memoria para que tts_to_file escriba directamente en él.
    buffer = io.BytesIO()

    # Para modelos de un solo hablante/idioma, los parámetros speaker y language no son necesarios.
    if tts_model.is_multi_speaker:
        tts_model.tts_to_file(text=text, file_path=buffer, speaker=tts_model.speakers[0], language=tts_model.languages[0])
    else:
        tts_model.tts_to_file(text=text, file_path=buffer)

    # Regresamos al inicio del buffer para leer su contenido.
    buffer.seek(0)

    return buffer.read()