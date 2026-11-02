
from flask import Flask, jsonify, render_template
import sqlite3
import pandas as pd
from pathlib import Path

app = Flask(__name__)

# Project folder and database location
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "careflow.db"


# --------------------------------
# Database Connection
# --------------------------------

def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# --------------------------------
# CSV Report Reader
# --------------------------------

def read_report(filename):
    file_path = BASE_DIR / filename

    if not file_path.exists():
        return None

    df = pd.read_csv(file_path)
    df = df.astype(object).where(pd.notna(df), None)

    return df.to_dict(orient="records")


# --------------------------------
# Home Page
# --------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------
# Backend Status API
# --------------------------------

@app.route("/api/status")
def status():
    return jsonify({
        "project": "CareFlow",
        "description": "Clinical Pathway Process Mining",
        "status": "Backend is running"
    })


# --------------------------------
# Dashboard Summary API
# --------------------------------

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


# --------------------------------
# Patient Records API
# --------------------------------

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


# --------------------------------
# Individual Patient Details API
# --------------------------------

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


# --------------------------------
# Bottleneck Ranking API
# --------------------------------

@app.route("/api/bottlenecks")
def bottlenecks():
    try:
        data = read_report("bottleneck_ranking_report.csv")

        if data is None:
            return jsonify({
                "error": "Bottleneck report not found"
            }), 404

        return jsonify(data)

    except Exception as error:
        return jsonify({
            "error": "Unable to retrieve bottleneck analysis",
            "details": str(error)
        }), 500


# --------------------------------
# Patient Pathway Analysis API
# --------------------------------

@app.route("/api/pathway-analysis")
def pathway_analysis():
    try:
        data = read_report("patient_pathway_summary.csv")

        if data is None:
            return jsonify({
                "error": "Patient pathway report not found"
            }), 404

        return jsonify(data)

    except Exception as error:
        return jsonify({
            "error": "Unable to retrieve patient pathway analysis",
            "details": str(error)
        }), 500


# --------------------------------
# Activity Waiting Time API
# --------------------------------

@app.route("/api/activity-waiting")
def activity_waiting():
    try:
        data = read_report("activity_waiting_analysis.csv")

        if data is None:
            return jsonify({
                "error": "Activity waiting report not found"
            }), 404

        return jsonify(data)

    except Exception as error:
        return jsonify({
            "error": "Unable to retrieve activity waiting analysis",
            "details": str(error)
        }), 500


# --------------------------------
# Run Flask Application
# --------------------------------

if __name__ == "__main__":
    app.run(debug=True)
