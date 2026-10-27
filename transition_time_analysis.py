
import pandas as pd
from pathlib import Path

# Input and output file paths
BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "hospital_event_logs.csv"
TRANSITION_FILE = BASE_DIR / "transition_times.csv"
SUMMARY_FILE = BASE_DIR / "bottleneck_summary.csv"

def main():
    # 1. Load hospital event logs
    if not INPUT_FILE.exists():
        print(f"Error: Input file not found: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)

    # 2. Standardize column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Support common column-name variations
    aliases = {
        "case_id": ["case_id", "caseid", "patient_id", "patientid"],
        "activity_name": [
            "activity_name", "activity", "activityname", "event"
        ],
        "timestamp": [
            "timestamp", "event_timestamp", "time", "event_time"
        ],
    }

    rename_map = {}

    for standard_name, possible_names in aliases.items():
        for column in possible_names:
            if column in df.columns:
                rename_map[column] = standard_name
                break

    df = df.rename(columns=rename_map)

    required_columns = ["case_id", "activity_name", "timestamp"]
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        print("Error: Required columns missing:", missing)
        print("Available columns:", df.columns.tolist())
        return

    # 3. Clean data
    df["timestamp"] = pd.to_datetime(
        df["timestamp"], errors="coerce"
    )

    df = df.dropna(subset=required_columns).copy()

    df["activity_name"] = df["activity_name"].astype(str).str.strip()

    df = df[df["activity_name"] != ""]

    if df.empty:
        print("Error: No valid event records found.")
        return

    # 4. Sort each patient's activities chronologically
    df = df.sort_values(
        ["case_id", "timestamp"],
        kind="stable"
    ).reset_index(drop=True)

    # 5. Find the previous activity for each patient
    df["previous_activity"] = (
        df.groupby("case_id")["activity_name"].shift(1)
    )

    df["previous_timestamp"] = (
        df.groupby("case_id")["timestamp"].shift(1)
    )

    transitions = df.dropna(
        subset=["previous_activity", "previous_timestamp"]
    ).copy()

    # 6. Calculate time between consecutive activities
    transitions["transition_minutes"] = (
        transitions["timestamp"] -
        transitions["previous_timestamp"]
    ).dt.total_seconds() / 60

    transitions = transitions.rename(
        columns={"activity_name": "next_activity"}
    )

    # Keep negative durations out of the analysis
    invalid_count = int(
        (transitions["transition_minutes"] < 0).sum()
    )

    transitions = transitions[
        transitions["transition_minutes"] >= 0
    ].copy()

    # 7. Save individual patient transitions
    output_columns = [
        "case_id",
        "previous_activity",
        "next_activity",
        "previous_timestamp",
        "timestamp",
        "transition_minutes",
    ]

    transitions[output_columns].to_csv(
        TRANSITION_FILE, index=False
    )

    # 8. Summarize each activity-to-activity transition
    if transitions.empty:
        print("No valid consecutive activity transitions found.")
        return

    summary = (
        transitions.groupby(
            ["previous_activity", "next_activity"],
            as_index=False
        )
        .agg(
            patient_transitions=("case_id", "size"),
            unique_patients=("case_id", "nunique"),
            average_wait_minutes=("transition_minutes", "mean"),
            median_wait_minutes=("transition_minutes", "median"),
            maximum_wait_minutes=("transition_minutes", "max"),
        )
    )

    summary = summary.sort_values(
        "average_wait_minutes",
        ascending=False
    )

    summary["average_wait_minutes"] = (
        summary["average_wait_minutes"].round(2)
    )
    summary["median_wait_minutes"] = (
        summary["median_wait_minutes"].round(2)
    )
    summary["maximum_wait_minutes"] = (
        summary["maximum_wait_minutes"].round(2)
    )

    summary.to_csv(SUMMARY_FILE, index=False)

    # 9. Display the results
    print("\nCARE FLOW - WEEK 3 TRANSITION ANALYSIS")
    print("-" * 45)
    print(f"Valid event records: {len(df)}")
    print(f"Patient transitions: {len(transitions)}")
    print(f"Invalid negative transitions excluded: {invalid_count}")

    print("\nTop 10 transitions by average elapsed time:")
    print(summary.head(10).to_string(index=False))

    print(f"\nSaved: {TRANSITION_FILE.name}")
    print(f"Saved: {SUMMARY_FILE.name}")

if __name__ == "__main__":
    main()