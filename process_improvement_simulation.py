
import pandas as pd
from pathlib import Path

INPUT_FILE = Path("bottleneck_analysis.csv")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        "bottleneck_analysis.csv not found. "
        "Run bottleneck_analysis.py first."
    )

df = pd.read_csv(INPUT_FILE)

required = {"activity_name", "next_activity", "count", "mean"}
missing = required - set(df.columns)

if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")

# Select the transition with the highest average elapsed time
df = df.dropna(subset=["activity_name", "next_activity", "mean"])

if df.empty:
    raise ValueError("No valid transition data available.")

target = df.loc[df["mean"].idxmax()]

activity = target["activity_name"]
next_activity = target["next_activity"]
patient_count = int(target["count"])
baseline_mean = float(target["mean"])

# Simulate several hypothetical improvement scenarios
reduction_percentages = [10, 20, 30, 40]

results = []

for reduction in reduction_percentages:
    simulated_mean = baseline_mean * (1 - reduction / 100)
    minutes_saved_per_transition = baseline_mean - simulated_mean

    results.append({
        "from_activity": activity,
        "to_activity": next_activity,
        "transition_count": patient_count,
        "baseline_mean_minutes": round(baseline_mean, 2),
        "assumed_reduction_percent": reduction,
        "simulated_mean_minutes": round(simulated_mean, 2),
        "estimated_minutes_saved_per_transition": round(
            minutes_saved_per_transition, 2
        ),
        "estimated_total_transition_minutes_saved": round(
            minutes_saved_per_transition * patient_count, 2
        ),
    })

result_df = pd.DataFrame(results)
result_df.to_csv("process_improvement_scenarios.csv", index=False)

# Display the simulation
print("\nCARE FLOW - PROCESS IMPROVEMENT SIMULATION")
print("=" * 50)
print(f"Selected transition: {activity} -> {next_activity}")
print(f"Recorded transitions: {patient_count}")
print(f"Baseline mean elapsed time: {baseline_mean:.2f} minutes")

print("\nHypothetical scenarios:")
print(
    result_df[
        [
            "assumed_reduction_percent",
            "simulated_mean_minutes",
            "estimated_minutes_saved_per_transition",
            "estimated_total_transition_minutes_saved",
        ]
    ].to_string(index=False)
)

print("\nReport saved: process_improvement_scenarios.csv")
print(
    "\nNote: These are hypothetical estimates based on transition "
    "averages, not measured real-world improvements."
)
