"""
AstroEngine API - Configurações e Variáveis de Ambiente
"""
import os
from functools import lru_cache


class Settings:
    """Configurações da aplicação carregadas de variáveis de ambiente."""

    # Servidor
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Segurança
    API_KEYS: list[str] = [
        k.strip() for k in os.getenv("API_KEYS", "dev-key-cosmic-suite").split(",")
    ]
    ALLOWED_ORIGINS: list[str] = [
        o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    ]
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))

    # Astrologia - Sistema de Casas Padrão
    DEFAULT_HOUSE_SYSTEM: str = os.getenv("DEFAULT_HOUSE_SYSTEM", "placidus")

    # Astrologia - Orbes padrão (em graus)
    DEFAULT_ORB_CONJUNCTION: float = float(os.getenv("DEFAULT_ORB_CONJUNCTION", "8.0"))
    DEFAULT_ORB_OPPOSITION: float = float(os.getenv("DEFAULT_ORB_OPPOSITION", "8.0"))
    DEFAULT_ORB_TRINE: float = float(os.getenv("DEFAULT_ORB_TRINE", "8.0"))
    DEFAULT_ORB_SQUARE: float = float(os.getenv("DEFAULT_ORB_SQUARE", "7.0"))
    DEFAULT_ORB_SEXTILE: float = float(os.getenv("DEFAULT_ORB_SEXTILE", "6.0"))

    # Repositório (para conformidade AGPL Seção 13)
    SOURCE_REPOSITORY: str = os.getenv(
        "SOURCE_REPOSITORY", "https://github.com/FW2B/astroengine-api"
    )

    @property
    def orbs(self) -> dict[str, float]:
        return {
            "conjunction": self.DEFAULT_ORB_CONJUNCTION,
            "opposition": self.DEFAULT_ORB_OPPOSITION,
            "trine": self.DEFAULT_ORB_TRINE,
            "square": self.DEFAULT_ORB_SQUARE,
            "sextile": self.DEFAULT_ORB_SEXTILE,
        }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
