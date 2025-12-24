# API de Voz a Texto (STT) y Texto a Voz (TTS) de Alto Rendimiento
 
Este proyecto implementa una API RESTful de alta velocidad utilizando FastAPI para realizar dos tareas principales:
1.  **Voz a Texto (STT)**: Transcribe un archivo de audio a texto utilizando `faster-whisper` para una inferencia ultrarrápida.
2.  **Texto a Voz (TTS)**: Convierte un texto en **inglés o español** a un archivo de audio `.wav` utilizando `Coqui TTS`, lo sube a un bucket de S3 y devuelve una **URL prefirmada** segura y temporal para su acceso.
 
La arquitectura está diseñada para ser asíncrona y de alto rendimiento, con soporte para aceleración por GPU.

## ✨ Características Principales

- **Asíncrono de Extremo a Extremo**: Construido con FastAPI y `aiobotocore` para un manejo no bloqueante de las peticiones y subidas de archivos.
- **Inferencia Rápida**: Utiliza `faster-whisper`, una reimplementación optimizada de Whisper para transcripciones hasta 4 veces más rápidas.
- **TTS Bilingüe (EN/ES)**: Soporta la generación de voz en inglés y español utilizando modelos `Tacotron2-DDC` de alta calidad.
- **Seguridad**: Los archivos de audio generados se exponen a través de URLs prefirmadas de S3 con tiempo de expiración, en lugar de URLs públicas.
- **Protección de Endpoints**: Uso de claves de API (`API Key`) para asegurar el acceso a los endpoints y prevenir el uso no autorizado.
- **Optimización de Recursos**: Carga los modelos de IA en memoria una sola vez al inicio de la aplicación para minimizar la latencia en las peticiones.
- **Soporte para GPU**: Detecta y utiliza automáticamente una GPU (CUDA) si está disponible, para una aceleración masiva de la inferencia.
 
## 🚀 Stack Tecnológico
 
| Tarea                 | Librería/Módulo        | Modelo Recomendado        | Razón Principal                                                                                             |
| --------------------- | ---------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Framework API**     | `FastAPI`              | N/A                       | Máximo rendimiento y soporte nativo para `async/await`.                                                     |
| **Servidor ASGI**     | `Uvicorn` / `Gunicorn` | N/A                       | Servidor ASGI ultrarrápido, gestionado por Gunicorn en producción para robustez.                            |
| **Voz a Texto (STT)** | `faster-whisper`       | `base` o `small`          | La implementación de Whisper más rápida. Ofrece gran precisión con latencia muy baja para audios cortos.      |
| **Texto a Voz (TTS)** | `Coqui TTS` (`TTS`)    | `tts_models/en/ljspeech/tacotron2-DDC` (EN) y `tts_models/es/mai/tacotron2-DDC` (ES) | Modelos de alta calidad con una arquitectura consistente para ambos idiomas.                                 |
| **Almacenamiento S3** | `aiobotocore`          | N/A                       | Permite interactuar con S3 de forma asíncrona, crucial para no bloquear la API durante la subida de archivos. |
| **Estructura Datos**  | `Pydantic`             | N/A                       | Validación de datos de entrada/salida integrada en FastAPI.                                                 |
| **Seguridad API**     | `FastAPI.Security`     | N/A                       | Implementación sencilla y estándar de autenticación por clave de API en el header.                          |
 
## 📂 Estructura del Proyecto
 
```
project_root/
├── src/
│   ├── main.py             # Endpoints de la API (FastAPI)
│   ├── config.py           # Configuración (variables de entorno)
│   ├── core/
│   │   ├── s3_handler.py   # Gestión asíncrona con S3 (Aiobotocore)
│   │   ├── loader.py       # Carga de modelos STT y TTS al inicio
│   │   └── security.py     # Lógica de autenticación (API Key)
│   └── services/
│       ├── stt.py          # Lógica de transcripción (faster-whisper)
│       └── tts.py          # Lógica de generación de audio (Coqui TTS)
├── requirements.txt      # Dependencias del proyecto
└── .env.example          # Ejemplo de variables de entorno
```

## ⚙️ Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio> && cd SpeechToText-service
    ```

2.  **Instalar dependencias del sistema:**
    Los modelos TTS requieren `espeak-ng` para la fonetización del texto. `libsndfile1` es necesaria para el procesamiento de audio.
    ```bash
    sudo apt-get update && sudo apt-get install -y espeak-ng libsndfile1
    ```

3.  **Crear y activar un entorno virtual de Python:**
    Se recomienda usar Python 3.11 o superior.
    ```bash
    python3.11 -m venv .venv
    source .venv/bin/activate
    ```

4.  **Instalar dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configurar variables de entorno:**
    Crea un archivo `.env` a partir de `.env.example` y complétalo con tus credenciales de AWS y configuración de S3.
    ```bash
    cp .env.example .env
    # Edita el archivo .env con tus valores
    ```

## ⚡️ Ejecución

Para iniciar el servidor en modo de desarrollo, ejecuta:

```bash
uvicorn src.main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`. Puedes acceder a la documentación interactiva de Swagger en `http://127.0.0.1:8000/docs`.

## 📦 Despliegue en Producción

Para producción, se recomienda usar `gunicorn` como gestor de procesos para los workers de `uvicorn`. Esto proporciona concurrencia y robustez.

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
```

*   `-w 4`: Inicia 4 procesos "worker". El número ideal es `(2 * número_de_cores_cpu) + 1`.
*   `-k uvicorn.workers.UvicornWorker`: Especifica que `uvicorn` manejará las peticiones dentro de cada worker de `gunicorn`.

**Recomendación de Entorno:** Para la máxima velocidad, despliega en una máquina virtual o contenedor Docker con una **GPU** y las librerías CUDA/cuDNN instaladas. La inferencia en GPU es significativamente más rápida, especialmente para TTS.


## ⚙️ Configuración Local (Python)

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio> && cd SpeechToText-service
    ```

2.  **Instalar dependencias del sistema:**
    ```bash
    sudo apt-get update && sudo apt-get install -y espeak-ng libsndfile1
    ```

3.  **Configurar entorno:**
    ```bash
    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    # Edita el .env con los valores de la tabla de Variables de Entorno
    ```

4.  **Ejecutar:**
    ```bash
    uvicorn src.main:app --reload
    ```

## 🐳 Ejecución con Docker (Recomendado)

1.  Asegúrate de tener el archivo `.env` configurado.
2.  Levanta el servicio:
    ```bash
    docker-compose up -d --build
    ```

    *Nota: Docker gestionará automáticamente los volúmenes para cachear los modelos de IA, evitando descargas repetidas.*

## ☁️ CI/CD y Despliegue en AWS Lightsail

El proyecto cuenta con pipelines de **GitHub Actions** configurados para desplegar automáticamente en una instancia de **AWS Lightsail (VM)** mediante SSH y Docker Compose.

### Estrategia de Ramas y Ambientes

| Rama | Ambiente | Puerto | Modelo STT | Prefijo S3 |
| :--- | :--- | :--- | :--- | :--- |
| `develop` | Desarrollo | `8001` | `base` | `dev/` |
| `quality` | Calidad (QA) | `8002` | `base` | `qa/` |
| `main` | Producción | `8000` | `medium` | `prod/` |

### 🔐 Secretos de GitHub Requeridos

Para que los flujos de trabajo funcionen correctamente, debes configurar los siguientes secretos en tu repositorio (Settings > Secrets and variables > Actions):

#### Credenciales de Conexión (SSH)
*   `LIGHTSAIL_HOST`: Dirección IP pública de tu instancia Lightsail.
*   `LIGHTSAIL_USERNAME`: Usuario SSH (ej: `ubuntu` o `bitnami`).
*   `LIGHTSAIL_SSH_KEY`: Clave privada SSH (.pem) para acceder a la instancia.

#### Variables de Entorno de la Aplicación
Estas se inyectan en el contenedor durante el despliegue:
*   `API_KEY`: Clave para proteger los endpoints.
*   `APP_AWS_ACCESS_KEY_ID`: Credenciales para que la app acceda a S3.
*   `APP_AWS_SECRET_ACCESS_KEY`: Credenciales para que la app acceda a S3.
*   `AWS_REGION`: Región de AWS para S3.

📦 Producción

Para despliegues manuales en producción, se recomienda el uso de gunicorn para gestionar los workers de uvicorn:
Bash

gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app

    Consejo de Rendimiento: Para obtener la máxima velocidad, despliega en una instancia con GPU NVIDIA y asegúrate de que los drivers CUDA estén instalados. La inferencia en GPU reduce drásticamente los tiempos de procesamiento de TTS.