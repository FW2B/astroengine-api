# =============================================================================
# AstroEngine API - Dockerfile (Multi-Stage Build)
# Motor de cálculo astrológico baseado na Swiss Ephemeris
# Licença: GNU AGPL v3.0
# Código-fonte: https://github.com/FW2B/astroengine-api
# =============================================================================

# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

# Instalar dependências de compilação necessárias para pyswisseph
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final image
FROM python:3.11-slim

LABEL maintainer="FW2B - Frameworks to Business"
LABEL description="AstroEngine API - Motor de cálculo astrológico"
LABEL license="AGPL-3.0"
LABEL source="https://github.com/FW2B/astroengine-api"

WORKDIR /app

# Copiar dependências instaladas do builder
COPY --from=builder /install /usr/local

# Copiar código da aplicação
COPY app/ ./app/

# Variáveis de ambiente padrão
ENV PORT=8000
ENV LOG_LEVEL=INFO
ENV API_KEYS=dev-key-cosmic-suite
ENV ALLOWED_ORIGINS=*
ENV DEFAULT_HOUSE_SYSTEM=placidus
ENV SOURCE_REPOSITORY=https://github.com/FW2B/astroengine-api

# Expor porta
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

# Executar com uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
