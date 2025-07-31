# app/api/zodiac_logic.py
"""
Contiene la lógica de negocio pura para los cálculos de compatibilidad.
Esto permite que los cálculos se prueben y reutilicen independientemente de la API.
"""
from datetime import date
from typing import Dict, List, Tuple

def get_zodiac_sign_details(birth_date_obj: date) -> Tuple[int, str]:
    """Calcula el índice (0-11) y el elemento de un signo zodiacal."""
    month = birth_date_obj.month
    day = birth_date_obj.day
    
    if (month == 3 and day >= 21) or (month == 4 and day <= 19): return (0, "Fuego")    # Aries
    if (month == 4 and day >= 20) or (month == 5 and day <= 20): return (1, "Tierra")  # Tauro
    if (month == 5 and day >= 21) or (month == 6 and day <= 20): return (2, "Aire")     # Géminis
    if (month == 6 and day >= 21) or (month == 7 and day <= 22): return (3, "Agua")    # Cáncer
    if (month == 7 and day >= 23) or (month == 8 and day <= 22): return (4, "Fuego")    # Leo
    if (month == 8 and day >= 23) or (month == 9 and day <= 22): return (5, "Tierra")  # Virgo
    if (month == 9 and day >= 23) or (month == 10 and day <= 22): return (6, "Aire")     # Libra
    if (month == 10 and day >= 23) or (month == 11 and day <= 21): return (7, "Agua")    # Escorpio
    if (month == 11 and day >= 22) or (month == 12 and day <= 21): return (8, "Fuego")    # Sagitario
    if (month == 12 and day >= 22) or (month == 1 and day <= 19): return (9, "Tierra")  # Capricornio
    if (month == 1 and day >= 20) or (month == 2 and day <= 18): return (10, "Aire")    # Acuario
    return (11, "Agua") # Piscis

def calculate_compatibility_scores(
    date1: date, date2: date, is_premium: bool
) -> List[Dict[str, any]]:
    """
    Calcula las puntuaciones de compatibilidad basadas en las fechas de nacimiento.
    """
    sign1_index, elem1 = get_zodiac_sign_details(date1)
    sign2_index, elem2 = get_zodiac_sign_details(date2)

    # Calcula la distancia en la rueda zodiacal (0 a 6)
    diff = abs(sign1_index - sign2_index)
    distance = diff if diff <= 6 else 12 - diff

    # Puntuaciones base según la distancia
    scores = {
        "Conexión auténtica": max(0.0, 100.0 - distance * 12), # Amistad
        "Relación estable": max(0.0, 100.0 - distance * 15),   # Largo plazo
        "Relación abierta": max(0.0, 100.0 - distance * 10),    # Casual
    }

    # Bono premium si comparten elemento
    if is_premium and elem1 == elem2:
        for key in scores:
            scores[key] = min(100.0, scores[key] + 15.0)

    # Genera la descripción final
    breakdowns = []
    for category, score in scores.items():
        if score >= 85: desc = "Muy alta compatibilidad"
        elif score >= 70: desc = "Alta compatibilidad"
        elif score >= 50: desc = "Buena compatibilidad"
        elif score >= 30: desc = "Compatibilidad moderada"
        else: desc = "Baja compatibilidad"
        breakdowns.append({"category": category, "score": score, "description": desc})

    return breakdowns