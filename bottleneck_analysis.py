import pandas as pd

# Load hospital event log
df = pd.read_csv("hospital_event_logs.csv")

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort events by patient and time
df = df.sort_values(["case_id", "timestamp"])

# Get next activity and next timestamp
df["next_activity"] = df.groupby("case_id")["activity_name"].shift(-1)
df["next_timestamp"] = df.groupby("case_id")["timestamp"].shift(-1)

# Calculate transition time in minutes
df["transition_time_minutes"] = (
    df["next_timestamp"] - df["timestamp"]
).dt.total_seconds() / 60

# Remove final activity of each case
transitions = df.dropna(subset=["next_activity"])

# Calculate bottleneck statistics
bottleneck = (
    transitions
    .groupby(["activity_name", "next_activity"])["transition_time_minutes"]
    .agg(["count", "mean", "median", "max"])
    .reset_index()
)

# Sort by average transition time
bottleneck = bottleneck.sort_values(
    "mean",
    ascending=False
)

# Save results
bottleneck.to_csv("bottleneck_analysis.csv", index=False)

print("\nBottleneck Analysis Results:")
print(bottleneck.to_string(index=False))

print("\nBottleneck analysis saved as bottleneck_analysis.csv")