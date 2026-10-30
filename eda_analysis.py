
import pandas as pd
from pathlib import Path

# File paths
INPUT_FILE = Path("hospital_event_logs.csv")

# Load dataset
print("\nCARE FLOW - EXPLORATORY DATA ANALYSIS")
print("=" * 50)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

# Check required columns
required_columns = {"case_id", "activity_name", "timestamp"}

if not required_columns.issubset(df.columns):
    raise ValueError("Dataset is missing required columns.")

# Data preprocessing
df["timestamp"] = pd.to_datetime(
    df["timestamp"], errors="coerce"
)

df = df.sort_values(
    ["case_id", "timestamp"]
).reset_index(drop=True)

# 1. Dataset Summary
total_events = len(df)
total_patients = df["case_id"].nunique()
total_activities = df["activity_name"].nunique()

missing_values = int(df.isnull().sum().sum())
duplicate_rows = int(df.duplicated().sum())
invalid_timestamps = int(df["timestamp"].isna().sum())

summary = pd.DataFrame([{
    "total_events": total_events,
    "total_patients": total_patients,
    "total_activities": total_activities,
    "missing_values": missing_values,
    "duplicate_rows": duplicate_rows,
    "invalid_timestamps": invalid_timestamps,
    "start_timestamp": df["timestamp"].min(),
    "end_timestamp": df["timestamp"].max()
}])

summary.to_csv("eda_dataset_summary.csv", index=False)

# 2. Activity Frequency Analysis
activity_frequency = (
    df["activity_name"]
    .value_counts()
    .reset_index()
)

activity_frequency.columns = [
    "activity_name", "event_count"
]

activity_frequency["percentage"] = (
    activity_frequency["event_count"]
    / total_events * 100
).round(2)

activity_frequency.to_csv(
    "eda_activity_frequency.csv", index=False
)

# 3. Patient-wise Activity Summary
patient_summary = (
    df.groupby("case_id")
    .agg(
        total_activities=("activity_name", "count"),
        first_activity_time=("timestamp", "min"),
        last_activity_time=("timestamp", "max")
    )
    .reset_index()
)

patient_summary["journey_duration_minutes"] = (
    patient_summary["last_activity_time"]
    - patient_summary["first_activity_time"]
).dt.total_seconds() / 60

patient_summary.to_csv(
    "eda_patient_summary.csv", index=False
)

# 4. Inter-event Duration Analysis
df["next_timestamp"] = (
    df.groupby("case_id")["timestamp"].shift(-1)
)

df["next_activity"] = (
    df.groupby("case_id")["activity_name"].shift(-1)
)

df["duration_minutes"] = (
    df["next_timestamp"] - df["timestamp"]
).dt.total_seconds() / 60

intervals = df.dropna(
    subset=["next_timestamp", "duration_minutes"]
).copy()

# Keep only valid non-negative durations
intervals = intervals[
    intervals["duration_minutes"] >= 0
]

waiting_summary = (
    intervals.groupby(
        ["activity_name", "next_activity"]
    )["duration_minutes"]
    .agg(
        transition_count="count",
        mean_minutes="mean",
        median_minutes="median",
        max_minutes="max"
    )
    .reset_index()
)

waiting_summary[
    ["mean_minutes", "median_minutes", "max_minutes"]
] = waiting_summary[
    ["mean_minutes", "median_minutes", "max_minutes"]
].round(2)

waiting_summary.to_csv(
    "eda_waiting_time_summary.csv", index=False
)

# 5. Activity Transition Frequency
transition_frequency = (
    intervals.groupby(
        ["activity_name", "next_activity"]
    )
    .size()
    .reset_index(name="transition_count")
    .sort_values("transition_count", ascending=False)
)

transition_frequency.to_csv(
    "eda_transition_frequency.csv", index=False
)

# Display Results
print("\nDATASET SUMMARY")
print(summary.to_string(index=False))

print("\nACTIVITY FREQUENCY")
print(activity_frequency.to_string(index=False))

print("\nPATIENT SUMMARY")
print(patient_summary.head().to_string(index=False))

print("\nTOP 5 ACTIVITY TRANSITIONS")
print(transition_frequency.head().to_string(index=False))

print("\nTOP 5 INTER-EVENT DURATIONS")
print(
    waiting_summary.sort_values(
        "mean_minutes", ascending=False
    ).head().to_string(index=False)
)

print("\nEDA ANALYSIS COMPLETED SUCCESSFULLY")

print("\nGenerated Reports:")
print("- eda_dataset_summary.csv")
print("- eda_activity_frequency.csv")
print("- eda_patient_summary.csv")
print("- eda_waiting_time_summary.csv")
print("- eda_transition_frequency.csv")
