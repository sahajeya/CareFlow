import pandas as pd

# Load hospital event logs
df = pd.read_csv("hospital_event_logs.csv")

# Convert timestamps
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort patient activities by time
df = df.sort_values(["case_id", "timestamp"])

# Calculate time between consecutive activities
df["time_to_next_activity"] = (
    df.groupby("case_id")["timestamp"]
    .shift(-1) - df["timestamp"]
).dt.total_seconds() / 60

# Calculate total pathway time for each patient
patient_summary = df.groupby("case_id").agg(
    start_time=("timestamp", "min"),
    end_time=("timestamp", "max"),
    total_pathway_minutes=("timestamp", lambda x: 0)
)

patient_summary["total_pathway_minutes"] = (
    patient_summary["end_time"] - patient_summary["start_time"]
).dt.total_seconds() / 60

# Save patient-level results
patient_summary.to_csv("patient_waiting_analysis.csv")

# Find the slowest activity transitions
transition_summary = df.dropna(subset=["time_to_next_activity"]).groupby(
    "activity_name"
)["time_to_next_activity"].agg(
    ["count", "mean", "median", "max"]
).sort_values("mean", ascending=False)

# Display results
print("\nPatient Pathway Time Analysis:")
print(patient_summary.head(10).to_string())

print("\nActivity Waiting Time Analysis:")
print(transition_summary.to_string())

# Save transition results
transition_summary.to_csv("activity_waiting_analysis.csv")

print("\nAnalysis completed successfully!")
print("Saved: patient_waiting_analysis.csv")
print("Saved: activity_waiting_analysis.csv")
