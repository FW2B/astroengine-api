"""
AstroEngine API - Endpoint /natal_chart
"""
import logging
from fastapi import APIRouter, Depends

from app.models.schemas import BirthData, NatalChart
from app.services.astronomy_calc import calculate_natal_chart
from app.middleware.auth import verify_api_key

logger = logging.getLogger("astroengine")
router = APIRouter()


@router.post(
    "/natal_chart",
    response_model=NatalChart,
    summary="Calcula o mapa astral natal completo",
    description=(
        "Calcula o mapa astral natal completo para uma pessoa, incluindo "
        "posições dos 10 corpos celestes principais, Ascendente, Meio do Céu, "
        "cúspides das 12 casas e aspectos natais."
    ),
)
async def natal_chart(
    birth_data: BirthData,
    api_key: str = Depends(verify_api_key),
) -> NatalChart:
    logger.info(f"Calculando mapa natal para: {birth_data.name}")
    chart = calculate_natal_chart(birth_data)
    logger.info(f"Mapa natal calculado com sucesso para: {birth_data.name}")
    return chart
