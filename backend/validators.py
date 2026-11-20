from datetime import date, timedelta

# Date limits supported by Open-Meteo / Límites de fechas soportados por Open-Meteo
MIN_SUPPORTED_DATE = date(1940, 1, 1)
MAX_FORECAST_DAYS = 15
MAX_RANGE_DAYS = 90


class ValidationError(Exception):
    """
    Custom error raised when user input is invalid.
    Error personalizado que se lanza cuando los datos del usuario no son válidos.
    """
    pass


def validate_location(raw_location):
    """
    Check that location is a non-empty text with safe length.
    Verificar que la ubicación sea un texto no vacío y de longitud segura.
    """
    if not isinstance(raw_location, str) or not raw_location.strip():
        raise ValidationError("Location is required and cannot be empty.")

    cleaned = raw_location.strip()
    if len(cleaned) < 2:
        raise ValidationError("Location must be at least 2 characters long.")
    if len(cleaned) > 120:
        raise ValidationError("Location must be 120 characters or fewer.")

    return cleaned


def parse_gps_coordinates(location_text):
    """
    Check if the user typed 'lat, lon' coordinates. Returns (lat, lon) or None.
    Revisar si el usuario escribió coordenadas 'lat, lon'. Devuelve (lat, lon) o None.
    """
    if "," not in location_text:
        return None

    parts = location_text.split(",")
    if len(parts) != 2:
        return None

    try:
        latitude = float(parts[0].strip())
        longitude = float(parts[1].strip())
    except ValueError:
        # Not numbers (for example "Sunnyvale, CA") / No son números (ej. "Sunnyvale, CA")
        return None

    return validate_coordinates(latitude, longitude)


def validate_coordinates(raw_latitude, raw_longitude):
    """
    Ensure latitude is between -90 and 90, and longitude between -180 and 180.
    Asegurar que la latitud esté entre -90 y 90, y la longitud entre -180 y 180.
    """
    try:
        latitude = float(raw_latitude)
        longitude = float(raw_longitude)
    except (TypeError, ValueError):
        raise ValidationError("Latitude and longitude must be valid numbers.")

    if latitude < -90 or latitude > 90:
        raise ValidationError("Latitude must be between -90 and 90.")
    if longitude < -180 or longitude > 180:
        raise ValidationError("Longitude must be between -180 and 180.")

    return latitude, longitude


def parse_date(raw_date, field_name):
    """
    Convert a YYYY-MM-DD text into a Python date object.
    Convertir un texto YYYY-MM-DD en un objeto date de Python.
    """
    if not isinstance(raw_date, str) or not raw_date.strip():
        raise ValidationError(f"{field_name} is required in YYYY-MM-DD format.")

    try:
        return date.fromisoformat(raw_date.strip())
    except ValueError:
        raise ValidationError(f"{field_name} must be a valid date (YYYY-MM-DD).")


def validate_date_range(raw_start_date, raw_end_date):
    """
    Validate that start_date <= end_date and both are within allowed limits.
    Validar que start_date <= end_date y que ambas estén dentro de los límites permitidos.
    """
    start = parse_date(raw_start_date, "start_date")
    end = parse_date(raw_end_date, "end_date")

    if start > end:
        raise ValidationError("start_date must be earlier than or equal to end_date.")

    if start < MIN_SUPPORTED_DATE:
        raise ValidationError("start_date cannot be earlier than 1940-01-01.")

    max_future_date = date.today() + timedelta(days=MAX_FORECAST_DAYS)
    if end > max_future_date:
        raise ValidationError(f"end_date cannot be later than {max_future_date.isoformat()}.")

    total_days = (end - start).days + 1
    if total_days > MAX_RANGE_DAYS:
        raise ValidationError(f"Date range cannot exceed {MAX_RANGE_DAYS} days.")

    return start.isoformat(), end.isoformat()


def validate_notes(raw_notes):
    """
    Validate optional notes field (max 300 characters).
    Validar el campo opcional de notas (máximo 300 caracteres).
    """
    if raw_notes is None:
        return ""
    if not isinstance(raw_notes, str):
        raise ValidationError("Notes must be text.")

    cleaned = raw_notes.strip()
    if len(cleaned) > 300:
        raise ValidationError("Notes must be 300 characters or fewer.")
    return cleaned