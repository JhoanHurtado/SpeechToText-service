"""
Módulo de seguridad para la autenticación por clave de API.
"""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from .. import config

# Define el esquema de seguridad: buscará una cabecera llamada "X-API-Key"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Dependencia que valida la clave de API proporcionada en la cabecera.
    """
    if api_key == config.API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )