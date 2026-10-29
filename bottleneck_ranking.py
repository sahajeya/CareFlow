import pandas as pd
import matplotlib.pyplot as plt

print("\n========== CAREFLOW BOTTLENECK RANKING ==========")

# Load event logs
df = pd.read_csv("hospital_event_logs.csv")

# Convert timestamps
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort patient activities
df = df.sort_values(["case_id", "timestamp"])

# Identify next activity and timestamp
df["next_activity"] = df.groupby("case_id")["activity_name"].shift(-1)
df["next_timestamp"] = df.groupby("case_id")["timestamp"].shift(-1)

# Calculate transition duration
df["waiting_minutes"] = (
    df["next_timestamp"] - df["timestamp"]
).dt.total_seconds() / 60

# Remove last activities
transitions = df.dropna(
    subset=["next_activity", "waiting_minutes"]
).copy()

# Create transition names
transitions["transition"] = (
    transitions["activity_name"]
    + " -> "
    + transitions["next_activity"]
)

# Calculate bottleneck statistics
ranking = transitions.groupby("transition").agg(
    average_minutes=("waiting_minutes", "mean"),
    maximum_minutes=("waiting_minutes", "max"),
    minimum_minutes=("waiting_minutes", "min"),
    patient_count=("case_id", "nunique")
).reset_index()

# Rank transitions
ranking = ranking.sort_values(
    "average_minutes",
    ascending=False
).reset_index(drop=True)

ranking["rank"] = ranking.index + 1

# Calculate percentage contribution
total_average = ranking["average_minutes"].sum()

ranking["contribution_percentage"] = (
    ranking["average_minutes"] / total_average * 100
).round(2)

# Assign relative bottleneck levels
def bottleneck_level(rank):
    if rank <= 2:
        return "High"
    elif rank <= 4:
        return "Medium"
    return "Low"

ranking["bottleneck_level"] = ranking["rank"].apply(
    bottleneck_level
)

# Display results
print("\nBottleneck Ranking Results:")
print(ranking.round(2).to_string(index=False))

# Save CSV report
ranking.to_csv(
    "bottleneck_ranking_report.csv",
    index=False
)

print("\nReport saved as bottleneck_ranking_report.csv")

# Create ranking chart
plt.figure(figsize=(12, 7))

plt.barh(
    ranking["transition"],
    ranking["average_minutes"],
    color="teal"
)

plt.xlabel("Average Transition Duration (Minutes)")
plt.ylabel("Activity Transition")
plt.title("CareFlow - Bottleneck Ranking Analysis")

plt.gca().invert_yaxis()
plt.tight_layout()

plt.savefig(
    "bottleneck_ranking_chart.png",
    dpi=300
)

plt.close()

print("Chart saved as bottleneck_ranking_chart.png")

print("\n========== BOTTLENECK RANKING COMPLETED ==========")