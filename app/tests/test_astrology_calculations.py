import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.astrology_service import calculate_natal_chart

@pytest.mark.asyncio
async def test_astrology_calculation_matches_astro_com():
    """
    Verifica que el cálculo astrológico de Synastr coincida con astro.com
    para el nacimiento: 27/11/1991, 2:40 AM, Bogotá, Colombia.
    """

    # Datos de referencia (astro.com)
    expected_positions = {
        "Sun": ("Sagittarius", 4.55),
        "Moon": ("Leo", 17.35),
        "Mercury": ("Sagittarius", 24.03),
        "Venus": ("Libra", 19.71),
        "Mars": ("Scorpio", 28.74),
        "Jupiter": ("Virgo", 12.88),
        "Saturn": ("Aquarius", 2.46),
        "Uranus": ("Capricorn", 11.73),
        "Neptune": ("Capricorn", 15.00),
        "Pluto": ("Scorpio", 20.86),
        "Chiron": ("Leo", 9.58),
        "North Node": ("Capricorn", 10.36),
        "Lilith": ("Sagittarius", 24.75),
    }

    expected_houses = {
        "Ascendant": ("Libra", 17.45),
        "House 2": ("Scorpio", 18.14),
        "House 3": ("Sagittarius", 17.11),
        "Imum Coeli": ("Capricorn", 15.34),
        "House 5": ("Aquarius", 14.64),
        "House 6": ("Pisces", 15.82),
        "Descendant": ("Aries", 17.45),
        "House 8": ("Taurus", 18.14),
        "House 9": ("Gemini", 17.11),
        "Midheaven": ("Cancer", 15.34),
        "House 11": ("Leo", 14.64),
        "House 12": ("Virgo", 15.82),
    }

    # Fecha, hora y lugar de nacimiento
    birth_datetime = datetime(1991, 11, 27, 2, 40, tzinfo=ZoneInfo("America/Bogota"))
    birth_place = "Bogotá, Colombia"

    # Ejecutar cálculo de Synastr
    natal_chart, latitude, longitude, timezone = await calculate_natal_chart(
        birth_datetime, birth_place
    )

    # Verificar posiciones planetarias
    for pos in natal_chart.positions:
        exp_sign, exp_deg = expected_positions[pos.name]
        assert pos.sign == exp_sign, f"{pos.name}: esperado {exp_sign}, obtenido {pos.sign}"
        assert abs(pos.degrees - exp_deg) < 0.1, f"{pos.name}: esperado {exp_deg}°, obtenido {pos.degrees:.2f}°"

    # Verificar casas
    for house in natal_chart.houses:
        exp_sign, exp_deg = expected_houses[house.name]
        assert house.sign == exp_sign, f"{house.name}: esperado {exp_sign}, obtenido {house.sign}"
        assert abs(house.degrees - exp_deg) < 0.1, f"{house.name}: esperado {exp_deg}°, obtenido {house.degrees:.2f}°"

    # Verificar latitud, longitud y zona horaria
    assert round(latitude, 3) == 4.653, f"Latitud incorrecta: {latitude}"
    assert round(longitude, 3) == -74.084, f"Longitud incorrecta: {longitude}"
    assert timezone == "America/Bogota", f"Zona horaria incorrecta: {timezone}"
