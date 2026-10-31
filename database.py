import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

CSV_FILE = BASE_DIR / "hospital_event_logs.csv"
DB_FILE = BASE_DIR / "careflow.db"


def create_database():
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {CSV_FILE}"
        )

    connection = sqlite3.connect(DB_FILE)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hospital_event_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                activity_name TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

        with open(
            CSV_FILE,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            reader = csv.DictReader(file)

            required_columns = {
                "case_id",
                "activity_name",
                "timestamp"
            }

            if not required_columns.issubset(
                reader.fieldnames or []
            ):
                raise ValueError(
                    "CSV file does not contain "
                    "the required columns."
                )

            rows = [
                (
                    row["case_id"],
                    row["activity_name"],
                    row["timestamp"]
                )
                for row in reader
            ]

        cursor.execute("SELECT COUNT(*) FROM hospital_event_logs")
        existing_count = cursor.fetchone()[0]

        if existing_count == 0:
            cursor.executemany("""
                INSERT INTO hospital_event_logs
                (case_id, activity_name, timestamp)
                VALUES (?, ?, ?)
            """, rows)

        connection.commit()

        cursor.execute(
            "SELECT COUNT(*) FROM hospital_event_logs"
        )
        total = cursor.fetchone()[0]

        print("Database created successfully!")
        print(f"Database location: {DB_FILE}")
        print(f"Total event records: {total}")

    finally:
        connection.close()


if __name__ == "__main__":
    create_database()