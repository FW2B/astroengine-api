"""
Testes para o endpoint /natal_chart e cálculos astrológicos.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
API_KEY = "dev-key-cosmic-suite"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Dados de teste: 15/03/1990 14:30 UTC, São Paulo
BIRTH_DATA = {
    "name": "Test Person",
    "birth_datetime_utc": "1990-03-15T14:30:00Z",
    "latitude": -23.5505,
    "longitude": -46.6333,
}


def test_natal_chart_success():
    """Testa se o endpoint retorna um mapa natal completo."""
    response = client.post("/natal_chart", json=BIRTH_DATA, headers=HEADERS)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Test Person"
    assert len(data["planets"]) == 10
    assert len(data["houses"]) == 12
    assert data["ascendant"]["planet"] == "Ascendant"
    assert data["midheaven"]["planet"] == "Midheaven"
    assert len(data["aspects"]) > 0


def test_natal_chart_planet_signs():
    """Testa se os signos dos planetas estão corretos para a data de teste."""
    response = client.post("/natal_chart", json=BIRTH_DATA, headers=HEADERS)
    data = response.json()

    planets_by_name = {p["planet"]: p for p in data["planets"]}

    # Sol em Peixes (354.74°)
    assert planets_by_name["Sun"]["sign"] == "Pisces"
    # Lua em Escorpião (220.99°)
    assert planets_by_name["Moon"]["sign"] == "Scorpio"
    # Ascendente em Gêmeos
    assert data["ascendant"]["sign"] == "Gemini"
    # MC em Peixes
    assert data["midheaven"]["sign"] == "Pisces"


def test_natal_chart_houses_placidus():
    """Testa se as 12 casas são calculadas corretamente em Placidus."""
    response = client.post("/natal_chart", json=BIRTH_DATA, headers=HEADERS)
    data = response.json()

    houses = data["houses"]
    assert len(houses) == 12
    for i, house in enumerate(houses):
        assert house["house"] == i + 1
        assert 0 <= house["absolute_degree"] < 360


def test_natal_chart_different_house_systems():
    """Testa se diferentes sistemas de casas são aceitos."""
    for system in ["placidus", "koch", "equal", "whole_sign"]:
        birth = {**BIRTH_DATA, "house_system": system}
        response = client.post("/natal_chart", json=birth, headers=HEADERS)
        assert response.status_code == 200


def test_natal_chart_retrograde_detection():
    """Testa se a detecção de retrogradação funciona."""
    response = client.post("/natal_chart", json=BIRTH_DATA, headers=HEADERS)
    data = response.json()

    planets_by_name = {p["planet"]: p for p in data["planets"]}
    # Plutão estava retrógrado em 15/03/1990
    assert planets_by_name["Pluto"]["retrograde"] is True


def test_natal_chart_no_api_key():
    """Testa se a API rejeita requisições sem chave."""
    response = client.post("/natal_chart", json=BIRTH_DATA)
    assert response.status_code == 401


def test_natal_chart_invalid_api_key():
    """Testa se a API rejeita chaves inválidas."""
    headers = {"X-API-Key": "invalid-key", "Content-Type": "application/json"}
    response = client.post("/natal_chart", json=BIRTH_DATA, headers=headers)
    assert response.status_code == 403


def test_health_check():
    """Testa o endpoint de health check."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_source_endpoint():
    """Testa o endpoint de código-fonte (conformidade AGPL)."""
    response = client.get("/source")
    assert response.status_code == 200
    data = response.json()
    assert "repository_url" in data
    assert "Affero" in data["license"]


def test_planets_now():
    """Testa o endpoint de posições planetárias atuais."""
    response = client.get("/planets/now", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
