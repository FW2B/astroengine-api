"""
Testes para os endpoints /synastry, /transits e /composite.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
API_KEY = "dev-key-cosmic-suite"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

PERSON1 = {
    "name": "Maria",
    "birth_datetime_utc": "1990-03-15T14:30:00Z",
    "latitude": -23.5505,
    "longitude": -46.6333,
}

PERSON2 = {
    "name": "João",
    "birth_datetime_utc": "1988-07-20T10:00:00Z",
    "latitude": -22.9068,
    "longitude": -43.1729,
}


def test_synastry_success():
    """Testa se a sinastria retorna mapas de ambas as pessoas e aspectos inter-cartas."""
    response = client.post(
        "/synastry",
        json={"person1": PERSON1, "person2": PERSON2},
        headers=HEADERS,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["person1_chart"]["name"] == "Maria"
    assert data["person2_chart"]["name"] == "João"
    assert len(data["synastry_aspects"]) > 0


def test_transits_success():
    """Testa se os trânsitos são calculados corretamente."""
    response = client.post(
        "/transits",
        json={"birth_data": PERSON1},
        headers=HEADERS,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["natal_chart"]["name"] == "Maria"
    assert len(data["transit_planets"]) == 10
    assert len(data["transit_aspects"]) > 0


def test_transits_with_specific_date():
    """Testa trânsitos para uma data específica."""
    response = client.post(
        "/transits",
        json={
            "birth_data": PERSON1,
            "transit_datetime_utc": "2026-06-21T12:00:00Z",
        },
        headers=HEADERS,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["transit_datetime_utc"] == "2026-06-21T12:00:00Z"


def test_composite_success():
    """Testa se o mapa composto é gerado corretamente."""
    response = client.post(
        "/composite",
        json={"person1": PERSON1, "person2": PERSON2},
        headers=HEADERS,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["person1_name"] == "Maria"
    assert data["person2_name"] == "João"
    assert len(data["planets"]) == 10
    assert len(data["houses"]) == 12
    assert len(data["aspects"]) > 0
