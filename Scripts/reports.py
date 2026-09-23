import json
import csv
import matplotlib.pyplot as plt
from pathlib import Path
from decimal import Decimal
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from App.db import get_connection

OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)

LOGO_PATH = Path("scripts/logo_fiir.jpg")


def normalize(v):
    if isinstance(v, Decimal):
        x = float(v)
        return int(x) if x.is_integer() else x
    return v


def fetch_data(sql):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(sql)
        rows = cur.fetchall()
        return [{"name": str(r[0]), "value": normalize(r[1])} for r in rows]
    finally:
        cur.close()
        conn.close()


def export_csv(data, csv_path):
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "value"])
        writer.writeheader()
        writer.writerows(data)


def export_json(data, json_path):
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_chart(data, chart_path, title, xlabel, ylabel):
    names = [d["name"] for d in data]
    values = [d["value"] for d in data]

    plt.figure(figsize=(8, 5))
    plt.bar(names, values, color="#2c3e50")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(str(chart_path))
    plt.close()


def generate_pdf(data, pdf_path, chart_path, report_title, subtitle, intro_text, table_headers):
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=20
    )
    normal_style = styles["Normal"]

    if LOGO_PATH.exists():
        logo = Image(str(LOGO_PATH), width=1.5 * inch, height=1.5 * inch)
        elements.append(logo)
        elements.append(Spacer(1, 20))

    elements.append(Paragraph(report_title, title_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(subtitle, styles["Heading2"]))
    elements.append(Spacer(1, 15))

    full_intro = f"{intro_text}<br/>Raport generat la data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elements.append(Paragraph(full_intro, normal_style))
    elements.append(Spacer(1, 20))

    table_data = [table_headers]
    for d in data:
        table_data.append([d["name"], str(d["value"])])

    table = Table(table_data, colWidths=[300, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e58")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ecf0f1")),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 25))

    if chart_path.exists():
        chart = Image(str(chart_path), width=6 * inch, height=4 * inch)
        elements.append(chart)

    doc.build(elements)


def process_report(config):
    print(f"Generare raport: {config['base_name']}...")

    csv_path = OUT_DIR / f"{config['base_name']}.csv"
    json_path = OUT_DIR / f"{config['base_name']}.json"
    chart_path = OUT_DIR / f"{config['base_name']}_chart.png"
    pdf_path = OUT_DIR / f"{config['base_name']}.pdf"

    data = fetch_data(config['sql'])
    if not data:
        print(f"  -> Nu exista date pentru {config['base_name']}.")
        return

    export_csv(data, csv_path)
    export_json(data, json_path)
    generate_chart(data, chart_path, config['chart_title'], config['chart_xlabel'], config['chart_ylabel'])

    generate_pdf(
        data=data,
        pdf_path=pdf_path,
        chart_path=chart_path,
        report_title="Raport Business Intelligence",
        subtitle=config['pdf_subtitle'],
        intro_text=config['pdf_intro'],
        table_headers=config['table_headers']
    )
    print(f"  -> Finalizat cu succes.")


def main():
    report1 = {
        "base_name": "Top_Meniuri_Vandute",
        "sql": """
            SELECT m.nume_meniu, SUM(rm.cantitate) AS total_qty
            FROM rezervari_meniuri rm
            JOIN meniuri m ON m.id_meniu = rm.id_meniu
            GROUP BY m.id_meniu, m.nume_meniu
            ORDER BY total_qty DESC
        """,
        "chart_title": "Top meniuri comandate",
        "chart_xlabel": "Meniuri",
        "chart_ylabel": "Cantitate comandata",
        "pdf_subtitle": "Top Meniuri Comandate",
        "pdf_intro": "Acest raport prezinta analiza meniurilor comandate in cadrul aplicatiei de Gestiune Rezervari. Datele sunt agregate din tabelele de rezervari si meniuri si sunt ordonate descrescator in functie de cantitatea totala comandata de clienti.",
        "table_headers": ["Preparat Meniu", "Cantitate Totala"]
    }

    report2 = {
        "base_name": "Top_Clienti_Activi",
        "sql": """
            SELECT c.nume_client, COUNT(r.id_rezervare) AS total_rezervari
            FROM rezervari r
            JOIN clienti c ON c.id_client = r.id_client
            GROUP BY c.id_client, c.nume_client
            ORDER BY total_rezervari DESC
        """,
        "chart_title": "Top clienti cu cele mai multe rezervari",
        "chart_xlabel": "Client",
        "chart_ylabel": "Numar Rezervari",
        "pdf_subtitle": "Clienti Activi - Top Rezervari",
        "pdf_intro": "Acest raport prezinta analiza implicarii clientilor, calculand numarul total de rezervari efectuate de fiecare client inregistrat. Datele sunt utile pentru identificarea clientilor fideli.",
        "table_headers": ["Nume Client", "Numar Rezervari"]
    }

    process_report(report1)
    process_report(report2)

    print("\nToate rapoartele au fost generate in folderul:", OUT_DIR.resolve())


if __name__ == "__main__":
    main()