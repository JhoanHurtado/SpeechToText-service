from .loader import get_s3_client
from ..config import S3_BUCKET_NAME

async def upload_audio_to_s3(audio_data: bytes, file_name: str) -> str:
    """
    Sube datos de audio a S3 y genera una URL prefirmada para acceder al archivo.

    :param audio_data: Los bytes del archivo de audio.
    :param file_name: El nombre (key) con el que se guardará el archivo en S3.
    :return: Una URL prefirmada con una validez de 30 minutos.
    """
    client = get_s3_client()
    if not client:
        raise RuntimeError("El cliente S3 no está inicializado.")

    await client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=file_name,
        Body=audio_data,
        ContentType='audio/wav'  # Coqui TTS genera WAV
    )

    # Genera una URL prefirmada que expira en 30 minutos (1800 segundos)
    presigned_url = await client.generate_presigned_url(
        'get_object',
        Params={'Bucket': S3_BUCKET_NAME, 'Key': file_name},
        ExpiresIn=1800
    )

    return presigned_url