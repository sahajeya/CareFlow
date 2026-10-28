import pandas as pd
import matplotlib.pyplot as plt

print("\n========== PATIENT WAITING TIME COMPARISON ==========")

# Load hospital event logs
df = pd.read_csv("hospital_event_logs.csv")

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Calculate patient pathway duration
patient_times = df.groupby("case_id")["timestamp"].agg(
    start_time="min",
    end_time="max"
)

patient_times["total_pathway_minutes"] = (
    patient_times["end_time"] - patient_times["start_time"]
).dt.total_seconds() / 60

# Calculate average duration
average_duration = patient_times["total_pathway_minutes"].mean()

print("\nTotal Patients:", len(patient_times))
print(f"Average Pathway Duration: {average_duration:.2f} minutes")

# Compare each patient with average
patient_times["difference_from_average"] = (
    patient_times["total_pathway_minutes"] - average_duration
)

patient_times["comparison_status"] = patient_times[
    "total_pathway_minutes"
].apply(
    lambda x: "Above Average" if x > average_duration
    else "Below Average" if x < average_duration
    else "Equal to Average"
)

# Count patients
above_average = (
    patient_times["comparison_status"] == "Above Average"
).sum()

below_average = (
    patient_times["comparison_status"] == "Below Average"
).sum()

equal_average = (
    patient_times["comparison_status"] == "Equal to Average"
).sum()

print("\nPatients Above Average:", above_average)
print("Patients Below Average:", below_average)
print("Patients Equal to Average:", equal_average)

# Find top 10 longest pathways
top_10 = patient_times.sort_values(
    "total_pathway_minutes",
    ascending=False
).head(10)

print("\nTop 10 Longest Patient Pathways:")
print(
    top_10[
        ["total_pathway_minutes", "difference_from_average"]
    ].round(2).to_string()
)

# Save comparison report
patient_times.reset_index().to_csv(
    "patient_waiting_comparison.csv",
    index=False
)

print("\nReport saved as patient_waiting_comparison.csv")

# Create visualization
plt.figure(figsize=(12, 6))

plt.bar(
    top_10.index,
    top_10["total_pathway_minutes"],
    color="teal"
)

plt.axhline(
    average_duration,
    color="red",
    linestyle="--",
    label=f"Average: {average_duration:.2f} min"
)

plt.title("Top 10 Longest Patient Pathways")
plt.xlabel("Patient ID")
plt.ylabel("Pathway Duration (Minutes)")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    "patient_waiting_comparison.png",
    dpi=300
)

plt.close()

print("Comparison chart saved as patient_waiting_comparison.png")

print("\n========== COMPARISON COMPLETED ==========")
