"""
AstroEngine API - Cálculo de aspectos entre planetas
"""
from app.models.schemas import Aspect, PlanetPosition
from app.config import get_settings

# Definição dos aspectos e seus ângulos exatos
ASPECT_ANGLES: dict[str, float] = {
    "conjunction": 0.0,
    "sextile": 60.0,
    "square": 90.0,
    "trine": 120.0,
    "opposition": 180.0,
}


def angular_distance(lon1: float, lon2: float) -> float:
    """Calcula a menor distância angular entre duas longitudes eclípticas."""
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def calculate_aspects(
    planets1: list[PlanetPosition],
    planets2: list[PlanetPosition] | None = None,
    orbs: dict[str, float] | None = None,
) -> list[Aspect]:
    """
    Calcula aspectos entre planetas.

    Se planets2 é None, calcula aspectos natais (entre planetas da mesma lista).
    Se planets2 é fornecido, calcula aspectos inter-cartas (sinastria/trânsitos).
    """
    if orbs is None:
        settings = get_settings()
        orbs = settings.orbs

    aspects: list[Aspect] = []
    is_natal = planets2 is None

    if is_natal:
        planets2 = planets1

    for i, p1 in enumerate(planets1):
        start_j = i + 1 if is_natal else 0
        for j in range(start_j, len(planets2)):
            p2 = planets2[j]
            if is_natal and p1.planet == p2.planet:
                continue

            dist = angular_distance(p1.absolute_degree, p2.absolute_degree)

            for aspect_name, exact_angle in ASPECT_ANGLES.items():
                max_orb = orbs.get(aspect_name, 8.0)
                orb_value = abs(dist - exact_angle)

                if orb_value <= max_orb:
                    # Determinar se o aspecto é aplicativo ou separativo
                    # Aplicativo: os planetas estão se aproximando do aspecto exato
                    # Separativo: os planetas estão se afastando
                    applying = _is_applying(
                        p1.absolute_degree, p2.absolute_degree,
                        p1.retrograde, p2.retrograde,
                        exact_angle,
                    )

                    aspects.append(
                        Aspect(
                            planet1=p1.planet,
                            planet2=p2.planet,
                            aspect_type=aspect_name,
                            orb=round(orb_value, 4),
                            applying=applying,
                        )
                    )
                    break  # Um par de planetas só forma um aspecto principal

    return aspects


def _is_applying(
    lon1: float, lon2: float,
    retro1: bool, retro2: bool,
    exact_angle: float,
) -> bool:
    """
    Determina se um aspecto é aplicativo (planetas se aproximando do aspecto exato).

    Lógica simplificada: se o planeta mais rápido (geralmente o primeiro em ordem
    de velocidade) está se movendo em direção ao aspecto exato, é aplicativo.
    Para uma implementação mais precisa, seria necessário comparar velocidades reais.
    """
    diff = (lon1 - lon2) % 360
    if diff > 180:
        diff -= 360

    # Se nenhum está retrógrado, o aspecto é aplicativo se a distância
    # angular é menor que o ângulo exato (os planetas estão convergindo)
    current_dist = angular_distance(lon1, lon2)
    if current_dist < exact_angle:
        return not retro1 and not retro2
    return retro1 or retro2
