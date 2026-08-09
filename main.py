import os
import psycopg2
from dotenv import load_dotenv
from importer import import_positions

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

if not season:
    raise ValueError("SEASON is not defined in .env")

connection = get_database_connection()

try:
    positions = import_positions(connection=connection, season=season)

finally:
    connection.close()
