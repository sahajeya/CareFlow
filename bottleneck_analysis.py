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

# Remove final activity of each patient
transitions = df.dropna(
    subset=["next_activity", "transition_time_minutes"]
).copy()

# Calculate bottleneck statistics
bottleneck = (
    transitions
    .groupby(["activity_name", "next_activity"])["transition_time_minutes"]
    .agg(["count", "mean", "median", "max"])
    .reset_index()
)

# Calculate average patient pathway duration
patient_duration = (
    df.groupby("case_id")["timestamp"].max()
    - df.groupby("case_id")["timestamp"].min()
).dt.total_seconds() / 60

average_pathway_time = patient_duration.mean()

# Calculate percentage of average pathway duration
if average_pathway_time > 0:
    bottleneck["bottleneck_percentage"] = (
        bottleneck["mean"] / average_pathway_time
    ) * 100
else:
    bottleneck["bottleneck_percentage"] = 0

# Classify bottleneck severity
# Thresholds are illustrative, not clinical standards
def classify_severity(time):
    if time >= 32:
        return "High"
    elif time >= 30:
        return "Medium"
    else:
        return "Low"

bottleneck["severity"] = bottleneck["mean"].apply(
    classify_severity
)

# Sort bottlenecks by average transition time
bottleneck = bottleneck.sort_values(
    by="mean",
    ascending=False
).reset_index(drop=True)

# Round numerical columns
bottleneck["mean"] = bottleneck["mean"].round(2)
bottleneck["median"] = bottleneck["median"].round(2)
bottleneck["max"] = bottleneck["max"].round(2)

bottleneck["bottleneck_percentage"] = (
    bottleneck["bottleneck_percentage"].round(2)
)

# Save improved bottleneck analysis
bottleneck.to_csv(
    "bottleneck_analysis.csv",
    index=False
)

# Display results
print("\n========== CAREFLOW BOTTLENECK ANALYSIS ==========")

print("\nImproved Bottleneck Analysis Results:")
print(bottleneck.to_string(index=False))

print("\nAverage Patient Pathway Time:",
      round(average_pathway_time, 2), "minutes")

# Display highest bottleneck
if not bottleneck.empty:
    highest = bottleneck.iloc[0]

    print("\nHighest Bottleneck:")
    print("Activity:", highest["activity_name"])
    print("Next Activity:", highest["next_activity"])
    print("Average Time:", highest["mean"], "minutes")
    print("Severity:", highest["severity"])

# Display severity summary
print("\nBottleneck Severity Summary:")
print(bottleneck["severity"].value_counts().to_string())

print("\nImproved bottleneck analysis saved as bottleneck_analysis.csv")

print("\n========== ANALYSIS COMPLETED ==========")