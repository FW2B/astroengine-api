"""
AstroEngine API - Endpoint /synastry
"""
import logging
from fastapi import APIRouter, Depends

from app.models.schemas import SynastryInput, SynastryReport
from app.services.astronomy_calc import calculate_natal_chart
from app.services.aspects import calculate_aspects
from app.middleware.auth import verify_api_key
from app.config import get_settings

logger = logging.getLogger("astroengine")
router = APIRouter()


@router.post(
    "/synastry",
    response_model=SynastryReport,
    summary="Realiza a sinastria entre duas pessoas",
    description=(
        "Calcula os mapas natais de duas pessoas e os aspectos inter-cartas "
        "(sinastria), comparando as posições planetárias de ambos os mapas."
    ),
)
async def synastry(
    data: SynastryInput,
    api_key: str = Depends(verify_api_key),
) -> SynastryReport:
    logger.info(
        f"Calculando sinastria entre: {data.person1.name} e {data.person2.name}"
    )

    chart1 = calculate_natal_chart(data.person1)
    chart2 = calculate_natal_chart(data.person2)

    # Calcular aspectos inter-cartas
    settings = get_settings()
    synastry_aspects = calculate_aspects(
        chart1.planets, chart2.planets, orbs=settings.orbs
    )

    logger.info(
        f"Sinastria calculada: {len(synastry_aspects)} aspectos encontrados"
    )

    return SynastryReport(
        person1_chart=chart1,
        person2_chart=chart2,
        synastry_aspects=synastry_aspects,
    )
