"""
AstroEngine API - Endpoint /transits
"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends

from app.models.schemas import TransitInput, TransitReport, PlanetPosition
from app.services.astronomy_calc import (
    calculate_natal_chart,
    calculate_planet_positions,
    _parse_datetime,
    _datetime_to_jd,
)
from app.services.aspects import calculate_aspects
from app.middleware.auth import verify_api_key
from app.config import get_settings

logger = logging.getLogger("astroengine")
router = APIRouter()


@router.post(
    "/transits",
    response_model=TransitReport,
    summary="Calcula trânsitos planetários em relação a um mapa natal",
    description=(
        "Calcula as posições planetárias atuais (ou de uma data específica) "
        "e os aspectos que formam com as posições do mapa natal."
    ),
)
async def transits(
    data: TransitInput,
    api_key: str = Depends(verify_api_key),
) -> TransitReport:
    logger.info(f"Calculando trânsitos para: {data.birth_data.name}")

    # Calcular mapa natal
    natal_chart = calculate_natal_chart(data.birth_data)

    # Determinar data do trânsito
    if data.transit_datetime_utc:
        transit_dt = _parse_datetime(data.transit_datetime_utc)
        transit_dt_str = data.transit_datetime_utc
    else:
        transit_dt = datetime.now(timezone.utc)
        transit_dt_str = transit_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Calcular posições dos planetas em trânsito
    transit_jd = _datetime_to_jd(transit_dt)
    transit_planets = calculate_planet_positions(transit_jd)

    # Calcular aspectos entre trânsitos e natal
    settings = get_settings()
    transit_aspects = calculate_aspects(
        transit_planets, natal_chart.planets, orbs=settings.orbs
    )

    logger.info(
        f"Trânsitos calculados: {len(transit_aspects)} aspectos encontrados"
    )

    return TransitReport(
        natal_chart=natal_chart,
        transit_datetime_utc=transit_dt_str,
        transit_planets=transit_planets,
        transit_aspects=transit_aspects,
    )
