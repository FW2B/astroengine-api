"""
AstroEngine API - Modelos de Dados para Numerologia (Pydantic v2)
"""
from pydantic import BaseModel, Field
from typing import Optional


class NumerologyInput(BaseModel):
    """Dados de entrada para cálculo de perfil numerológico."""
    full_name: str = Field(
        ...,
        description="Nome completo de nascimento (com ou sem acentos)",
        examples=["Fernando Wanderley"],
    )
    birth_day: int = Field(..., ge=1, le=31, description="Dia de nascimento", examples=[14])
    birth_month: int = Field(..., ge=1, le=12, description="Mês de nascimento", examples=[4])
    birth_year: int = Field(..., ge=1900, le=2100, description="Ano de nascimento", examples=[1976])
    current_year: Optional[int] = Field(
        default=None,
        description="Ano atual para cálculos de período pessoal. Se omitido, usa o ano atual.",
    )
    current_month: Optional[int] = Field(
        default=None, ge=1, le=12,
        description="Mês atual para cálculos de período pessoal.",
    )
    current_day: Optional[int] = Field(
        default=None, ge=1, le=31,
        description="Dia atual para cálculos de período pessoal.",
    )


class NumerologyCompatibilityInput(BaseModel):
    """Dados de entrada para cálculo de compatibilidade numerológica."""
    person1_name: str = Field(..., description="Nome completo da pessoa 1", examples=["Fernando Wanderley"])
    person1_day: int = Field(..., ge=1, le=31, examples=[14])
    person1_month: int = Field(..., ge=1, le=12, examples=[4])
    person1_year: int = Field(..., ge=1900, le=2100, examples=[1976])
    person2_name: str = Field(..., description="Nome completo da pessoa 2", examples=["Maria Santos"])
    person2_day: int = Field(..., ge=1, le=31, examples=[22])
    person2_month: int = Field(..., ge=1, le=12, examples=[7])
    person2_year: int = Field(..., ge=1900, le=2100, examples=[1992])


class LetterDetail(BaseModel):
    letter: str
    value: int


class CoreNumber(BaseModel):
    number: int
    total_before_reduction: Optional[int] = None
    is_master_number: bool = False


class LifePathNumber(CoreNumber):
    reduced_day: int
    reduced_month: int
    reduced_year: int


class ExpressionNumber(CoreNumber):
    letter_values: list[LetterDetail] = []


class SoulUrgeNumber(CoreNumber):
    vowels: list[LetterDetail] = []


class PersonalityNumber(CoreNumber):
    consonants: list[LetterDetail] = []


class BirthdayNumber(BaseModel):
    number: int
    day: int
    is_master_number: bool = False


class MaturityNumber(CoreNumber):
    life_path: int
    expression: int


class PowerNameNumber(CoreNumber):
    soul_urge: int
    personality: int


class ActiveNumber(CoreNumber):
    first_name: str


class LegacyNumber(CoreNumber):
    last_name: str


class KarmicLessons(BaseModel):
    missing_numbers: list[int]
    present_numbers: list[int]
    karmic_lessons_count: int


class PinnacleItem(BaseModel):
    pinnacle: int
    number: int
    is_master_number: bool = False
    age_start: int
    age_end: Optional[int] = None
    year_start: int
    year_end: Optional[int] = None


class ChallengeItem(BaseModel):
    challenge: int
    number: int


class PersonalPeriod(BaseModel):
    number: int
    is_master_number: bool = False


class PersonalYear(PersonalPeriod):
    year: int


class PersonalMonth(BaseModel):
    number: int
    month: int
    personal_year: int


class PersonalDay(BaseModel):
    number: int
    day: int
    personal_month: int


class CoreNumbers(BaseModel):
    life_path: LifePathNumber
    expression: ExpressionNumber
    soul_urge: SoulUrgeNumber
    personality: PersonalityNumber
    birthday: BirthdayNumber
    maturity: MaturityNumber


class NameNumbers(BaseModel):
    power_name: PowerNameNumber
    active: ActiveNumber
    legacy: LegacyNumber


class LifeCycles(BaseModel):
    pinnacles: list[PinnacleItem]
    challenges: list[ChallengeItem]


class CurrentPeriod(BaseModel):
    personal_year: PersonalYear
    personal_month: PersonalMonth
    personal_day: PersonalDay


class NumerologyProfile(BaseModel):
    """Perfil numerológico completo de uma pessoa."""
    name: str
    birth_date: str
    core_numbers: CoreNumbers
    name_numbers: NameNumbers
    karmic_lessons: KarmicLessons
    life_cycles: LifeCycles
    current_period: CurrentPeriod


class CompatibilityDetail(BaseModel):
    score: float
    weight: float


class CompatibilityScores(BaseModel):
    overall_score: float
    life_path: CompatibilityDetail
    expression: CompatibilityDetail
    soul_urge: CompatibilityDetail
    personality: CompatibilityDetail


class PersonSummary(BaseModel):
    name: str
    life_path: int
    expression: int
    soul_urge: int
    personality: int


class NumerologyCompatibility(BaseModel):
    """Resultado da compatibilidade numerológica entre duas pessoas."""
    person1: PersonSummary
    person2: PersonSummary
    compatibility: CompatibilityScores
    profile1: NumerologyProfile
    profile2: NumerologyProfile
