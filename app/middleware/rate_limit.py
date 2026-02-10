"""
AstroEngine API - Middleware de Rate Limiting

Implementação simples em memória. Para produção com múltiplas instâncias,
considerar usar Redis como backend.
"""
import time
import logging
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings

logger = logging.getLogger("astroengine")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting baseado em chave de API ou IP."""

    def __init__(self, app):
        super().__init__(app)
        self.requests: dict[str, list[float]] = defaultdict(list)
        settings = get_settings()
        self.limit = settings.RATE_LIMIT_PER_MINUTE
        self.window = 60  # 1 minuto

    async def dispatch(self, request: Request, call_next):
        # Identificar o cliente pela API key ou IP
        client_id = request.headers.get("X-API-Key") or request.client.host
        now = time.time()

        # Limpar requisições antigas
        self.requests[client_id] = [
            t for t in self.requests[client_id] if now - t < self.window
        ]

        if len(self.requests[client_id]) >= self.limit:
            logger.warning(f"Rate limit excedido para {client_id}")
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {self.limit} requests per minute.",
            )

        self.requests[client_id].append(now)
        response = await call_next(request)
        return response
