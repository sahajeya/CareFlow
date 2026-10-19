
import pandas as pd
from pathlib import Path
from collections import Counter

# Input and output files
input_file = Path("conformance_results.csv")

if not input_file.exists():
    raise FileNotFoundError(
        "conformance_results.csv not found. "
        "Run conformance_checking.py first."
    )

df = pd.read_csv(input_file)

required_columns = {"case_id", "status", "deviation_details"}
missing = required_columns - set(df.columns)

if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

# Count patient-level conformance status
status_summary = (
    df["status"]
    .value_counts()
    .rename_axis("status")
    .reset_index(name="patient_count")
)

total_patients = len(df)

status_summary["percentage"] = (
    status_summary["patient_count"] / total_patients * 100
).round(2) if total_patients else 0

status_summary.to_csv("conformance_status_summary.csv", index=False)

# Categorize the detected deviations
deviation_counts = Counter()
deviation_patients = {}

for _, row in df.iterrows():
    if row["status"] != "Deviated":
        continue

    details = str(row["deviation_details"])

    for item in details.split(";"):
        item = item.strip()

        if not item or item == "No deviation":
            continue

        if item.startswith("Missing expected activity:"):
            category = "Missing expected activity"
            activity = item.split(":", 1)[1].strip()

        elif item.startswith("Extra/repeated activity:"):
            category = "Extra/repeated activity"
            activity = item.split(":", 1)[1].strip()

        elif item.startswith("Expected ["):
            category = "Activity sequence difference"
            activity = item

        else:
            category = "Other deviation"
            activity = item

        key = (category, activity)
        deviation_counts[key] += 1
        deviation_patients.setdefault(key, set()).add(row["case_id"])

# Build the deviation summary
summary_rows = []

for (category, activity), count in deviation_counts.items():
    summary_rows.append({
        "deviation_category": category,
        "activity_or_difference": activity,
        "occurrence_count": count,
        "unique_patients": len(deviation_patients[(category, activity)])
    })

summary_columns = [
    "deviation_category",
    "activity_or_difference",
    "occurrence_count",
    "unique_patients",
]

deviation_summary = pd.DataFrame(summary_rows, columns=summary_columns)

if not deviation_summary.empty:
    deviation_summary = deviation_summary.sort_values(
        ["occurrence_count", "unique_patients"],
        ascending=False
    )

deviation_summary.to_csv("deviation_summary.csv", index=False)

# Save detailed deviated patient records
details = df[df["status"] == "Deviated"].copy()
details.to_csv("deviation_details.csv", index=False)

# Display results
print("\nCARE FLOW - DEVIATION SUMMARY ANALYSIS")
print("=" * 45)
print("Total patients:", total_patients)
print("Conforming patients:", (df["status"] == "Conforming").sum())
print("Deviated patients:", (df["status"] == "Deviated").sum())

print("\nDeviation categories:")
if deviation_summary.empty:
    print("No deviations detected.")
else:
    print(deviation_summary.to_string(index=False))

print("\nReports saved:")
print("- conformance_status_summary.csv")
print("- deviation_summary.csv")
print("- deviation_details.csv")
