
import pandas as pd

# Load hospital event log
df = pd.read_csv("hospital_event_logs.csv")

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# Remove invalid records and sort events
df = df.dropna(
    subset=["case_id", "activity_name", "timestamp"]
).sort_values(["case_id", "timestamp"])

# Get next activity and timestamp for each patient
df["next_activity"] = (
    df.groupby("case_id")["activity_name"].shift(-1)
)
df["next_timestamp"] = (
    df.groupby("case_id")["timestamp"].shift(-1)
)

# Calculate elapsed time between consecutive activities
df["transition_minutes"] = (
    df["next_timestamp"] - df["timestamp"]
).dt.total_seconds() / 60

# Keep valid consecutive transitions
df = df.dropna(
    subset=["next_activity", "transition_minutes"]
)
df = df[df["transition_minutes"] >= 0].copy()

# Calculate bottleneck metrics for each transition
bottleneck = (
    df.groupby(["activity_name", "next_activity"])
    ["transition_minutes"]
    .agg(
        count="count",
        mean="mean",
        median="median",
        p90=lambda x: x.quantile(0.90),
        max="max"
    )
    .reset_index()
)

# Round time values
time_columns = ["mean", "median", "p90", "max"]
bottleneck[time_columns] = bottleneck[time_columns].round(2)

# Sort by highest average elapsed time
bottleneck = bottleneck.sort_values(
    "mean", ascending=False
)

# Display report
print("\n" + "=" * 75)
print("CARE FLOW - IMPROVED BOTTLENECK ANALYSIS")
print("=" * 75)
print(bottleneck.to_string(index=False))

# Save complete report for Power BI
bottleneck.to_csv("bottleneck_analysis.csv", index=False)

# Display top 3 transitions by P90
top_delays = bottleneck.sort_values(
    "p90", ascending=False
).head(3)

print("\n" + "=" * 75)
print("TOP 3 TRANSITIONS BY 90TH PERCENTILE TIME")
print("=" * 75)
print(top_delays.to_string(index=False))

print("\nBottleneck analysis completed successfully!")
print("Updated report saved as: bottleneck_analysis.csv")
