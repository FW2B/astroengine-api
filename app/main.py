"""
AstroEngine API - Ponto de Entrada Principal

Motor de cálculo astrológico de alta precisão baseado na Swiss Ephemeris.
Licenciado sob GNU Affero General Public License v3.0 (AGPL-3.0).

Copyright (C) 2026 FW2B - Frameworks to Business
Código-fonte: https://github.com/FW2B/astroengine-api
"""
import logging
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import natal, synastry, transits, composite, planets

# --- Logging Estruturado ---
settings = get_settings()


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL), handlers=[handler])
logger = logging.getLogger("astroengine")


# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AstroEngine API iniciando...")
    logger.info(f"Sistema de casas padrão: {settings.DEFAULT_HOUSE_SYSTEM}")
    logger.info(f"Rate limit: {settings.RATE_LIMIT_PER_MINUTE} req/min")
    yield
    logger.info("AstroEngine API encerrando...")


# --- Aplicação FastAPI ---
app = FastAPI(
    title="AstroEngine API",
    description=(
        "Motor de cálculo astrológico de alta precisão baseado na Swiss Ephemeris. "
        "Fornece cálculos de mapas natais, sinastria, trânsitos e mapas compostos. "
        "Licenciado sob GNU AGPL v3.0."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Middlewares ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

# --- Routers ---
app.include_router(natal.router, tags=["Natal Chart"])
app.include_router(synastry.router, tags=["Synastry"])
app.include_router(transits.router, tags=["Transits"])
app.include_router(composite.router, tags=["Composite"])
app.include_router(planets.router, tags=["Planets"])


# --- Endpoints Utilitários ---
@app.get("/health", tags=["System"])
async def health_check():
    """Endpoint de health check para monitoramento do container."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "engine": "Swiss Ephemeris (pyswisseph)",
        "license": "AGPL-3.0",
    }


@app.get("/source", tags=["System"])
async def source_code():
    """
    Conformidade com a Seção 13 da AGPL: disponibiliza o link para o
    código-fonte completo desta aplicação.
    """
    return {
        "repository_url": settings.SOURCE_REPOSITORY,
        "license": "GNU Affero General Public License v3.0",
        "license_url": "https://www.gnu.org/licenses/agpl-3.0.html",
    }
