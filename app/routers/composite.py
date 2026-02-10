"""
AstroEngine API - Endpoint /composite
"""
import logging
from fastapi import APIRouter, Depends

from app.models.schemas import (
    SynastryInput,
    CompositeChart,
    PlanetPosition,
    HouseCusp,
)
from app.services.astronomy_calc import (
    calculate_natal_chart,
    calculate_composite_midpoint,
)
from app.services.zodiac import longitude_to_sign
from app.services.aspects import calculate_aspects
from app.middleware.auth import verify_api_key
from app.config import get_settings

logger = logging.getLogger("astroengine")
router = APIRouter()


@router.post(
    "/composite",
    response_model=CompositeChart,
    summary="Gera o mapa composto entre duas pessoas",
    description=(
        "Calcula o ponto médio de cada par de planetas correspondentes "
        "entre duas pessoas, gerando um mapa único que representa a relação."
    ),
)
async def composite(
    data: SynastryInput,
    api_key: str = Depends(verify_api_key),
) -> CompositeChart:
    logger.info(
        f"Calculando mapa composto entre: {data.person1.name} e {data.person2.name}"
    )

    chart1 = calculate_natal_chart(data.person1)
    chart2 = calculate_natal_chart(data.person2)

    # Calcular pontos médios dos planetas
    composite_planets: list[PlanetPosition] = []
    for p1 in chart1.planets:
        # Encontrar o planeta correspondente no chart2
        p2 = next((p for p in chart2.planets if p.planet == p1.planet), None)
        if p2 is None:
            continue

        midpoint = calculate_composite_midpoint(p1.absolute_degree, p2.absolute_degree)
        sign, degree = longitude_to_sign(midpoint)

        composite_planets.append(
            PlanetPosition(
                planet=p1.planet,
                sign=sign,
                degree=round(degree, 4),
                absolute_degree=round(midpoint, 4),
                house=0,  # Casas serão recalculadas abaixo
                retrograde=False,
            )
        )

    # Calcular pontos médios do Ascendente e MC para as casas compostas
    asc_midpoint = calculate_composite_midpoint(
        chart1.ascendant.absolute_degree, chart2.ascendant.absolute_degree
    )
    mc_midpoint = calculate_composite_midpoint(
        chart1.midheaven.absolute_degree, chart2.midheaven.absolute_degree
    )

    # Gerar casas compostas usando Equal House a partir do ASC composto
    composite_houses: list[HouseCusp] = []
    for i in range(12):
        cusp_lon = (asc_midpoint + i * 30) % 360
        sign, degree = longitude_to_sign(cusp_lon)
        composite_houses.append(
            HouseCusp(
                house=i + 1,
                sign=sign,
                degree=round(degree, 4),
                absolute_degree=round(cusp_lon, 4),
            )
        )

    # Atribuir casas aos planetas compostos
    raw_cusps = [h.absolute_degree for h in composite_houses]
    from app.services.zodiac import determine_house

    for planet in composite_planets:
        planet.house = determine_house(planet.absolute_degree, raw_cusps)

    # Calcular aspectos do mapa composto
    settings = get_settings()
    composite_aspects = calculate_aspects(composite_planets, orbs=settings.orbs)

    logger.info(
        f"Mapa composto calculado: {len(composite_aspects)} aspectos encontrados"
    )

    return CompositeChart(
        person1_name=data.person1.name,
        person2_name=data.person2.name,
        planets=composite_planets,
        houses=composite_houses,
        aspects=composite_aspects,
    )
