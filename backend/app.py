import os
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS

import ai_service
import database
import export_service
import validators
import weather_service

# Path to built Vue frontend / Ruta al frontend compilado de Vue
FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
)

# Initialize Flask app serving Vue's dist folder and enable CORS
# Inicializar la app Flask sirviendo la carpeta dist de Vue y habilitar CORS
app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path="")
CORS(app)

# Make sure the SQLite table exists when the server starts
# Asegurar que la tabla SQLite exista cuando arranque el servidor
database.initialize_database()


@app.route("/", methods=["GET"])
def serve_frontend_index():
    """
    Serve the built Vue index.html at '/' if available, otherwise return API status.
    Servir el index.html compilado de Vue en '/' si existe; si no, devolver estado de la API.
    """
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(FRONTEND_DIST, "index.html")
    return jsonify({
        "message": "WeatherPulse Studio API is running. Run 'npm run build' in frontend/ to serve index.html here.",
        "health_endpoint": "/api/health",
    })


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
            location_info["latitude"], location_info["longitude"], language=lang
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
    UPDATE: Update notes (and optionally location/dates) in SQLite.
    UPDATE: Actualizar notas (y opcionalmente ubicación/fechas) en SQLite.
    """
    existing_record = database.get_weather_record_by_id(record_id)
    if existing_record is None:
        return jsonify({"error": "Record not found."}), 404

    data = request.get_json(silent=True) or {}

    try:
        # Use existing values if only notes were sent / Usar valores actuales si solo se enviaron notas
        location_query = validators.validate_location(
            data.get("location", existing_record["location_query"])
        )
        start_date, end_date = validators.validate_date_range(
            data.get("start_date", existing_record["start_date"]),
            data.get("end_date", existing_record["end_date"]),
        )
        notes = validators.validate_notes(data.get("notes", existing_record["notes"]))

        # Only re-fetch from Open-Meteo if location or dates changed
        # Solo volver a consultar Open-Meteo si cambiaron la ubicación o las fechas
        if (
            location_query != existing_record["location_query"]
            or start_date != existing_record["start_date"]
            or end_date != existing_record["end_date"]
        ):
            location_info = weather_service.resolve_location(location_query)
            daily_temps, avg_temp = weather_service.fetch_date_range_temperatures(
                location_info["latitude"], location_info["longitude"], start_date, end_date
            )
            resolved_name = location_info["resolved_name"]
            latitude = location_info["latitude"]
            longitude = location_info["longitude"]
        else:
            resolved_name = existing_record["resolved_name"]
            latitude = existing_record["latitude"]
            longitude = existing_record["longitude"]
            daily_temps = existing_record["daily_temperatures"]
            avg_temp = existing_record["average_temperature"]

        updated_record = database.update_weather_record(
            record_id=record_id,
            location_query=location_query,
            resolved_name=resolved_name,
            latitude=latitude,
            longitude=longitude,
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


@app.route("/api/export/<string:export_format>", methods=["GET"])
def export_records(export_format):
    """
    EXPORT: Download all saved records as json, csv, md, or pdf.
    EXPORT: Descargar todos los registros guardados como json, csv, md o pdf.
    """
    records = database.get_all_weather_records()
    chosen_format = export_format.lower()

    if chosen_format == "json":
        content = export_service.export_to_json(records)
        return Response(
            content,
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=weather_records.json"},
        )

    if chosen_format == "csv":
        content = export_service.export_to_csv(records)
        return Response(
            content,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=weather_records.csv"},
        )

    if chosen_format == "md" or chosen_format == "markdown":
        content = export_service.export_to_markdown(records)
        return Response(
            content,
            mimetype="text/markdown",
            headers={"Content-Disposition": "attachment; filename=weather_records.md"},
        )

    if chosen_format == "pdf":
        pdf_bytes = export_service.export_to_pdf(records)
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": "attachment; filename=weather_records.pdf"},
        )

    return jsonify({"error": "Unsupported format. Use json, csv, md, or pdf."}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5003)