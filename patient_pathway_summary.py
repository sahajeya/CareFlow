import pandas as pd

# Load hospital event logs
df = pd.read_csv("hospital_event_logs.csv")

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort patient events
df = df.sort_values(["case_id", "timestamp"])

# Calculate patient pathway details
patient_summary = (
    df.groupby("case_id")
    .agg(
        start_time=("timestamp", "min"),
        end_time=("timestamp", "max"),
        total_activities=("activity_name", "count")
    )
    .reset_index()
)

# Calculate pathway duration in minutes
patient_summary["pathway_minutes"] = (
    patient_summary["end_time"]
    - patient_summary["start_time"]
).dt.total_seconds() / 60

# Calculate overall statistics
total_patients = patient_summary["case_id"].nunique()
average_time = patient_summary["pathway_minutes"].mean()
minimum_time = patient_summary["pathway_minutes"].min()
maximum_time = patient_summary["pathway_minutes"].max()

# Find patient with longest pathway
longest_patient = patient_summary.loc[
    patient_summary["pathway_minutes"].idxmax()
]

# Save patient summary
patient_summary.to_csv(
    "patient_pathway_summary.csv",
    index=False
)

# Display results
print("\n========== CAREFLOW PATIENT PATHWAY SUMMARY ==========")

print("\nTotal Patients:", total_patients)
print("Average Pathway Time:", round(average_time, 2), "minutes")
print("Minimum Pathway Time:", round(minimum_time, 2), "minutes")
print("Maximum Pathway Time:", round(maximum_time, 2), "minutes")

print("\nPatient with Longest Pathway:")
print("Patient ID:", longest_patient["case_id"])
print("Total Activities:", longest_patient["total_activities"])
print("Pathway Duration:", longest_patient["pathway_minutes"], "minutes")

print("\nPatient Pathway Summary (First 10 Patients):")
print(patient_summary.head(10).to_string(index=False))

print("\nReport saved as patient_pathway_summary.csv")
print("\n========== ANALYSIS COMPLETED ==========")