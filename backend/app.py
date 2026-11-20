from flask import Flask, jsonify, request
from flask_cors import CORS

import ai_service
import database
import validators
import weather_service

# Initialize Flask app and enable CORS for Vue frontend
# Inicializar la app Flask y habilitar CORS para el frontend en Vue
app = Flask(__name__)
CORS(app)

# Make sure the SQLite table exists when the server starts
# Asegurar que la tabla SQLite exista cuando arranque el servidor
database.initialize_database()


@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Simple endpoint to verify the server is running.
    Endpoint simple para verificar que el servidor está funcionando.
    """
    return jsonify({"status": "ok", "service": "WeatherPulse Studio API"})


@app.route("/api/weather", methods=["GET"])
def get_live_weather():
    """
    Get current weather, 5-day forecast, and AI advice by location or GPS coordinates.
    Obtener clima actual, pronóstico de 5 días y consejo IA por ubicación o coordenadas GPS.
    """
    location_param = request.args.get("location")
    lat_param = request.args.get("lat")
    lon_param = request.args.get("lon")
    lang = request.args.get("lang", "en").lower()

    try:
        # Option A: Browser Geolocation (lat & lon) / Opción A: Geolocalización del navegador
        if lat_param is not None and lon_param is not None:
            latitude, longitude = validators.validate_coordinates(lat_param, lon_param)
            resolved_name = weather_service.reverse_geocode(latitude, longitude)
            location_info = {
                "resolved_name": resolved_name,
                "latitude": latitude,
                "longitude": longitude,
            }
        # Option B: Text search (city, ZIP, landmark, or GPS string) / Opción B: Búsqueda por texto
        else:
            cleaned_location = validators.validate_location(location_param)
            location_info = weather_service.resolve_location(cleaned_location)

        weather_data = weather_service.fetch_current_and_forecast(
            location_info["latitude"], location_info["longitude"]
        )
        ai_summary = ai_service.generate_weather_advice(
            location_info["resolved_name"], weather_data["current"], language=lang
        )

        return jsonify({
            "location": location_info,
            "timezone": weather_data["timezone"],
            "current": weather_data["current"],
            "forecast_5_days": weather_data["forecast_5_days"],
            "ai_advice": ai_summary["advice"],
            "ai_model": ai_summary["model_used"],
        })

    except validators.ValidationError as error:
        return jsonify({"error": str(error)}), 400
    except weather_service.WeatherServiceError as error:
        return jsonify({"error": str(error)}), error.status_code


@app.route("/api/records", methods=["GET"])
def list_records():
    """
    READ: Return all saved weather records from SQLite.
    READ: Devolver todos los registros climáticos guardados en SQLite.
    """
    records = database.get_all_weather_records()
    return jsonify({"records": records})


@app.route("/api/records", methods=["POST"])
def create_record():
    """
    CREATE: Validate input, fetch real temperatures for the date range, and save to SQLite.
    CREATE: Validar datos, obtener temperaturas reales del rango de fechas y guardar en SQLite.
    """
    data = request.get_json(silent=True) or {}

    try:
        location_query = validators.validate_location(data.get("location"))
        start_date, end_date = validators.validate_date_range(
            data.get("start_date"), data.get("end_date")
        )
        notes = validators.validate_notes(data.get("notes"))

        location_info = weather_service.resolve_location(location_query)
        daily_temps, avg_temp = weather_service.fetch_date_range_temperatures(
            location_info["latitude"], location_info["longitude"], start_date, end_date
        )

        new_record = database.create_weather_record(
            location_query=location_query,
            resolved_name=location_info["resolved_name"],
            latitude=location_info["latitude"],
            longitude=location_info["longitude"],
            start_date=start_date,
            end_date=end_date,
            daily_temperatures=daily_temps,
            average_temperature=avg_temp,
            notes=notes,
        )
        return jsonify({"record": new_record}), 201

    except validators.ValidationError as error:
        return jsonify({"error": str(error)}), 400
    except weather_service.WeatherServiceError as error:
        return jsonify({"error": str(error)}), error.status_code


@app.route("/api/records/<int:record_id>", methods=["PUT"])
def update_record(record_id):
    """
    UPDATE: Re-validate location/dates, refresh temperatures, and update SQLite.
    UPDATE: Revalidar ubicación/fechas, actualizar temperaturas y guardar en SQLite.
    """
    if database.get_weather_record_by_id(record_id) is None:
        return jsonify({"error": "Record not found."}), 404

    data = request.get_json(silent=True) or {}

    try:
        location_query = validators.validate_location(data.get("location"))
        start_date, end_date = validators.validate_date_range(
            data.get("start_date"), data.get("end_date")
        )
        notes = validators.validate_notes(data.get("notes"))

        location_info = weather_service.resolve_location(location_query)
        daily_temps, avg_temp = weather_service.fetch_date_range_temperatures(
            location_info["latitude"], location_info["longitude"], start_date, end_date
        )

        updated_record = database.update_weather_record(
            record_id=record_id,
            location_query=location_query,
            resolved_name=location_info["resolved_name"],
            latitude=location_info["latitude"],
            longitude=location_info["longitude"],
            start_date=start_date,
            end_date=end_date,
            daily_temperatures=daily_temps,
            average_temperature=avg_temp,
            notes=notes,
        )
        return jsonify({"record": updated_record}), 200

    except validators.ValidationError as error:
        return jsonify({"error": str(error)}), 400
    except weather_service.WeatherServiceError as error:
        return jsonify({"error": str(error)}), error.status_code


@app.route("/api/records/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    """
    DELETE: Remove a saved weather record by ID.
    DELETE: Eliminar un registro climático guardado por su ID.
    """
    deleted = database.delete_weather_record(record_id)
    if not deleted:
        return jsonify({"error": "Record not found."}), 404

    return jsonify({"message": "Record deleted successfully.", "id": record_id}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)