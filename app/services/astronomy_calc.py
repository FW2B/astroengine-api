"""
AstroEngine API - Cálculos astronômicos com Swiss Ephemeris (pyswisseph)

Este módulo encapsula todas as chamadas à biblioteca Swiss Ephemeris,
fornecendo funções de alto nível para cálculos astrológicos.
"""
import swisseph as swe
from datetime import datetime, timezone

from app.models.schemas import (
    BirthData,
    HouseCusp,
    HouseSystem,
    NatalChart,
    PlanetPosition,
    HOUSE_SYSTEM_CODES,
)
from app.services.zodiac import longitude_to_sign, determine_house
from app.services.aspects import calculate_aspects
from app.config import get_settings

# Corpos celestes a calcular
PLANET_IDS: dict[int, str] = {
    swe.SUN: "Sun",
    swe.MOON: "Moon",
    swe.MERCURY: "Mercury",
    swe.VENUS: "Venus",
    swe.MARS: "Mars",
    swe.JUPITER: "Jupiter",
    swe.SATURN: "Saturn",
    swe.URANUS: "Uranus",
    swe.NEPTUNE: "Neptune",
    swe.PLUTO: "Pluto",
}

# Inicializar Swiss Ephemeris com efemérides Moshier (built-in)
swe.set_ephe_path("")


def _parse_datetime(dt_str: str) -> datetime:
    """Converte string ISO 8601 para datetime UTC."""
    dt_str = dt_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(dt_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _datetime_to_jd(dt: datetime) -> float:
    """Converte datetime para Julian Day."""
    hour_decimal = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    return swe.julday(dt.year, dt.month, dt.day, hour_decimal)


def _get_house_system_code(house_system: HouseSystem) -> bytes:
    """Retorna o código Swiss Ephemeris para o sistema de casas."""
    return HOUSE_SYSTEM_CODES.get(house_system.value, b"P")


def calculate_planet_positions(
    jd: float,
    cusps: list[float] | None = None,
) -> list[PlanetPosition]:
    """Calcula as posições de todos os planetas para um dado Julian Day."""
    positions: list[PlanetPosition] = []

    for planet_id, planet_name in PLANET_IDS.items():
        result, flags = swe.calc_ut(jd, planet_id)
        longitude = result[0]
        speed = result[3]  # Velocidade em longitude (graus/dia)

        sign, degree = longitude_to_sign(longitude)
        retrograde = speed < 0
        house = determine_house(longitude, cusps) if cusps else 0

        positions.append(
            PlanetPosition(
                planet=planet_name,
                sign=sign,
                degree=round(degree, 4),
                absolute_degree=round(longitude, 4),
                house=house,
                retrograde=retrograde,
            )
        )

    return positions


def calculate_houses(
    jd: float,
    latitude: float,
    longitude: float,
    house_system: HouseSystem = HouseSystem.PLACIDUS,
) -> tuple[list[HouseCusp], PlanetPosition, PlanetPosition, list[float]]:
    """
    Calcula as cúspides das casas, Ascendente e Meio do Céu.

    Retorna: (house_cusps, ascendant, midheaven, raw_cusps)
    """
    hs_code = _get_house_system_code(house_system)
    cusps, ascmc = swe.houses(jd, latitude, longitude, hs_code)

    # ascmc: [0]=ASC, [1]=MC, [2]=ARMC, [3]=Vertex, [4]=Equatorial ASC, etc.
    asc_longitude = ascmc[0]
    mc_longitude = ascmc[1]

    raw_cusps = list(cusps)

    # Construir lista de HouseCusp
    house_cusps: list[HouseCusp] = []
    for i in range(12):
        cusp_lon = cusps[i]
        sign, degree = longitude_to_sign(cusp_lon)
        house_cusps.append(
            HouseCusp(
                house=i + 1,
                sign=sign,
                degree=round(degree, 4),
                absolute_degree=round(cusp_lon, 4),
            )
        )

    # Ascendente como PlanetPosition
    asc_sign, asc_degree = longitude_to_sign(asc_longitude)
    ascendant = PlanetPosition(
        planet="Ascendant",
        sign=asc_sign,
        degree=round(asc_degree, 4),
        absolute_degree=round(asc_longitude, 4),
        house=1,
        retrograde=False,
    )

    # Meio do Céu como PlanetPosition
    mc_sign, mc_degree = longitude_to_sign(mc_longitude)
    midheaven = PlanetPosition(
        planet="Midheaven",
        sign=mc_sign,
        degree=round(mc_degree, 4),
        absolute_degree=round(mc_longitude, 4),
        house=10,
        retrograde=False,
    )

    return house_cusps, ascendant, midheaven, raw_cusps


def calculate_natal_chart(birth_data: BirthData) -> NatalChart:
    """Calcula o mapa astral natal completo para uma pessoa."""
    dt = _parse_datetime(birth_data.birth_datetime_utc)
    jd = _datetime_to_jd(dt)

    # Calcular casas, ascendente e MC
    house_cusps, ascendant, midheaven, raw_cusps = calculate_houses(
        jd, birth_data.latitude, birth_data.longitude, birth_data.house_system
    )

    # Calcular posições planetárias (com casas)
    planets = calculate_planet_positions(jd, raw_cusps)

    # Calcular aspectos natais
    settings = get_settings()
    aspects = calculate_aspects(planets, orbs=settings.orbs)

    return NatalChart(
        name=birth_data.name,
        birth_datetime_utc=birth_data.birth_datetime_utc,
        latitude=birth_data.latitude,
        longitude=birth_data.longitude,
        planets=planets,
        houses=house_cusps,
        ascendant=ascendant,
        midheaven=midheaven,
        aspects=aspects,
    )


def calculate_current_positions() -> list[PlanetPosition]:
    """Calcula as posições planetárias atuais."""
    now = datetime.now(timezone.utc)
    jd = _datetime_to_jd(now)
    return calculate_planet_positions(jd)


def calculate_composite_midpoint(lon1: float, lon2: float) -> float:
    """Calcula o ponto médio entre duas longitudes eclípticas."""
    diff = abs(lon1 - lon2)
    if diff > 180:
        midpoint = (lon1 + lon2) / 2 + 180
    else:
        midpoint = (lon1 + lon2) / 2
    return midpoint % 360
