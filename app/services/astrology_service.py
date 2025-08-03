# app/services/astrology_service.py
import swisseph as swe
from datetime import datetime
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo

from ..models.user import NatalChart, AstrologicalPosition

# Mapping of Swiss Ephemeris planet indexes
PLANET_MAPPING = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
    "Chiron": swe.CHIRON,
    "North Node": swe.TRUE_NODE,
    "Lilith": swe.OSCU_APOG,  # Lilith (osculating lunar apogee)
}

# Zodiac signs and their icons
ZODIAC_SIGNS = [
    ("Aries", "♈️"), ("Taurus", "♉️"), ("Gemini", "♊️"), ("Cancer", "♋️"),
    ("Leo", "♌️"), ("Virgo", "♍️"), ("Libra", "♎️"), ("Scorpio", "♏️"),
    ("Sagittarius", "♐️"), ("Capricorn", "♑️"), ("Aquarius", "♒️"), ("Pisces", "♓️")
]

def get_zodiac_sign(longitude):
    """Returns the sign name and icon from a celestial longitude."""
    index = int(longitude / 30)
    return ZODIAC_SIGNS[index]

def get_zodiac_sign_index(sign_name):
    """Returns the numerical index of a sign (0 for Aries, 1 for Taurus, etc.)."""
    return next(
        (
            i
            for i, sign_tuple in enumerate(ZODIAC_SIGNS)
            if sign_tuple[0] == sign_name
        ),
        -1,
    )

async def calculate_natal_chart(birth_datetime: datetime, birth_place: str):
    """
    Calculates the complete natal chart using Swiss Ephemeris.
    Also determines the timezone based on coordinates.
    Returns a tuple: (NatalChart, latitude, longitude, timezone_name)
    """
    # 1. Geocode the birth place to get latitude and longitude
    geolocator = Nominatim(user_agent="synastr_app")
    try:
        location = geolocator.geocode(birth_place)
        if not location:
            raise ValueError("Birth location not found.")
    except Exception as e:
        raise ValueError(
            f"Could not connect to the geocoding service to find '{birth_place}'."
        ) from e

    latitude, longitude = location.latitude, location.longitude

    # 2. Determine timezone using timezonefinder
    tf = TimezoneFinder()
    timezone_name = tf.timezone_at(lng=longitude, lat=latitude)
    if not timezone_name:
        raise ValueError("Could not determine timezone for the given location.")

    # 3. Convert birth datetime to local timezone and then to UTC
    local_tz = ZoneInfo(timezone_name)
    birth_local = birth_datetime.replace(tzinfo=local_tz)
    birth_dt_utc = birth_local.astimezone(ZoneInfo("UTC"))

    # 4. Set path for Swiss Ephemeris
    swe.set_ephe_path('./ephe')

    # 5. Calculate Julian day in UTC
    julian_day_utc = swe.utc_to_jd(
        birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
        birth_dt_utc.hour, birth_dt_utc.minute, birth_dt_utc.second,
        1  # Gregorian calendar
    )[1]

    chart = NatalChart()

    # 6. Calculate astrological houses (Placidus)
    houses_cusps, ascmc = swe.houses(julian_day_utc, latitude, longitude, b'P')

    # 7. Calculate planetary positions
    for name, planet_id in PLANET_MAPPING.items():
        position_data = swe.calc_ut(julian_day_utc, planet_id, swe.FLG_SPEED)
        planet_longitude = position_data[0][0]
        sign, icon = get_zodiac_sign(planet_longitude)

        # Determine which house the planet falls into
        planet_house_number = 0
        for i in range(12):
            cusp_start = houses_cusps[i]
            cusp_end = houses_cusps[(i + 1) % 12]

            if (cusp_start > cusp_end and (planet_longitude >= cusp_start or planet_longitude < cusp_end)) or \
               (cusp_start <= cusp_end and cusp_start <= planet_longitude < cusp_end):
                planet_house_number = i + 1
                break

        chart.positions.append(AstrologicalPosition(
            name=name,
            sign=sign,
            sign_icon=icon,
            degrees=planet_longitude % 30,
            house=planet_house_number
        ))

    # 8. Store house cusps
    house_names = ["Ascendant", "House 2", "House 3", "Imum Coeli", "House 5", "House 6",
                   "Descendant", "House 8", "House 9", "Midheaven", "House 11", "House 12"]

    for i in range(12):
        house_longitude = houses_cusps[i]
        sign, icon = get_zodiac_sign(house_longitude)
        chart.houses.append(AstrologicalPosition(
            name=house_names[i],
            sign=sign,
            sign_icon=icon,
            degrees=house_longitude % 30,
            house=i + 1
        ))

    # Return chart with location and timezone info
    return chart, latitude, longitude, timezone_name
