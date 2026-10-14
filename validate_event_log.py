
import pandas as pd

# Load the hospital event log
df = pd.read_csv("hospital_event_logs.csv")

required_columns = ["case_id", "activity_name", "timestamp"]

print("=" * 45)
print("CARE FLOW - EVENT LOG VALIDATION")
print("=" * 45)

# Check required columns
missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    print("Missing required columns:", missing_columns)
    raise SystemExit(1)

# Check missing values
missing_values = int(df[required_columns].isna().sum().sum())

# Check unique patients and events
total_events = len(df)
unique_patients = df["case_id"].nunique()

# Convert timestamps
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

invalid_timestamps = int(df["timestamp"].isna().sum())

# Check duplicate patient-timestamp records
duplicate_timestamps = int(
    df.dropna(subset=["case_id", "timestamp"])
    .duplicated(["case_id", "timestamp"])
    .sum()
)

# Check first and last activities
valid_df = df.dropna(
    subset=["case_id", "activity_name", "timestamp"]
).sort_values(["case_id", "timestamp"])

first_activities = valid_df.groupby("case_id")["activity_name"].first()
last_activities = valid_df.groupby("case_id")["activity_name"].last()

patients_starting_registration = int(
    (first_activities == "Patient Registration").sum()
)

patients_ending_discharge = int(
    (last_activities == "Discharge").sum()
)

# Print results
results = {
    "Total events": total_events,
    "Unique patients": unique_patients,
    "Missing required values": missing_values,
    "Invalid timestamps": invalid_timestamps,
    "Duplicate patient-timestamp rows": duplicate_timestamps,
    "Patients starting with registration": patients_starting_registration,
    "Patients ending with discharge": patients_ending_discharge,
}

for check, value in results.items():
    print(f"{check}: {value}")

# Save validation report
pd.DataFrame(
    list(results.items()),
    columns=["validation_check", "result"]
).to_csv("event_log_validation.csv", index=False)

print("\nReport saved as event_log_validation.csv")
