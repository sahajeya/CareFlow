import pandas as pd
import pm4py

from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.visualization.dfg import visualizer as dfg_visualizer

# Load hospital event log
df = pd.read_csv("hospital_event_logs.csv")

print("\n========== CAREFLOW PROCESS MINING ==========")

print("\nTotal Events:", len(df))
print("Total Patients:", df["case_id"].nunique())

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort events
df = df.sort_values(["case_id", "timestamp"])

# Rename columns for PM4Py
df = df.rename(columns={
    "case_id": "case:concept:name",
    "activity_name": "concept:name",
    "timestamp": "time:timestamp"
})

# Convert to PM4Py event log
event_log = log_converter.apply(
    df,
    variant=log_converter.Variants.TO_EVENT_LOG
)

# Discover process tree
process_tree = inductive_miner.apply(event_log)

print("\nProcess tree discovered successfully!")

# Save process tree visualization
gviz_tree = pt_visualizer.apply(process_tree)

pt_visualizer.save(
    gviz_tree,
    "process_tree.png"
)

print("Process tree saved as process_tree.png")

# Discover Directly-Follows Graph
dfg = pm4py.discover_dfg(event_log)

# Extract frequency information
dfg_frequency = dfg[0]

# Visualize DFG
gviz_dfg = dfg_visualizer.apply(
    dfg_frequency,
    log=event_log,
    variant=dfg_visualizer.Variants.FREQUENCY
)

# Save DFG visualization
dfg_visualizer.save(
    gviz_dfg,
    "patient_activity_flow.png"
)

print("\nDirectly-Follows Graph created successfully!")
print("Patient activity flow saved as patient_activity_flow.png")

# Display activity transitions
print("\nPatient Activity Transitions:")

for (source, target), frequency in sorted(
    dfg_frequency.items(),
    key=lambda item: item[1],
    reverse=True
):
    print(f"{source} -> {target}: {frequency} times")

print("\n========== PROCESS MINING COMPLETED ==========")