import pandas as pd

# Load hospital event log
df = pd.read_csv("hospital_event_logs.csv")

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort by patient and time
df = df.sort_values(["case_id", "timestamp"])

# Get next activity and next timestamp
df["next_activity"] = df.groupby("case_id")["activity_name"].shift(-1)
df["next_timestamp"] = df.groupby("case_id")["timestamp"].shift(-1)

# Calculate transition time in minutes
df["transition_minutes"] = (
    df["next_timestamp"] - df["timestamp"]
).dt.total_seconds() / 60

# Remove last activity of each patient
df = df.dropna(subset=["next_activity", "transition_minutes"])

# Group transitions
bottleneck = (
    df.groupby(["activity_name", "next_activity"])["transition_minutes"]
    .agg(["count", "mean", "median", "max"])
    .reset_index()
)

# Round values
bottleneck["mean"] = bottleneck["mean"].round(2)
bottleneck["median"] = bottleneck["median"].round(2)
bottleneck["max"] = bottleneck["max"].round(2)

# Sort by average transition time
bottleneck = bottleneck.sort_values("mean", ascending=False)

print("\n" + "=" * 60)
print("CARE FLOW - TRANSITION TIME BOTTLENECK ANALYSIS")
print("=" * 60)

print(bottleneck.to_string(index=False))

# Save result for Power BI
bottleneck.to_csv("bottleneck_analysis.csv", index=False)

print("\nBottleneck analysis completed successfully!")
print("Saved as: bottleneck_analysis.csv")