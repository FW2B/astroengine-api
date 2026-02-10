"""
AstroEngine API - Middleware de Autenticação por API Key
"""
import logging
from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.config import get_settings

logger = logging.getLogger("astroengine")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verifica se a chave de API fornecida é válida."""
    settings = get_settings()

    if not api_key:
        logger.warning("Requisição sem chave de API")
        raise HTTPException(status_code=401, detail="API key is missing")

    if api_key not in settings.API_KEYS:
        logger.warning(f"Chave de API inválida: {api_key[:8]}...")
        raise HTTPException(status_code=403, detail="Invalid API key")

    return api_key
