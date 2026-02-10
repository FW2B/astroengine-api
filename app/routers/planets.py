"""
AstroEngine API - Endpoint /planets/now
"""
import logging
from fastapi import APIRouter, Depends

from app.models.schemas import PlanetPosition
from app.services.astronomy_calc import calculate_current_positions
from app.middleware.auth import verify_api_key

logger = logging.getLogger("astroengine")
router = APIRouter()


@router.get(
    "/planets/now",
    response_model=list[PlanetPosition],
    summary="Retorna as posições planetárias atuais",
    description=(
        "Retorna as posições planetárias atuais, útil para dashboards e widgets."
    ),
)
async def planets_now(
    api_key: str = Depends(verify_api_key),
) -> list[PlanetPosition]:
    logger.info("Calculando posições planetárias atuais")
    positions = calculate_current_positions()
    return positions
