"""
AstroEngine API - Endpoints de Numerologia Pitagórica
"""
import logging
from fastapi import APIRouter, Depends

from app.models.numerology_schemas import (
    NumerologyInput,
    NumerologyCompatibilityInput,
    NumerologyProfile,
    NumerologyCompatibility,
)
from app.services.numerology import calculate_full_profile, calculate_compatibility
from app.middleware.auth import verify_api_key

logger = logging.getLogger("astroengine")
router = APIRouter()


@router.post(
    "/numerology/profile",
    response_model=NumerologyProfile,
    summary="Calcula o perfil numerológico completo",
    description=(
        "Calcula o perfil numerológico pitagórico completo de uma pessoa, incluindo "
        "Life Path, Expression, Soul Urge, Personality, Birthday, Maturity, "
        "Power Name, Active, Legacy, Karmic Lessons, Pinnacle Cycles, "
        "Challenge Numbers e Personal Year/Month/Day."
    ),
)
async def numerology_profile(
    data: NumerologyInput,
    api_key: str = Depends(verify_api_key),
) -> dict:
    logger.info(f"Calculando perfil numerológico para: {data.full_name}")

    profile = calculate_full_profile(
        full_name=data.full_name,
        day=data.birth_day,
        month=data.birth_month,
        year=data.birth_year,
        current_year=data.current_year,
        current_month=data.current_month,
        current_day=data.current_day,
    )

    # Adaptar a estrutura de pinnacles e challenges para o schema
    profile["life_cycles"] = {
        "pinnacles": profile["life_cycles"]["pinnacles"]["pinnacles"],
        "challenges": profile["life_cycles"]["challenges"]["challenges"],
    }

    logger.info(f"Perfil numerológico calculado para: {data.full_name}")
    return profile


@router.post(
    "/numerology/compatibility",
    response_model=NumerologyCompatibility,
    summary="Calcula a compatibilidade numerológica entre duas pessoas",
    description=(
        "Calcula a compatibilidade numerológica pitagórica entre duas pessoas, "
        "comparando Life Path, Expression, Soul Urge e Personality. "
        "Inclui os perfis completos de ambas as pessoas."
    ),
)
async def numerology_compatibility(
    data: NumerologyCompatibilityInput,
    api_key: str = Depends(verify_api_key),
) -> dict:
    logger.info(
        f"Calculando compatibilidade numerológica: {data.person1_name} x {data.person2_name}"
    )

    result = calculate_compatibility(
        name1=data.person1_name,
        day1=data.person1_day,
        month1=data.person1_month,
        year1=data.person1_year,
        name2=data.person2_name,
        day2=data.person2_day,
        month2=data.person2_month,
        year2=data.person2_year,
    )

    # Adaptar a estrutura de pinnacles e challenges para ambos os perfis
    for profile_key in ["profile1", "profile2"]:
        profile = result[profile_key]
        profile["life_cycles"] = {
            "pinnacles": profile["life_cycles"]["pinnacles"]["pinnacles"],
            "challenges": profile["life_cycles"]["challenges"]["challenges"],
        }

    logger.info(
        f"Compatibilidade numerológica calculada: {data.person1_name} x {data.person2_name}"
    )
    return result
