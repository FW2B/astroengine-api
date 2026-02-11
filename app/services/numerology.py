"""
AstroEngine API - Motor de Numerologia Pitagórica
Implementação completa seguindo as regras tradicionais de Hans Decoz
(worldnumerology.com) e fontes de referência da numerologia pitagórica.

Licenciado sob GNU Affero General Public License v3.0 (AGPL-3.0).
Copyright (C) 2026 FW2B - Frameworks to Business
"""
import unicodedata
import re
from typing import Optional

# ============================================================================
# CONSTANTES
# ============================================================================

# Tabela Pitagórica padrão: A=1, B=2, ..., I=9, J=1, ..., R=9, S=1, ..., Z=8
PYTHAGOREAN_TABLE: dict[str, int] = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9,
    "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "O": 6, "P": 7, "Q": 8, "R": 9,
    "S": 1, "T": 2, "U": 3, "V": 4, "W": 5, "X": 6, "Y": 7, "Z": 8,
}

# Vogais padrão (Y é tratado contextualmente)
STANDARD_VOWELS = set("AEIOU")

# Números mestres reconhecidos
MASTER_NUMBERS = {11, 22, 33}


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def normalize_name(name: str) -> str:
    """
    Normaliza um nome para cálculo numerológico:
    - Remove acentos (é→e, ã→a, ç→c, ñ→n, etc.)
    - Converte para maiúsculas
    - Remove caracteres não-alfabéticos (exceto espaços)
    """
    # Decomposição Unicode para separar acentos
    nfkd = unicodedata.normalize("NFKD", name)
    # Remove combining characters (acentos)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Converte para maiúsculas
    upper = ascii_text.upper()
    # Mantém apenas letras e espaços
    clean = re.sub(r"[^A-Z ]", "", upper)
    # Remove espaços extras
    return re.sub(r"\s+", " ", clean).strip()


def _is_y_vowel_in_word(word: str, pos: int) -> bool:
    """
    Determina se a letra Y na posição `pos` dentro de uma PALAVRA INDIVIDUAL
    é vogal ou consoante, seguindo as regras de Hans Decoz (worldnumerology.com):

    1. Se Y é a primeira letra e seguido de consoante → VOGAL (Yvonne, Ylsa)
    2. Se Y é a última letra e após consoante → VOGAL (Barry, Tommy)
    3. Se Y é a primeira letra e seguido de vogal → CONSOANTE (Yolanda)
    4. Se Y é a última letra e após vogal → CONSOANTE (Mulrooney)
    5. Se Y está entre duas consoantes → VOGAL (Kyle, Tyson)
    6. Se Y está entre duas vogais → CONSOANTE (Eyarta)
    7. Se Y está entre consoante e vogal → CONSOANTE (padrão)
    8. Se Y está entre vogal e consoante → CONSOANTE (padrão)
    """
    if word[pos] != "Y":
        return False

    def is_std_vowel(c: str) -> bool:
        return c in STANDARD_VOWELS

    def is_consonant(c: str) -> bool:
        return c.isalpha() and c not in STANDARD_VOWELS and c != "Y"

    # Regra: Y no início da palavra
    if pos == 0:
        if pos + 1 < len(word):
            nxt = word[pos + 1]
            if is_consonant(nxt):
                return True   # Yvonne, Ylsa
            if is_std_vowel(nxt):
                return False  # Yolanda
        return True  # Y isolado

    # Regra: Y no final da palavra
    if pos == len(word) - 1:
        prev = word[pos - 1]
        if is_consonant(prev):
            return True   # Barry, Tommy, Wanderley
        if is_std_vowel(prev):
            return False  # Mulrooney
        return True  # fallback

    # Regra: Y no meio da palavra
    prev = word[pos - 1]
    nxt = word[pos + 1]

    if is_consonant(prev) and is_consonant(nxt):
        return True   # Kyle, Tyson
    if is_std_vowel(prev) and is_std_vowel(nxt):
        return False  # Eyarta
    if is_consonant(prev) and is_std_vowel(nxt):
        return False  # padrão
    if is_std_vowel(prev) and is_consonant(nxt):
        return False  # padrão

    return True  # fallback


def is_y_vowel(name: str, position: int) -> bool:
    """
    Wrapper que identifica a PALAVRA onde o Y está e delega
    para `_is_y_vowel_in_word` para análise contextual correta.
    """
    if name[position] != "Y":
        return False

    # Encontrar a palavra que contém a posição
    words = name.split()
    char_idx = 0
    for word in words:
        word_start = char_idx
        word_end = char_idx + len(word)
        if word_start <= position < word_end:
            pos_in_word = position - word_start
            return _is_y_vowel_in_word(word, pos_in_word)
        char_idx = word_end + 1  # +1 para o espaço

    return True  # fallback


def classify_letters(name: str) -> tuple[list[tuple[str, int]], list[tuple[str, int]]]:
    """
    Classifica as letras de um nome em vogais e consoantes,
    tratando Y contextualmente.

    Retorna: (vogais, consoantes) como listas de tuplas (letra, valor).
    """
    normalized = normalize_name(name)
    vowels: list[tuple[str, int]] = []
    consonants: list[tuple[str, int]] = []

    for i, char in enumerate(normalized):
        if char == " ":
            continue

        value = PYTHAGOREAN_TABLE.get(char, 0)
        if value == 0:
            continue

        if char in STANDARD_VOWELS:
            vowels.append((char, value))
        elif char == "Y":
            if is_y_vowel(normalized, i):
                vowels.append((char, value))
            else:
                consonants.append((char, value))
        else:
            consonants.append((char, value))

    return vowels, consonants


def reduce_to_single_digit(number: int, keep_master: bool = True) -> int:
    """
    Reduz um número a um único dígito, preservando números mestres
    (11, 22, 33) se keep_master=True.
    """
    while number > 9:
        if keep_master and number in MASTER_NUMBERS:
            return number
        number = sum(int(d) for d in str(number))
    return number


def reduce_date_part(number: int) -> int:
    """
    Reduz uma parte da data (dia, mês ou ano) a um dígito ou número mestre.
    Usado no cálculo do Life Path pelo método de redução por partes.
    """
    return reduce_to_single_digit(number, keep_master=True)


def sum_letter_values(letters: list[tuple[str, int]]) -> int:
    """Soma os valores numéricos de uma lista de letras."""
    return sum(value for _, value in letters)


# ============================================================================
# CÁLCULOS NUMEROLÓGICOS PRINCIPAIS
# ============================================================================

def calculate_life_path(day: int, month: int, year: int) -> dict:
    """
    Calcula o Número do Caminho de Vida (Life Path Number).

    Método: Redução por partes (método correto de Hans Decoz).
    Cada componente (dia, mês, ano) é reduzido separadamente antes da soma final.

    Exemplo: 14/04/1976
    - Dia: 14 → 1+4 = 5
    - Mês: 04 → 4
    - Ano: 1976 → 1+9+7+6 = 23 → 2+3 = 5
    - Soma: 5 + 4 + 5 = 14 → 1+4 = 5
    """
    reduced_day = reduce_date_part(day)
    reduced_month = reduce_date_part(month)
    reduced_year = reduce_date_part(year)

    total = reduced_day + reduced_month + reduced_year
    life_path = reduce_to_single_digit(total, keep_master=True)

    return {
        "number": life_path,
        "reduced_day": reduced_day,
        "reduced_month": reduced_month,
        "reduced_year": reduced_year,
        "total_before_reduction": total,
        "is_master_number": life_path in MASTER_NUMBERS,
    }


def calculate_expression(full_name: str) -> dict:
    """
    Calcula o Número de Expressão / Destino (Expression / Destiny Number).
    Soma de TODAS as letras do nome completo de nascimento.
    """
    normalized = normalize_name(full_name)
    total = 0
    letter_values = []

    for char in normalized:
        if char == " ":
            continue
        value = PYTHAGOREAN_TABLE.get(char, 0)
        if value > 0:
            letter_values.append({"letter": char, "value": value})
            total += value

    expression = reduce_to_single_digit(total, keep_master=True)

    return {
        "number": expression,
        "total_before_reduction": total,
        "is_master_number": expression in MASTER_NUMBERS,
        "letter_values": letter_values,
    }


def calculate_soul_urge(full_name: str) -> dict:
    """
    Calcula o Número da Motivação / Desejo da Alma (Soul Urge / Heart's Desire).
    Soma apenas das VOGAIS do nome completo.
    """
    vowels, _ = classify_letters(full_name)
    total = sum_letter_values(vowels)
    soul_urge = reduce_to_single_digit(total, keep_master=True)

    return {
        "number": soul_urge,
        "total_before_reduction": total,
        "is_master_number": soul_urge in MASTER_NUMBERS,
        "vowels": [{"letter": l, "value": v} for l, v in vowels],
    }


def calculate_personality(full_name: str) -> dict:
    """
    Calcula o Número da Personalidade (Personality Number).
    Soma apenas das CONSOANTES do nome completo.
    """
    _, consonants = classify_letters(full_name)
    total = sum_letter_values(consonants)
    personality = reduce_to_single_digit(total, keep_master=True)

    return {
        "number": personality,
        "total_before_reduction": total,
        "is_master_number": personality in MASTER_NUMBERS,
        "consonants": [{"letter": l, "value": v} for l, v in consonants],
    }


def calculate_birthday_number(day: int) -> dict:
    """
    Calcula o Número do Aniversário (Birthday Number).
    Redução do dia de nascimento.
    """
    birthday = reduce_to_single_digit(day, keep_master=True)

    return {
        "number": birthday,
        "day": day,
        "is_master_number": birthday in MASTER_NUMBERS,
    }


def calculate_maturity_number(life_path: int, expression: int) -> dict:
    """
    Calcula o Número de Maturidade (Maturity Number).
    Soma do Life Path + Expression.
    """
    total = life_path + expression
    maturity = reduce_to_single_digit(total, keep_master=True)

    return {
        "number": maturity,
        "life_path": life_path,
        "expression": expression,
        "total_before_reduction": total,
        "is_master_number": maturity in MASTER_NUMBERS,
    }


def calculate_power_name_number(soul_urge: int, personality: int) -> dict:
    """
    Calcula o Número do Nome de Poder (Power Name Number).
    Soma do Soul Urge + Personality.
    """
    total = soul_urge + personality
    power_name = reduce_to_single_digit(total, keep_master=True)

    return {
        "number": power_name,
        "soul_urge": soul_urge,
        "personality": personality,
        "total_before_reduction": total,
        "is_master_number": power_name in MASTER_NUMBERS,
    }


def calculate_active_number(first_name: str) -> dict:
    """
    Calcula o Número Ativo (Active Number).
    Soma de todas as letras do primeiro nome.
    """
    normalized = normalize_name(first_name)
    first = normalized.split()[0] if normalized.split() else normalized
    total = sum(PYTHAGOREAN_TABLE.get(c, 0) for c in first if c != " ")
    active = reduce_to_single_digit(total, keep_master=True)

    return {
        "number": active,
        "first_name": first,
        "total_before_reduction": total,
        "is_master_number": active in MASTER_NUMBERS,
    }


def calculate_legacy_number(last_name: str) -> dict:
    """
    Calcula o Número Hereditário / Legado (Legacy / Hereditary Number).
    Soma de todas as letras do sobrenome.
    """
    normalized = normalize_name(last_name)
    parts = normalized.split()
    last = parts[-1] if parts else normalized
    total = sum(PYTHAGOREAN_TABLE.get(c, 0) for c in last if c != " ")
    legacy = reduce_to_single_digit(total, keep_master=True)

    return {
        "number": legacy,
        "last_name": last,
        "total_before_reduction": total,
        "is_master_number": legacy in MASTER_NUMBERS,
    }


def calculate_missing_numbers(full_name: str) -> dict:
    """
    Calcula os Números Ausentes / Lições Cármicas (Missing Numbers / Karmic Lessons).
    Números de 1 a 9 que não aparecem em nenhuma letra do nome.
    """
    normalized = normalize_name(full_name)
    present_values = set()

    for char in normalized:
        if char == " ":
            continue
        value = PYTHAGOREAN_TABLE.get(char, 0)
        if value > 0:
            present_values.add(value)

    all_numbers = set(range(1, 10))
    missing = sorted(all_numbers - present_values)

    return {
        "missing_numbers": missing,
        "present_numbers": sorted(present_values),
        "karmic_lessons_count": len(missing),
    }


def calculate_pinnacle_cycles(day: int, month: int, year: int) -> dict:
    """
    Calcula os 4 Ciclos de Pináculos (Pinnacle Cycles).

    - 1° Pináculo: Mês + Dia (duração: 36 - Life Path)
    - 2° Pináculo: Dia + Ano (duração: 9 anos)
    - 3° Pináculo: 1° + 2° Pináculo (duração: 9 anos)
    - 4° Pináculo: Mês + Ano (duração: até o fim da vida)
    """
    rd = reduce_date_part(day)
    rm = reduce_date_part(month)
    ry = reduce_date_part(year)

    life_path_data = calculate_life_path(day, month, year)
    lp = life_path_data["number"]
    # Se for número mestre, usar o valor reduzido para o cálculo de idade
    lp_single = reduce_to_single_digit(lp, keep_master=False)

    first_pinnacle_end = 36 - lp_single

    p1 = reduce_to_single_digit(rm + rd, keep_master=True)
    p2 = reduce_to_single_digit(rd + ry, keep_master=True)
    p3 = reduce_to_single_digit(p1 + p2, keep_master=True)
    p4 = reduce_to_single_digit(rm + ry, keep_master=True)

    birth_year = year

    return {
        "pinnacles": [
            {
                "pinnacle": 1,
                "number": p1,
                "is_master_number": p1 in MASTER_NUMBERS,
                "age_start": 0,
                "age_end": first_pinnacle_end,
                "year_start": birth_year,
                "year_end": birth_year + first_pinnacle_end,
            },
            {
                "pinnacle": 2,
                "number": p2,
                "is_master_number": p2 in MASTER_NUMBERS,
                "age_start": first_pinnacle_end + 1,
                "age_end": first_pinnacle_end + 9,
                "year_start": birth_year + first_pinnacle_end + 1,
                "year_end": birth_year + first_pinnacle_end + 9,
            },
            {
                "pinnacle": 3,
                "number": p3,
                "is_master_number": p3 in MASTER_NUMBERS,
                "age_start": first_pinnacle_end + 10,
                "age_end": first_pinnacle_end + 18,
                "year_start": birth_year + first_pinnacle_end + 10,
                "year_end": birth_year + first_pinnacle_end + 18,
            },
            {
                "pinnacle": 4,
                "number": p4,
                "is_master_number": p4 in MASTER_NUMBERS,
                "age_start": first_pinnacle_end + 19,
                "age_end": None,  # até o fim da vida
                "year_start": birth_year + first_pinnacle_end + 19,
                "year_end": None,
            },
        ],
    }


def calculate_challenge_numbers(day: int, month: int, year: int) -> dict:
    """
    Calcula os 4 Números de Desafio (Challenge Numbers).

    - 1° Desafio: |Mês - Dia|
    - 2° Desafio: |Dia - Ano|
    - 3° Desafio: |1° - 2°|
    - 4° Desafio: |Mês - Ano|
    """
    rd = reduce_date_part(day)
    rm = reduce_date_part(month)
    ry = reduce_date_part(year)

    c1 = reduce_to_single_digit(abs(rm - rd), keep_master=False)
    c2 = reduce_to_single_digit(abs(rd - ry), keep_master=False)
    c3 = reduce_to_single_digit(abs(c1 - c2), keep_master=False)
    c4 = reduce_to_single_digit(abs(rm - ry), keep_master=False)

    return {
        "challenges": [
            {"challenge": 1, "number": c1},
            {"challenge": 2, "number": c2},
            {"challenge": 3, "number": c3},
            {"challenge": 4, "number": c4},
        ],
    }


def calculate_personal_year(day: int, month: int, current_year: int) -> dict:
    """
    Calcula o Ano Pessoal (Personal Year).
    Soma do dia de nascimento + mês de nascimento + ano atual.
    """
    rd = reduce_date_part(day)
    rm = reduce_date_part(month)
    ry = reduce_date_part(current_year)

    total = rd + rm + ry
    personal_year = reduce_to_single_digit(total, keep_master=True)

    return {
        "number": personal_year,
        "year": current_year,
        "is_master_number": personal_year in MASTER_NUMBERS,
    }


def calculate_personal_month(personal_year: int, current_month: int) -> dict:
    """
    Calcula o Mês Pessoal (Personal Month).
    Soma do Ano Pessoal + mês atual.
    """
    total = personal_year + current_month
    personal_month = reduce_to_single_digit(total, keep_master=False)

    return {
        "number": personal_month,
        "month": current_month,
        "personal_year": personal_year,
    }


def calculate_personal_day(personal_month: int, current_day: int) -> dict:
    """
    Calcula o Dia Pessoal (Personal Day).
    Soma do Mês Pessoal + dia atual.
    """
    total = personal_month + current_day
    personal_day = reduce_to_single_digit(total, keep_master=False)

    return {
        "number": personal_day,
        "day": current_day,
        "personal_month": personal_month,
    }


# ============================================================================
# PERFIL NUMEROLÓGICO COMPLETO
# ============================================================================

def calculate_full_profile(
    full_name: str,
    day: int,
    month: int,
    year: int,
    current_year: Optional[int] = None,
    current_month: Optional[int] = None,
    current_day: Optional[int] = None,
) -> dict:
    """
    Calcula o perfil numerológico completo de uma pessoa.
    """
    from datetime import datetime

    now = datetime.utcnow()
    if current_year is None:
        current_year = now.year
    if current_month is None:
        current_month = now.month
    if current_day is None:
        current_day = now.day

    life_path = calculate_life_path(day, month, year)
    expression = calculate_expression(full_name)
    soul_urge = calculate_soul_urge(full_name)
    personality = calculate_personality(full_name)
    birthday = calculate_birthday_number(day)
    maturity = calculate_maturity_number(life_path["number"], expression["number"])
    power_name = calculate_power_name_number(soul_urge["number"], personality["number"])
    active = calculate_active_number(full_name)
    legacy = calculate_legacy_number(full_name)
    missing = calculate_missing_numbers(full_name)
    pinnacles = calculate_pinnacle_cycles(day, month, year)
    challenges = calculate_challenge_numbers(day, month, year)
    personal_year = calculate_personal_year(day, month, current_year)
    personal_month = calculate_personal_month(personal_year["number"], current_month)
    personal_day = calculate_personal_day(personal_month["number"], current_day)

    return {
        "name": full_name,
        "birth_date": f"{year:04d}-{month:02d}-{day:02d}",
        "core_numbers": {
            "life_path": life_path,
            "expression": expression,
            "soul_urge": soul_urge,
            "personality": personality,
            "birthday": birthday,
            "maturity": maturity,
        },
        "name_numbers": {
            "power_name": power_name,
            "active": active,
            "legacy": legacy,
        },
        "karmic_lessons": missing,
        "life_cycles": {
            "pinnacles": pinnacles,
            "challenges": challenges,
        },
        "current_period": {
            "personal_year": personal_year,
            "personal_month": personal_month,
            "personal_day": personal_day,
        },
    }


# ============================================================================
# COMPATIBILIDADE NUMEROLÓGICA
# ============================================================================

def calculate_compatibility(
    name1: str, day1: int, month1: int, year1: int,
    name2: str, day2: int, month2: int, year2: int,
) -> dict:
    """
    Calcula a compatibilidade numerológica entre duas pessoas.
    Compara Life Path, Expression, Soul Urge e Personality.
    """
    profile1 = calculate_full_profile(name1, day1, month1, year1)
    profile2 = calculate_full_profile(name2, day2, month2, year2)

    # Tabela de compatibilidade baseada em numerologia tradicional
    # Cada par de números tem uma pontuação de 0 a 100
    compatibility_matrix = _build_compatibility_matrix()

    lp1 = profile1["core_numbers"]["life_path"]["number"]
    lp2 = profile2["core_numbers"]["life_path"]["number"]
    ex1 = profile1["core_numbers"]["expression"]["number"]
    ex2 = profile2["core_numbers"]["expression"]["number"]
    su1 = profile1["core_numbers"]["soul_urge"]["number"]
    su2 = profile2["core_numbers"]["soul_urge"]["number"]
    pe1 = profile1["core_numbers"]["personality"]["number"]
    pe2 = profile2["core_numbers"]["personality"]["number"]

    lp_compat = _get_compatibility_score(lp1, lp2, compatibility_matrix)
    ex_compat = _get_compatibility_score(ex1, ex2, compatibility_matrix)
    su_compat = _get_compatibility_score(su1, su2, compatibility_matrix)
    pe_compat = _get_compatibility_score(pe1, pe2, compatibility_matrix)

    # Pesos: Life Path (40%), Soul Urge (25%), Expression (20%), Personality (15%)
    overall = round(
        lp_compat * 0.40 + su_compat * 0.25 + ex_compat * 0.20 + pe_compat * 0.15,
        1,
    )

    return {
        "person1": {
            "name": name1,
            "life_path": lp1,
            "expression": ex1,
            "soul_urge": su1,
            "personality": pe1,
        },
        "person2": {
            "name": name2,
            "life_path": lp2,
            "expression": ex2,
            "soul_urge": su2,
            "personality": pe2,
        },
        "compatibility": {
            "overall_score": overall,
            "life_path": {"score": lp_compat, "weight": 0.40},
            "expression": {"score": ex_compat, "weight": 0.20},
            "soul_urge": {"score": su_compat, "weight": 0.25},
            "personality": {"score": pe_compat, "weight": 0.15},
        },
        "profile1": profile1,
        "profile2": profile2,
    }


def _get_compatibility_score(n1: int, n2: int, matrix: dict) -> float:
    """Obtém a pontuação de compatibilidade entre dois números."""
    # Para números mestres, usar tanto o valor mestre quanto o reduzido
    key = (min(n1, n2), max(n1, n2))
    if key in matrix:
        return matrix[key]

    # Se um dos números é mestre, tentar com o valor reduzido
    r1 = reduce_to_single_digit(n1, keep_master=False)
    r2 = reduce_to_single_digit(n2, keep_master=False)
    key_reduced = (min(r1, r2), max(r1, r2))
    return matrix.get(key_reduced, 50.0)


def _build_compatibility_matrix() -> dict[tuple[int, int], float]:
    """
    Constrói a matriz de compatibilidade numerológica.
    Baseada em fontes tradicionais de numerologia pitagórica.
    Escala: 0 (incompatível) a 100 (altamente compatível).
    """
    m: dict[tuple[int, int], float] = {}

    # Definições de compatibilidade (min, max) → score
    data = {
        # Número 1
        (1, 1): 70, (1, 2): 55, (1, 3): 85, (1, 4): 50, (1, 5): 90,
        (1, 6): 60, (1, 7): 65, (1, 8): 55, (1, 9): 80,
        # Número 2
        (2, 2): 75, (2, 3): 80, (2, 4): 85, (2, 5): 45, (2, 6): 90,
        (2, 7): 60, (2, 8): 70, (2, 9): 65,
        # Número 3
        (3, 3): 80, (3, 4): 40, (3, 5): 90, (3, 6): 85, (3, 7): 55,
        (3, 8): 50, (3, 9): 95,
        # Número 4
        (4, 4): 75, (4, 5): 35, (4, 6): 80, (4, 7): 70, (4, 8): 90,
        (4, 9): 40,
        # Número 5
        (5, 5): 70, (5, 6): 45, (5, 7): 80, (5, 8): 55, (5, 9): 75,
        # Número 6
        (6, 6): 85, (6, 7): 40, (6, 8): 60, (6, 9): 90,
        # Número 7
        (7, 7): 80, (7, 8): 45, (7, 9): 55,
        # Número 8
        (8, 8): 75, (8, 9): 50,
        # Número 9
        (9, 9): 70,
    }

    for key, score in data.items():
        m[key] = float(score)

    return m
