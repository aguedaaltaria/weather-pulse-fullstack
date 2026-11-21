import csv
import io
import json
from fpdf import FPDF


def export_to_json(records):
    """
    Convert weather records into a pretty-printed JSON string.
    Convertir los registros del clima en un texto JSON bien formateado.
    """
    return json.dumps({"records": records}, indent=2, ensure_ascii=False)


def export_to_csv(records):
    """
    Convert weather records into CSV text (compatible with Excel and Google Sheets).
    Convertir los registros del clima en texto CSV (compatible con Excel y Google Sheets).
    """
    # StringIO acts like an in-memory text file / StringIO actúa como un archivo de texto en memoria
    output = io.StringIO()
    field_names = [
        "id",
        "location_query",
        "resolved_name",
        "latitude",
        "longitude",
        "start_date",
        "end_date",
        "average_temperature",
        "notes",
        "created_at",
    ]
    writer = csv.DictWriter(output, fieldnames=field_names)
    writer.writeheader()

    for record in records:
        writer.writerow({
            "id": record["id"],
            "location_query": record["location_query"],
            "resolved_name": record["resolved_name"],
            "latitude": record["latitude"],
            "longitude": record["longitude"],
            "start_date": record["start_date"],
            "end_date": record["end_date"],
            "average_temperature": record["average_temperature"],
            "notes": record["notes"],
            "created_at": record["created_at"],
        })

    return output.getvalue()


def export_to_markdown(records):
    """
    Convert weather records into a clean Markdown table.
    Convertir los registros del clima en una tabla limpia de Markdown.
    """
    lines = [
        "# WeatherPulse Studio — Saved Weather Records",
        "",
        "| ID | Location | Start Date | End Date | Avg Temp (°C) | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for record in records:
        average_text = "N/A"
        if record["average_temperature"] is not None:
            average_text = f"{record['average_temperature']}°C"

        # Replace pipe characters so they do not break the Markdown table
        # Reemplazar barras verticales para no romper la tabla de Markdown
        clean_name = str(record["resolved_name"]).replace("|", "-")
        clean_notes = str(record["notes"]).replace("|", "-")

        lines.append(
            f"| {record['id']} | {clean_name} | {record['start_date']} | "
            f"{record['end_date']} | {average_text} | {clean_notes} |"
        )

    return "\n".join(lines)


def _safe_pdf_text(text):
    """
    Ensure text is compatible with standard PDF fonts (Latin-1).
    Asegurar que el texto sea compatible con las fuentes estándar de PDF (Latin-1).
    """
    return str(text).encode("latin-1", "replace").decode("latin-1")


def export_to_pdf(records):
    """
    Generate a PDF report in memory and return its raw bytes.
    Generar un reporte PDF en memoria y devolver sus bytes.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title / Título
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "WeatherPulse Studio - Saved Weather Records", ln=True)
    pdf.ln(4)

    if not records:
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, "No weather records saved yet.", ln=True)
    else:
        for record in records:
            average_text = "N/A"
            if record["average_temperature"] is not None:
                average_text = f"{record['average_temperature']} C"

            pdf.set_font("Helvetica", "B", 12)
            header_line = f"#{record['id']} - {record['resolved_name']}"
            pdf.cell(0, 8, _safe_pdf_text(header_line), ln=True)

            pdf.set_font("Helvetica", "", 10)
            details_line = (
                f"Dates: {record['start_date']} to {record['end_date']} | "
                f"Average Temp: {average_text}"
            )
            pdf.cell(0, 6, _safe_pdf_text(details_line), ln=True)

            if record["notes"]:
                pdf.cell(0, 6, _safe_pdf_text(f"Notes: {record['notes']}"), ln=True)

            pdf.ln(3)

    # Return PDF as bytes so Flask can send it directly / Devolver PDF en bytes para enviarlo con Flask
    return bytes(pdf.output())