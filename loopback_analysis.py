
import pandas as pd

# Load hospital event log
df = pd.read_csv("hospital_event_logs.csv")

# Validate required columns
required = ["case_id", "activity_name", "timestamp"]

if not all(col in df.columns for col in required):
    raise ValueError("Required event-log columns are missing.")

# Clean and sort events
df["timestamp"] = pd.to_datetime(
    df["timestamp"], errors="coerce"
)
df = df.dropna(subset=required)
df = df.sort_values(
    ["case_id", "timestamp"]
).reset_index(drop=True)

# Get the next activity for each patient
df["next_activity"] = (
    df.groupby("case_id")["activity_name"].shift(-1)
)

# Detect transitions that return to an activity
# already visited earlier in the same patient's journey
loop_records = []

for case_id, group in df.groupby("case_id", sort=False):
    activities = group["activity_name"].tolist()
    timestamps = group["timestamp"].tolist()
    visited = set()

    for i, activity in enumerate(activities):
        visited.add(activity)

        if i + 1 < len(activities):
            next_activity = activities[i + 1]

            if next_activity in visited:
                loop_records.append({
                    "case_id": case_id,
                    "from_activity": activity,
                    "revisited_activity": next_activity,
                    "timestamp": timestamps[i + 1]
                })

# Save patient-level loop-back details
details_columns = [
    "case_id",
    "from_activity",
    "revisited_activity",
    "timestamp"
]

details = pd.DataFrame(
    loop_records, columns=details_columns
)

details.to_csv("loopback_details.csv", index=False)

# Summarize loop-backs by transition
if not details.empty:
    summary = (
        details.groupby(
            ["from_activity", "revisited_activity"]
        )
        .agg(
            loopback_count=("case_id", "size"),
            unique_patients=("case_id", "nunique")
        )
        .reset_index()
        .sort_values("loopback_count", ascending=False)
    )
else:
    summary = pd.DataFrame(columns=[
        "from_activity",
        "revisited_activity",
        "loopback_count",
        "unique_patients"
    ])

summary.to_csv("loopback_analysis.csv", index=False)

print("\n" + "=" * 60)
print("CARE FLOW - REWORK & LOOP-BACK ANALYSIS")
print("=" * 60)

print("Total patients:", df["case_id"].nunique())
print("Detected loop-back events:", len(details))

if details.empty:
    print("\nNo loop-backs detected in this event log.")
else:
    print("\nLoop-back summary:")
    print(summary.to_string(index=False))

    print("\nPatient-level examples:")
    print(details.head(10).to_string(index=False))

print("\nReports saved:")
print("- loopback_analysis.csv")
print("- loopback_details.csv")
