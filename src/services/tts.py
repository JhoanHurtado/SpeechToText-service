"""
Servicio de Text-to-Speech (TTS).
Encapsula la lógica de síntesis de voz.
"""
from ..core.loader import get_tts_model
import io

def generate_speech(text: str, lang: str) -> bytes:
    """
    Sintetiza texto a voz en un idioma específico utilizando el modelo Coqui TTS correspondiente.

    Args:
        text (str): El texto a convertir en voz.
        lang (str): El idioma del texto ('en' o 'es').

    Returns:
        bytes: Un stream de bytes con el audio resultante en formato WAV.
    """
    tts_model = get_tts_model(lang)

    # buffer en memoria para que tts_to_file escriba directamente en él.
    buffer = io.BytesIO()

    # cosntruir los argumentos para tts_to_file dinámicamente, ya que algunos
    # modelos son multi-hablante y otros no.
    tts_kwargs = {}
    if tts_model.is_multi_speaker:
        # uso el primer hablante disponible por defecto.
        tts_kwargs["speaker"] = tts_model.speakers[0]

    tts_model.tts_to_file(text=text, file_path=buffer, **tts_kwargs)

    # regresa al inicio del buffer para leer su contenido.
    buffer.seek(0)
    return buffer.read()