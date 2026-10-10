import pandas as pd
import pm4py
from pm4py.visualization.process_tree import visualizer as pt_visualizer

# Load hospital event log
df = pd.read_csv("hospital_event_logs.csv")

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort events by patient and time
df = df.sort_values(["case_id", "timestamp"])

print("Event log loaded successfully!")
print(df.head(10))

# Convert DataFrame to PM4Py event log
event_log = pm4py.format_dataframe(
    df,
    case_id="case_id",
    activity_key="activity_name",
    timestamp_key="timestamp"
)

print("\nPM4Py event log created successfully!")
print("Total events:", len(event_log))

# Discover the process model
process_tree = pm4py.discover_process_tree_inductive(event_log)

print("\nProcess tree discovered successfully!")

gviz = pt_visualizer.apply(process_tree)
pt_visualizer.save(gviz, "process_tree.png")

print("Process tree saved as process_tree.png")

# -----------------------------------------
# WEEK 4 - CONFORMANCE CHECKING
# -----------------------------------------

from pm4py.conformance import conformance_diagnostics_token_based_replay


# Ideal hospital process
ideal_sequence = [
    "Patient Registration",
    "Triage",
    "Doctor Consultation",
    "Lab Test",
    "Lab Result",
    "Treatment",
    "Discharge"
]

# Create ideal process log
ideal_data = []

start_time = pd.Timestamp("2026-01-01 08:00:00")

for i, activity in enumerate(ideal_sequence):
    ideal_data.append({
        "case_id": "IDEAL_CASE",
        "activity_name": activity,
        "timestamp": start_time + pd.Timedelta(minutes=i * 30)
    })

ideal_df = pd.DataFrame(ideal_data)

ideal_log = pm4py.format_dataframe(
    ideal_df,
    case_id="case_id",
    activity_key="activity_name",
    timestamp_key="timestamp"
)

# Create Petri net from ideal process
net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(
    ideal_log
)

print("\nIdeal process model created successfully!")


# Conformance checking
diagnostics = conformance_diagnostics_token_based_replay(
    event_log,
    net,
    initial_marking,
    final_marking
)

print("\nConformance checking completed!")

# Check each patient
conformance_results = []

for i, result in enumerate(diagnostics):

    conformance_results.append({
        "case_id": df["case_id"].drop_duplicates().iloc[i],
        "is_conformant": result["trace_is_fit"],
        "trace_fitness": result["trace_fitness"],
        "missing_tokens": result["missing_tokens"],
        "remaining_tokens": result["remaining_tokens"]
    })

conformance_df = pd.DataFrame(conformance_results)

# Save results
conformance_df.to_csv(
    "conformance_results.csv",
    index=False
)

print("\nConformance results saved as conformance_results.csv")

print("\nConformance Summary:")
print(conformance_df.head(10))