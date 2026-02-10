"""
AstroEngine API - Conversão de coordenadas eclípticas para signos zodiacais
"""

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def longitude_to_sign(longitude: float) -> tuple[str, float]:
    """Converte longitude eclíptica (0-360) para signo e grau dentro do signo."""
    longitude = longitude % 360
    sign_index = int(longitude // 30)
    degree_in_sign = round(longitude % 30, 4)
    return SIGNS[sign_index], degree_in_sign


def determine_house(longitude: float, cusps: list[float]) -> int:
    """Determina em qual casa astrológica uma longitude eclíptica se encontra."""
    longitude = longitude % 360
    for i in range(12):
        cusp_start = cusps[i] % 360
        cusp_end = cusps[(i + 1) % 12] % 360
        if cusp_start < cusp_end:
            if cusp_start <= longitude < cusp_end:
                return i + 1
        else:
            # A casa cruza o ponto 0° Áries
            if longitude >= cusp_start or longitude < cusp_end:
                return i + 1
    return 1  # Fallback
