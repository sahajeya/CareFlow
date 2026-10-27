import pandas as pd

# Load hospital event log
df = pd.read_csv("hospital_event_logs.csv")

print("\n========== CAREFLOW EVENT LOG VALIDATION ==========")

print("\nTotal Records:", len(df))

# Check required columns
required_columns = ["case_id", "activity_name", "timestamp"]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# Check missing values
missing_values = df[required_columns].isna().sum()

# Check blank patient IDs and activities
blank_patient_ids = (
    df["case_id"].fillna("").astype(str).str.strip() == ""
).sum()

blank_activities = (
    df["activity_name"].fillna("").astype(str).str.strip() == ""
).sum()

# Check duplicate records
duplicate_records = df.duplicated().sum()

# Check invalid timestamps
converted_timestamps = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

invalid_timestamps = (
    converted_timestamps.isna() & df["timestamp"].notna()
).sum()

# Check activity sequence
expected_sequence = [
    "Patient Registration",
    "Triage",
    "Doctor Consultation",
    "Lab Test",
    "Lab Result",
    "Treatment",
    "Discharge"
]

df["parsed_timestamp"] = converted_timestamps

invalid_sequences = 0

for case_id, group in df.groupby("case_id"):
    activities = (
        group.sort_values("parsed_timestamp")["activity_name"].tolist()
    )

    if activities != expected_sequence:
        invalid_sequences += 1

# Create validation report
validation_report = pd.DataFrame({
    "validation_check": [
        "Missing Patient IDs",
        "Missing Activity Names",
        "Missing Timestamps",
        "Blank Patient IDs",
        "Blank Activity Names",
        "Duplicate Records",
        "Invalid Timestamps",
        "Invalid Patient Activity Sequences"
    ],
    "error_count": [
        missing_values["case_id"],
        missing_values["activity_name"],
        missing_values["timestamp"],
        blank_patient_ids,
        blank_activities,
        duplicate_records,
        invalid_timestamps,
        invalid_sequences
    ]
})

validation_report["status"] = validation_report[
    "error_count"
].apply(lambda x: "PASS" if x == 0 else "FAIL")

# Save report
validation_report.to_csv(
    "event_log_validation_report.csv",
    index=False
)

# Display results
print("\nData Validation Results:")
print(validation_report.to_string(index=False))

print("\nTotal Validation Checks:", len(validation_report))

print(
    "Passed Checks:",
    (validation_report["status"] == "PASS").sum()
)

print(
    "Failed Checks:",
    (validation_report["status"] == "FAIL").sum()
)

print("\nReport saved as event_log_validation_report.csv")

print("\n========== VALIDATION COMPLETED ==========")