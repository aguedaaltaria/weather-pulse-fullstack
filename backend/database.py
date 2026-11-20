import sqlite3
import json
from datetime import datetime

# Name of the local SQLite database file / Nombre del archivo local de base de datos SQLite
DATABASE_FILE = "weather_records.db"


def get_connection():
    """
    Open a connection to SQLite / Abrir una conexión a SQLite.
    row_factory lets us access columns by name (like a dictionary) instead of numbers.
    row_factory nos permite acceder a las columnas por nombre (como diccionario) y no por número.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """
    Create the table if it does not exist / Crear la tabla si no existe.
    """
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS weather_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_query TEXT NOT NULL,
            resolved_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            daily_temperatures TEXT NOT NULL,
            average_temperature REAL,
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def format_row(row):
    """
    Turn a database row into a normal Python dictionary / Convertir una fila en un diccionario normal.
    We use json.loads() to turn the saved temperature text back into a Python list.
    Usamos json.loads() para convertir el texto de temperaturas de vuelta a una lista de Python.
    """
    return {
        "id": row["id"],
        "location_query": row["location_query"],
        "resolved_name": row["resolved_name"],
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "start_date": row["start_date"],
        "end_date": row["end_date"],
        "daily_temperatures": json.loads(row["daily_temperatures"]),
        "average_temperature": row["average_temperature"],
        "notes": row["notes"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def create_weather_record(
    location_query, resolved_name, latitude, longitude,
    start_date, end_date, daily_temperatures, average_temperature, notes=""
):
    """
    Save a new weather record / Guardar un nuevo registro del clima.
    """
    now = datetime.now().isoformat()
    # SQLite cannot save Python lists directly, so we convert it to text with json.dumps()
    # SQLite no guarda listas de Python directamente, así que la convertimos a texto con json.dumps()
    temps_as_text = json.dumps(daily_temperatures)

    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO weather_records (
            location_query, resolved_name, latitude, longitude,
            start_date, end_date, daily_temperatures,
            average_temperature, notes, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            location_query, resolved_name, latitude, longitude,
            start_date, end_date, temps_as_text,
            average_temperature, notes, now, now
        ),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return get_weather_record_by_id(new_id)


def get_all_weather_records():
    """
    Get all saved records, newest first / Obtener todos los registros, los más nuevos primero.
    """
    conn = get_connection()
    rows = conn.execute("SELECT * FROM weather_records ORDER BY id DESC").fetchall()
    conn.close()

    return [format_row(row) for row in rows]


def get_weather_record_by_id(record_id):
    """
    Find one record by its ID / Buscar un registro por su ID.
    """
    conn = get_connection()
    row = conn.execute("SELECT * FROM weather_records WHERE id = ?", (record_id,)).fetchone()
    conn.close()

    if row is None:
        return None
    return format_row(row)


def update_weather_record(
    record_id, location_query, resolved_name, latitude, longitude,
    start_date, end_date, daily_temperatures, average_temperature, notes=""
):
    """
    Update an existing record / Actualizar un registro existente.
    """
    now = datetime.now().isoformat()
    temps_as_text = json.dumps(daily_temperatures)

    conn = get_connection()
    cursor = conn.execute(
        """
        UPDATE weather_records
        SET location_query = ?, resolved_name = ?, latitude = ?, longitude = ?,
            start_date = ?, end_date = ?, daily_temperatures = ?,
            average_temperature = ?, notes = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            location_query, resolved_name, latitude, longitude,
            start_date, end_date, temps_as_text,
            average_temperature, notes, now, record_id
        ),
    )
    conn.commit()
    updated_rows = cursor.rowcount
    conn.close()

    if updated_rows == 0:
        return None
    return get_weather_record_by_id(record_id)


def delete_weather_record(record_id):
    """
    Delete a record by its ID / Eliminar un registro por su ID.
    Returns True if deleted, False if not found / Devuelve True si se borró, False si no existía.
    """
    conn = get_connection()
    cursor = conn.execute("DELETE FROM weather_records WHERE id = ?", (record_id,))
    conn.commit()
    deleted_rows = cursor.rowcount
    conn.close()

    return deleted_rows > 0