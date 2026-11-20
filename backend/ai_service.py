import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

PRIMARY_MODEL = os.getenv("GEMINI_PRIMARY_MODEL", "gemini-3.5-flash-lite")
FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.8-flash")


def _basic_fallback_advice(location_name, current_weather, language="en"):
    """
    Simple rule-based advice in English or Spanish if Gemini is unavailable.
    Consejo simple en inglés o español si Gemini no está disponible.
    """
    temp = current_weather.get("temperature")
    desc = current_weather.get("description", "variable conditions")

    if language == "es":
        if temp is None:
            return f"Clima actual en {location_name}: {desc}. Vístete cómodo."
        if temp < 12:
            return f"Hace frío en {location_name} ({temp}°C). Lleva una chaqueta abrigada."
        if temp < 24:
            return f"Clima agradable en {location_name} ({temp}°C). Una capa ligera será ideal."
        return f"Hace calor en {location_name} ({temp}°C). Usa ropa fresca e hidrátate."

    if temp is None:
        return f"Current conditions in {location_name}: {desc}. Dress comfortably."
    if temp < 12:
        return f"It is chilly in {location_name} ({temp}°C, {desc}). Wear a warm jacket."
    if temp < 24:
        return f"Pleasant weather in {location_name} ({temp}°C, {desc}). A light layer is ideal."
    return f"It is warm in {location_name} ({temp}°C, {desc}). Wear light clothing and stay hydrated."


def generate_weather_advice(location_name, current_weather, language="en"):
    """
    Generate a short AI weather summary in English ('en') or Spanish ('es').
    Generar un resumen corto del clima con IA en inglés ('en') o español ('es').
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    target_language = "Spanish" if language == "es" else "English"

    if not api_key or api_key == "your_gemini_api_key_here":
        return {
            "advice": _basic_fallback_advice(location_name, current_weather, language),
            "model_used": "rule-based-fallback",
        }

    prompt = (
        f"You are a concise, friendly weather assistant. "
        f"Based ONLY on these real-time facts for {location_name}: "
        f"temperature {current_weather.get('temperature')}°C, "
        f"feels like {current_weather.get('apparent_temperature')}°C, "
        f"humidity {current_weather.get('humidity')}%, "
        f"wind {current_weather.get('wind_speed')} km/h, "
        f"condition: {current_weather.get('description')}. "
        f"Write 2 short sentences in {target_language}: one summarizing the weather "
        f"and one practical clothing/activity tip."
    )

    client = genai.Client(api_key=api_key)

    for model_name in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            if response.text:
                return {"advice": response.text.strip(), "model_used": model_name}
        except Exception:
            continue

    return {
        "advice": _basic_fallback_advice(location_name, current_weather, language),
        "model_used": "rule-based-fallback",
    }