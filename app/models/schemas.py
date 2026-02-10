"""
AstroEngine API - Modelos de Dados (Pydantic v2)
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class HouseSystem(str, Enum):
    PLACIDUS = "placidus"
    KOCH = "koch"
    PORPHYRIUS = "porphyrius"
    REGIOMONTANUS = "regiomontanus"
    CAMPANUS = "campanus"
    EQUAL = "equal"
    WHOLE_SIGN = "whole_sign"


# Mapeamento de HouseSystem para código Swiss Ephemeris
HOUSE_SYSTEM_CODES: dict[str, bytes] = {
    "placidus": b"P",
    "koch": b"K",
    "porphyrius": b"O",
    "regiomontanus": b"R",
    "campanus": b"C",
    "equal": b"E",
    "whole_sign": b"W",
}


class BirthData(BaseModel):
    name: str = Field(..., description="Nome da pessoa", examples=["Maria Silva"])
    birth_datetime_utc: str = Field(
        ...,
        description="Data e hora de nascimento em UTC, formato ISO 8601: YYYY-MM-DDTHH:MM:SSZ",
        examples=["1990-03-15T14:30:00Z"],
    )
    latitude: float = Field(
        ..., ge=-90, le=90, description="Latitude do local de nascimento", examples=[-23.5505]
    )
    longitude: float = Field(
        ..., ge=-180, le=180, description="Longitude do local de nascimento", examples=[-46.6333]
    )
    house_system: HouseSystem = Field(
        default=HouseSystem.PLACIDUS, description="Sistema de casas astrológicas"
    )


class TransitInput(BaseModel):
    birth_data: BirthData
    transit_datetime_utc: Optional[str] = Field(
        default=None,
        description="Data/hora do trânsito em UTC (ISO 8601). Se omitido, usa a data/hora atual.",
        examples=["2026-02-10T12:00:00Z"],
    )


class PlanetPosition(BaseModel):
    planet: str = Field(
        ...,
        description="Nome do corpo celeste (ex: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto)",
    )
    sign: str = Field(..., description="Signo zodiacal (ex: Aries, Taurus, Gemini...)")
    degree: float = Field(..., description="Grau dentro do signo (0-30)")
    absolute_degree: float = Field(..., description="Grau absoluto na eclíptica (0-360)")
    house: int = Field(default=0, ge=0, le=12, description="Casa astrológica (1-12, 0 se não aplicável)")
    retrograde: bool = Field(default=False, description="Se o planeta está retrógrado")


class HouseCusp(BaseModel):
    house: int = Field(..., ge=1, le=12)
    sign: str
    degree: float
    absolute_degree: float


class Aspect(BaseModel):
    planet1: str
    planet2: str
    aspect_type: str = Field(
        ...,
        description="Tipo do aspecto: conjunction, opposition, trine, square, sextile",
    )
    orb: float = Field(..., description="Orbe do aspecto em graus")
    applying: bool = Field(
        ..., description="Se o aspecto é aplicativo (true) ou separativo (false)"
    )


class NatalChart(BaseModel):
    name: str
    birth_datetime_utc: str
    latitude: float
    longitude: float
    planets: list[PlanetPosition]
    houses: list[HouseCusp]
    ascendant: PlanetPosition
    midheaven: PlanetPosition
    aspects: list[Aspect] = Field(
        default_factory=list, description="Aspectos entre planetas do mapa natal"
    )


class SynastryInput(BaseModel):
    person1: BirthData
    person2: BirthData


class SynastryReport(BaseModel):
    person1_chart: NatalChart
    person2_chart: NatalChart
    synastry_aspects: list[Aspect] = Field(
        ...,
        description="Aspectos inter-cartas entre os planetas das duas pessoas",
    )


class TransitReport(BaseModel):
    natal_chart: NatalChart
    transit_datetime_utc: str
    transit_planets: list[PlanetPosition]
    transit_aspects: list[Aspect] = Field(
        ...,
        description="Aspectos entre planetas em trânsito e planetas natais",
    )


class CompositeChart(BaseModel):
    person1_name: str
    person2_name: str
    planets: list[PlanetPosition] = Field(
        ..., description="Pontos médios dos planetas das duas pessoas"
    )
    houses: list[HouseCusp]
    aspects: list[Aspect]
