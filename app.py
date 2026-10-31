from flask import Flask, jsonify, render_template
import sqlite3
from pathlib import Path

app = Flask(__name__)

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "careflow.db"


# Database connection
def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# Home page - Frontend
@app.route("/")
def home():
    return render_template("index.html")


# API: Backend status
@app.route("/api/status")
def status():
    return jsonify({
        "project": "CareFlow",
        "description": "Clinical Pathway Process Mining",
        "status": "Backend is running"
    })


# API: Dashboard summary
@app.route("/api/summary")
def summary():
    connection = get_db_connection()

    try:
        total_patients = connection.execute("""
            SELECT COUNT(DISTINCT case_id)
            FROM hospital_event_logs
        """).fetchone()[0]

        total_events = connection.execute("""
            SELECT COUNT(*)
            FROM hospital_event_logs
        """).fetchone()[0]

        total_activities = connection.execute("""
            SELECT COUNT(DISTINCT activity_name)
            FROM hospital_event_logs
        """).fetchone()[0]

        return jsonify({
            "total_patients": total_patients,
            "total_events": total_events,
            "total_activities": total_activities
        })

    except sqlite3.Error as error:
        return jsonify({
            "error": "Unable to retrieve dashboard summary",
            "details": str(error)
        }), 500

    finally:
        connection.close()


# API: Patient journey records
@app.route("/api/patients")
def patients():
    connection = get_db_connection()

    try:
        rows = connection.execute("""
            SELECT
                case_id,
                MIN(timestamp) AS start_time,
                MAX(timestamp) AS end_time,
                COUNT(*) AS total_activities
            FROM hospital_event_logs
            GROUP BY case_id
            ORDER BY case_id
            LIMIT 100
        """).fetchall()

        return jsonify([dict(row) for row in rows])

    except sqlite3.Error as error:
        return jsonify({
            "error": "Unable to retrieve patient records",
            "details": str(error)
        }), 500

    finally:
        connection.close()


# API: Individual patient details
@app.route("/api/patients/<case_id>")
def patient_details(case_id):
    connection = get_db_connection()

    try:
        rows = connection.execute("""
            SELECT case_id, activity_name, timestamp
            FROM hospital_event_logs
            WHERE case_id = ?
            ORDER BY timestamp
        """, (case_id,)).fetchall()

        if not rows:
            return jsonify({
                "error": "Patient record not found"
            }), 404

        return jsonify([dict(row) for row in rows])

    except sqlite3.Error as error:
        return jsonify({
            "error": "Unable to retrieve patient details",
            "details": str(error)
        }), 500

    finally:
        connection.close()


# Run application
if __name__ == "__main__":
    app.run(debug=True)