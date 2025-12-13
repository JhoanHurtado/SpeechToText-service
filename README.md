# API de Voz a Texto (STT) y Texto a Voz (TTS) de Alto Rendimiento

Este proyecto implementa una API RESTful de alta velocidad utilizando FastAPI para realizar dos tareas principales:
1.  **Texto a Voz (TTS)**: Convierte un texto en un archivo de audio y devuelve la URL pública de S3.
2.  **Voz a Texto (STT)**: Transcribe un archivo de audio corto a texto.

La arquitectura está optimizada para inferencia rápida, ideal para audios de 3 a 10 segundos, con un máximo de un minuto.

## 🚀 Stack Tecnológico

| Tarea                 | Librería/Módulo        | Modelo Recomendado        | Razón Principal                                                                                             |
| --------------------- | ---------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Framework API**     | `FastAPI`              | N/A                       | Máximo rendimiento y soporte nativo para `async/await`.                                                     |
| **Servidor ASGI**     | `Uvicorn`              | N/A                       | Servidor ASGI ultrarrápido para FastAPI.                                                                    |
| **Voz a Texto (STT)** | `faster-whisper`       | `base` o `small`          | La implementación de Whisper más rápida. Ofrece gran precisión con latencia muy baja para audios cortos.      |
| **Texto a Voz (TTS)** | `Coqui TTS` (`TTS`)    | `tts_models/en/ljspeech/tacotron2-DDC` | Mejor equilibrio entre calidad y velocidad. Ideal para inferencia rápida en CPU/GPU.                  |
| **Almacenamiento S3** | `aiobotocore`          | N/A                       | Permite interactuar con S3 de forma asíncrona, crucial para no bloquear la API durante la subida de archivos. |
| **Estructura Datos**  | `Pydantic`             | N/A                       | Validación de datos de entrada/salida integrada en FastAPI.                                                 |

## 📂 Estructura del Proyecto

```
project_root/
├── app/
│   ├── main.py             # Endpoints de la API (FastAPI)
│   ├── config.py           # Configuración (variables de entorno)
│   ├── core/
│   │   ├── s3_handler.py   # Gestión asíncrona con S3 (Aiobotocore)
│   │   └── loader.py       # Carga de modelos STT y TTS al inicio
│   └── services/
│       ├── stt.py          # Lógica de transcripción (faster-whisper)
│       └── tts.py          # Lógica de generación de audio (Coqui TTS)
├── requirements.txt      # Dependencias del proyecto
└── .env.example          # Ejemplo de variables de entorno
```

## ⚙️ Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd <nombre-del-repositorio>
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instalar dependencias:**
    Asegúrate de tener `libsndfile1` instalado en sistemas Debian/Ubuntu para procesar audio.
    ```bash
    sudo apt-get update && sudo apt-get install libsndfile1
    pip install -r requirements.txt
    ```

4.  **Configurar variables de entorno:**
    Crea un archivo `.env` a partir de `.env.example` y complétalo con tus credenciales de AWS y configuración de S3.
    ```bash
    cp .env.example .env
    # Edita el archivo .env con tus valores
    ```

## ⚡️ Ejecución

Para iniciar el servidor en modo de desarrollo, ejecuta:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`. Puedes acceder a la documentación interactiva de Swagger en `http://127.0.0.1:8000/docs`.

## 📦 Despliegue en Producción

Para producción, se recomienda usar `gunicorn` como gestor de procesos para los workers de `uvicorn`. Esto proporciona concurrencia y robustez.

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

*   `-w 4`: Inicia 4 procesos "worker". El número ideal es `(2 * número_de_cores_cpu) + 1`.
*   `-k uvicorn.workers.UvicornWorker`: Especifica que `uvicorn` manejará las peticiones dentro de cada worker de `gunicorn`.

**Recomendación de Entorno:** Para la máxima velocidad, despliega en una máquina virtual o contenedor Docker con una **GPU** y las librerías CUDA/cuDNN instaladas. La inferencia en GPU es significativamente más rápida, especialmente para TTS.