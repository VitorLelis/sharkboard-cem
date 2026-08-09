import os
import psycopg2
from dotenv import load_dotenv
from tools.importer import import_positions
from tools.transformer import calculate_rankings
from tools.clubs import calculate_club_ranking
from tools.reporter import generate_report

def get_database_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

load_dotenv()
season = os.getenv("SEASON")
highlight_club = os.getenv("HIGHLIGHT_CLUB")
logo = os.getenv("LOGO")

if not season:
    raise ValueError("SEASON is not defined in .env")

if not highlight_club:
    raise ValueError("HIGHLIGHT_CLUB is not defined in .env")

if not logo:
    raise ValueError("LOGO is not defined in .env")

connection = get_database_connection()

try:
    positions = import_positions(connection=connection, season=season)
    ranks = calculate_rankings(positions)

    club_ranking = calculate_club_ranking(ranks)

    generate_report(
            ranks=ranks,
            club_ranking=club_ranking,
            output_path="report.pdf",
            season=season,
            logo_path=logo,
            highlight_club=highlight_club,
        )

finally:
    connection.close()
