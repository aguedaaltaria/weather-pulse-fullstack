from datetime import date, timedelta
import requests

from validators import parse_gps_coordinates

# External API URLs (free, no API key needed) / URLs de APIs externas (gratis, sin API key)
OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"

REQUEST_TIMEOUT = 25
HEADERS = {"User-Agent": "WeatherPulseStudio/1.0"}

# Map numeric WMO weather codes to English, Spanish, and icon names
# Mapear códigos numéricos WMO a inglés, español y nombres de iconos
WEATHER_CODES = {
    0: ("Clear sky", "Cielo despejado", "clear"),
    1: ("Mainly clear", "Mayormente despejado", "partly-cloudy"),
    2: ("Partly cloudy", "Parcialmente nublado", "partly-cloudy"),
    3: ("Overcast", "Nublado", "cloudy"),
    45: ("Foggy", "Con niebla", "fog"),
    48: ("Rime fog", "Niebla con escarcha", "fog"),
    51: ("Light drizzle", "Llovizna ligera", "drizzle"),
    53: ("Moderate drizzle", "Llovizna moderada", "drizzle"),
    55: ("Dense drizzle", "Llovizna intensa", "drizzle"),
    61: ("Slight rain", "Lluvia ligera", "rain"),
    63: ("Moderate rain", "Lluvia moderada", "rain"),
    65: ("Heavy rain", "Lluvia fuerte", "rain"),
    71: ("Slight snow", "Nieve ligera", "snow"),
    73: ("Moderate snow", "Nieve moderada", "snow"),
    75: ("Heavy snow", "Nieve fuerte", "snow"),
    80: ("Rain showers", "Chubascos ligeros", "rain"),
    81: ("Moderate showers", "Chubascos moderados", "rain"),
    82: ("Heavy showers", "Chubascos fuertes", "storm"),
    95: ("Thunderstorm", "Tormenta eléctrica", "storm"),
    96: ("Thunderstorm with hail", "Tormenta con granizo", "storm"),
    99: ("Severe thunderstorm", "Tormenta severa", "storm"),
}


class WeatherServiceError(Exception):
    """
    Custom error for external API failures / Error personalizado para fallos de APIs externas.
    """
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


def describe_weather_code(code, language="en"):
    """
    Convert a WMO weather code into description (EN/ES) and icon.
    Convertir código WMO a descripción (EN/ES) e icono.
    """
    en_text, es_text, icon = WEATHER_CODES.get(
        code, ("Unknown conditions", "Condiciones desconocidas", "cloudy")
    )
    description = es_text if language == "es" else en_text
    return {"description": description, "icon": icon}


def reverse_geocode(latitude, longitude):
    """
    Turn GPS coordinates into a place name using OpenStreetMap / Convertir GPS a nombre de lugar.
    """
    try:
        response = requests.get(
            NOMINATIM_REVERSE_URL,
            params={"lat": latitude, "lon": longitude, "format": "json", "zoom": 10},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        if response.ok:
            name = response.json().get("display_name")
            if name:
                return name
    except requests.RequestException:
        pass
    return f"Coordinates ({latitude:.4f}, {longitude:.4f})"


def resolve_location(location_query):
    """
    Find latitude, longitude, and official name for any city, ZIP, landmark, or GPS.
    Buscar latitud, longitud y nombre oficial para cualquier ciudad, ZIP, lugar o GPS.
    """
    # 1. Check if the user typed GPS coordinates / 1. Revisar si el usuario escribió coordenadas GPS
    gps = parse_gps_coordinates(location_query)
    if gps:
        latitude, longitude = gps
        return {
            "resolved_name": reverse_geocode(latitude, longitude),
            "latitude": latitude,
            "longitude": longitude,
        }

    # 2. Primary search with Open-Meteo / 2. Búsqueda principal con Open-Meteo
    try:
        response = requests.get(
            OPEN_METEO_GEOCODING_URL,
            params={"name": location_query, "count": 1, "language": "en", "format": "json"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        results = response.json().get("results") or []
        if results:
            match = results[0]
            parts = [match.get("name"), match.get("admin1"), match.get("country")]
            full_name = ", ".join(part for part in parts if part)
            return {
                "resolved_name": full_name,
                "latitude": float(match["latitude"]),
                "longitude": float(match["longitude"]),
            }
    except requests.RequestException:
        pass

    # 3. Fallback search with Nominatim (great for ZIP codes and landmarks)
    # 3. Búsqueda de respaldo con Nominatim (ideal para códigos postales y puntos de interés)
    try:
        response = requests.get(
            NOMINATIM_SEARCH_URL,
            params={"q": location_query, "format": "json", "limit": 1},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        results = response.json()
        if results:
            match = results[0]
            return {
                "resolved_name": match.get("display_name", location_query),
                "latitude": float(match["lat"]),
                "longitude": float(match["lon"]),
            }
    except requests.RequestException as error:
        print("Error de Nominatim:", error)
        raise WeatherServiceError("Unable to reach geocoding service.", 502)

    raise WeatherServiceError(f"Location '{location_query}' could not be found.", 404)


def fetch_current_and_forecast(latitude, longitude, language="en"):
    """
    Get current weather and 5-day forecast from Open-Meteo.
    Obtener clima actual y pronóstico de 5 días desde Open-Meteo.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 6,
    }
    try:
        response = requests.get(OPEN_METEO_FORECAST_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as error:
        print("Error de Open-Meteo:", error)
        raise WeatherServiceError("Failed to fetch weather forecast.", 502)

    current = data.get("current", {})
    current_info = describe_weather_code(current.get("weather_code"), language)
    daily = data.get("daily", {})
    dates = daily.get("time", [])

    # Skip index 0 (today) to build the next 5 days / Saltar índice 0 (hoy) para armar los próximos 5 días
    forecast_5_days = []
    for i in range(1, min(len(dates), 6)):
        day_info = describe_weather_code(daily["weather_code"][i], language)
        forecast_5_days.append({
            "date": dates[i],
            "temperature_max": daily["temperature_2m_max"][i],
            "temperature_min": daily["temperature_2m_min"][i],
            "precipitation_probability": daily["precipitation_probability_max"][i],
            "weather_code": daily["weather_code"][i],
            "description": day_info["description"],
            "icon": day_info["icon"],
        })

    return {
        "timezone": data.get("timezone", "UTC"),
        "current": {
            "temperature": current.get("temperature_2m"),
            "apparent_temperature": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "weather_code": current.get("weather_code"),
            "description": current_info["description"],
            "icon": current_info["icon"],
        },
        "forecast_5_days": forecast_5_days,
    }


def _query_daily_range(url, latitude, longitude, start_date, end_date):
    """
    Helper to fetch daily temperatures from either Archive or Forecast API.
    Función auxiliar para obtener temperaturas diarias desde la API Archive o Forecast.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,weather_code",
        "timezone": "auto",
    }
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        daily = response.json().get("daily", {})
    except requests.RequestException as error:
        print("Error de Open-Meteo (rango de fechas):", error)
        raise WeatherServiceError("Failed to fetch date-range temperatures.", 502)

    dates = daily.get("time", [])
    records = []
    for i, day_str in enumerate(dates):
        temp_max = daily["temperature_2m_max"][i]
        temp_min = daily["temperature_2m_min"][i]
        temp_mean = daily.get("temperature_2m_mean", [None] * len(dates))[i]

        # If mean is missing, calculate average of max and min / Si falta la media, promediar max y min
        if temp_mean is None and temp_max is not None and temp_min is not None:
            temp_mean = round((temp_max + temp_min) / 2, 1)

        day_info = describe_weather_code(daily["weather_code"][i])
        records.append({
            "date": day_str,
            "temperature_max": temp_max,
            "temperature_min": temp_min,
            "temperature_mean": temp_mean,
            "description": day_info["description"],
        })
    return records


def fetch_date_range_temperatures(latitude, longitude, start_date, end_date):
    """
    Fetch temperatures for past or near-future dates and compute the overall average.
    Obtener temperaturas para fechas pasadas o futuras cercanas y calcular el promedio general.
    """
    start_obj = date.fromisoformat(start_date)
    end_obj = date.fromisoformat(end_date)
    archive_cutoff = date.today() - timedelta(days=5)

    daily_records = []

    if end_obj < archive_cutoff:
        daily_records = _query_daily_range(
            OPEN_METEO_ARCHIVE_URL, latitude, longitude, start_date, end_date
        )
    elif start_obj >= archive_cutoff:
        daily_records = _query_daily_range(
            OPEN_METEO_FORECAST_URL, latitude, longitude, start_date, end_date
        )
    else:
        # Split range between Archive (past) and Forecast (recent/future)
        # Dividir el rango entre Archive (pasado) y Forecast (reciente/futuro)
        archive_end = (archive_cutoff - timedelta(days=1)).isoformat()
        forecast_start = archive_cutoff.isoformat()
        daily_records.extend(
            _query_daily_range(OPEN_METEO_ARCHIVE_URL, latitude, longitude, start_date, archive_end)
        )
        daily_records.extend(
            _query_daily_range(OPEN_METEO_FORECAST_URL, latitude, longitude, forecast_start, end_date)
        )

    valid_means = [day["temperature_mean"] for day in daily_records if day["temperature_mean"] is not None]
    average_temp = round(sum(valid_means) / len(valid_means), 2) if valid_means else None

    return daily_records, average_temp