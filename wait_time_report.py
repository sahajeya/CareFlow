
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "hospital_event_logs.csv"
OUTPUT_FILE = BASE_DIR / "wait_time_report.csv"


def main():
    if not INPUT_FILE.exists():
        print("Error: hospital_event_logs.csv not found.")
        return

    df = pd.read_csv(INPUT_FILE)

    # Standardize column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Find expected columns
    aliases = {
        "case_id": ["case_id", "caseid", "patient_id", "patientid"],
        "activity_name": [
            "activity_name", "activity", "activityname", "event"
        ],
        "timestamp": [
            "timestamp", "event_timestamp", "event_time", "time"
        ],
    }

    rename_map = {}

    for standard, candidates in aliases.items():
        for candidate in candidates:
            if candidate in df.columns:
                rename_map[candidate] = standard
                break

    df = df.rename(columns=rename_map)

    required = ["case_id", "activity_name", "timestamp"]
    missing = [column for column in required if column not in df.columns]

    if missing:
        print("Required columns missing:", missing)
        print("Available columns:", df.columns.tolist())
        return

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], errors="coerce"
    )

    df = df.dropna(subset=required)
    df = df.sort_values(["case_id", "timestamp"]).copy()

    # Calculate elapsed time between consecutive patient events
    df["previous_activity"] = (
        df.groupby("case_id")["activity_name"].shift(1)
    )

    df["previous_timestamp"] = (
        df.groupby("case_id")["timestamp"].shift(1)
    )

    df["elapsed_minutes"] = (
        df["timestamp"] - df["previous_timestamp"]
    ).dt.total_seconds() / 60

    transitions = df.dropna(subset=["elapsed_minutes"]).copy()
    transitions = transitions[
        transitions["elapsed_minutes"] >= 0
    ]

    if transitions.empty:
        print("No valid patient transitions found.")
        return

    report = (
        transitions.groupby("activity_name", as_index=False)
        .agg(
            event_count=("case_id", "size"),
            average_elapsed_minutes=("elapsed_minutes", "mean"),
            maximum_elapsed_minutes=("elapsed_minutes", "max"),
        )
        .rename(columns={"activity_name": "next_activity"})
    )

    report["average_elapsed_minutes"] = (
        report["average_elapsed_minutes"].round(2)
    )
    report["maximum_elapsed_minutes"] = (
        report["maximum_elapsed_minutes"].round(2)
    )

    report.to_csv(OUTPUT_FILE, index=False)

    print("\nCARE FLOW - WAIT TIME REPORT")
    print(report.to_string(index=False))
    print(f"\nReport saved to: {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()

