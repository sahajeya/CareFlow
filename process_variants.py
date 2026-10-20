
import pandas as pd
from pathlib import Path

# 1. Load event log
input_file = Path("hospital_event_logs.csv")

if not input_file.exists():
    raise FileNotFoundError("hospital_event_logs.csv not found.")

df = pd.read_csv(input_file)

required_columns = {"case_id", "activity_name", "timestamp"}
missing = required_columns - set(df.columns)

if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")

# 2. Clean and sort events
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["case_id", "activity_name", "timestamp"])
df = df.sort_values(["case_id", "timestamp"])

# 3. Build one pathway per patient
patient_rows = []

for case_id, group in df.groupby("case_id"):
    activities = group["activity_name"].astype(str).tolist()

    patient_rows.append({
        "case_id": case_id,
        "process_variant": " -> ".join(activities),
        "number_of_events": len(activities),
        "start_time": group["timestamp"].min(),
        "end_time": group["timestamp"].max(),
        "journey_duration_minutes": (
            group["timestamp"].max() - group["timestamp"].min()
        ).total_seconds() / 60,
    })

patient_df = pd.DataFrame(patient_rows)

# 4. Count unique pathway variants
total_patients = len(patient_df)

variant_df = (
    patient_df.groupby("process_variant")
    .agg(
        patient_count=("case_id", "count"),
        average_events=("number_of_events", "mean"),
        average_journey_minutes=("journey_duration_minutes", "mean"),
    )
    .reset_index()
)

variant_df["percentage"] = (
    variant_df["patient_count"] / total_patients * 100
).round(2) if total_patients else 0

variant_df["average_events"] = variant_df["average_events"].round(2)
variant_df["average_journey_minutes"] = (
    variant_df["average_journey_minutes"].round(2)
)

# Most common pathway gets rank 1
variant_df = variant_df.sort_values(
    ["patient_count", "process_variant"],
    ascending=[False, True]
).reset_index(drop=True)

variant_df.insert(0, "variant_id", [
    f"V{i:03d}" for i in range(1, len(variant_df) + 1)
])

# 5. Attach variant ID to each patient
patient_df = patient_df.merge(
    variant_df[["variant_id", "process_variant", "patient_count", "percentage"]],
    on="process_variant",
    how="left",
)

patient_df = patient_df.rename(columns={
    "patient_count": "variant_patient_count",
    "percentage": "variant_percentage",
})

# 6. Export reports
variant_df.to_csv("process_variants.csv", index=False)
patient_df.to_csv("patient_process_variants.csv", index=False)

# 7. Display summary
print("\nCARE FLOW - PROCESS VARIANT ANALYSIS")
print("=" * 45)
print("Total patients:", total_patients)
print("Unique process variants:", len(variant_df))

print("\nVariant summary:")
print(
    variant_df[
        ["variant_id", "patient_count", "percentage",
         "average_events", "average_journey_minutes"]
    ].to_string(index=False)
)

print("\nMost common pathway:")
if not variant_df.empty:
    print(variant_df.iloc[0]["process_variant"])
    print(
        f"Followed by {variant_df.iloc[0]['patient_count']} patients "
        f"({variant_df.iloc[0]['percentage']:.2f}%)."
    )

print("\nReports saved:")
print("- process_variants.csv")
print("- patient_process_variants.csv")

